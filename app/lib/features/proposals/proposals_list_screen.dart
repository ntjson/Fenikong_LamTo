import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lamto_api/lamto_api.dart';

import '../../core/adaptive_page_route.dart';
import '../../core/error_retry.dart';
import '../../core/format.dart';
import '../../core/load_more_button.dart';
import '../../core/providers.dart';
import '../../l10n/app_localizations.dart';
import '../../theme.dart';
import '../reports/reports_repository.dart' show cursorFromNext;
import 'proposal_detail_screen.dart';
import 'proposals_repository.dart';

String proposalStatusLabel(String status, AppLocalizations l10n) =>
    switch (status) {
      'PUBLISHED' => l10n.proposalStatusPublished,
      'IN_PROGRESS' => l10n.proposalStatusInProgress,
      'NOT_PROCEEDING' => l10n.proposalStatusNotProceeding,
      'COMPLETED' => l10n.proposalStatusCompleted,
      'CLOSED' => l10n.proposalStatusClosed,
      'DRAFT' => l10n.proposalStatusDraft,
      _ => status,
    };

StatusTone proposalStatusTone(String status) => switch (status) {
  'COMPLETED' || 'CLOSED' => StatusTone.success,
  'NOT_PROCEEDING' => StatusTone.warning,
  _ => StatusTone.info,
};

class ProposalsListController extends AsyncNotifier<List<Proposal>> {
  String? _nextCursor;
  bool get hasMore => _nextCursor != null;

  @override
  Future<List<Proposal>> build() async {
    ref.watch(occupancyScopedProviders);
    final page = await ref.read(proposalsRepositoryProvider).listProposals();
    _nextCursor = cursorFromNext(page.next);
    return page.results.toList();
  }

  Future<void> loadMore() async {
    final cursor = _nextCursor;
    final current = state.value;
    if (cursor == null || current == null) return;
    final page = await ref
        .read(proposalsRepositoryProvider)
        .listProposals(cursor: cursor);
    if (!identical(state.value, current)) return;
    _nextCursor = cursorFromNext(page.next);
    state = AsyncData([...current, ...page.results]);
  }
}

final proposalsListProvider =
    AsyncNotifierProvider<ProposalsListController, List<Proposal>>(
      ProposalsListController.new,
    );

class ProposalsListScreen extends ConsumerWidget {
  const ProposalsListScreen({this.showTitle = true, super.key});

  final bool showTitle;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final proposals = ref.watch(proposalsListProvider);
    final title = showTitle
        ? Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
            child: Text(
              l10n.proposalsSegment,
              style: Theme.of(context).textTheme.titleLarge,
            ),
          )
        : const SizedBox(height: 8);

    return Material(
      color: Colors.transparent,
      child: switch (proposals) {
        AsyncData(:final value) => RefreshIndicator.adaptive(
          onRefresh: () async {
            ref.invalidate(proposalsListProvider);
            try {
              await ref.read(proposalsListProvider.future);
            } catch (_) {}
          },
          // Builder-based so a long paginated history lays out lazily.
          child: ListView.builder(
            physics: const AlwaysScrollableScrollPhysics(),
            itemCount:
                1 +
                value.length +
                (ref.read(proposalsListProvider.notifier).hasMore ? 1 : 0),
            itemBuilder: (context, index) {
              if (index == 0) return title;
              final i = index - 1;
              if (i == value.length) {
                return LoadMoreButton(
                  label: l10n.ledgerLoadMore,
                  onLoadMore: ref.read(proposalsListProvider.notifier).loadMore,
                );
              }
              return _ProposalTile(proposal: value[i]);
            },
          ),
        ),
        AsyncError(:final error) => ListView(
          children: [
            title,
            const SizedBox(height: 48),
            ErrorRetry(
              error: error,
              onRetry: () => ref.invalidate(proposalsListProvider),
            ),
          ],
        ),
        _ => ListView(
          children: [
            title,
            const SizedBox(height: 48),
            const Center(child: CircularProgressIndicator.adaptive()),
          ],
        ),
      },
    );
  }
}

class _ProposalTile extends StatelessWidget {
  const _ProposalTile({required this.proposal});

  final Proposal proposal;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return ListTile(
      minTileHeight: 72,
      title: Align(
        alignment: Alignment.centerLeft,
        child: StatusChip(
          tone: proposalStatusTone(proposal.status),
          label: proposalStatusLabel(proposal.status, l10n),
        ),
      ),
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(proposal.purpose, maxLines: 2, overflow: TextOverflow.ellipsis),
          Text(formatVnd(proposal.amountVnd), style: listAmountStyle(context)),
        ],
      ),
      onTap: () => Navigator.push(
        context,
        adaptivePageRoute(
          builder: (_) => ProposalDetailScreen(proposalId: proposal.id),
        ),
      ),
    );
  }
}
