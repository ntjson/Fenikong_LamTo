import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/legacy.dart';
import 'package:lamto_api/lamto_api.dart';

import '../../core/adaptive_buttons.dart';
import '../../core/adaptive_page_route.dart';
import '../../core/error_retry.dart';
import '../../core/format.dart';
import '../../core/load_more_button.dart';
import '../../core/providers.dart';
import '../../l10n/app_localizations.dart';
import '../../theme.dart';
import '../reports/reports_repository.dart' show cursorFromNext;
import '../proposals/proposals_list_screen.dart';
import '../transparency/fund_chart.dart';
import '../transparency/transparency_repository.dart';
import 'evidence_labels.dart';
import 'ledger_detail_screen.dart';

/// Period filter lives outside the controller: Riverpod 3 recreates the
/// notifier whenever the provider rebuilds, so fields stored on it do not
/// survive an invalidation (the selected year silently reset to "all").
final ledgerYearProvider = StateProvider<int?>((_) => null);
final ledgerMonthProvider = StateProvider<int?>((_) => null);

class LedgerListController extends AsyncNotifier<List<LedgerEntryList>> {
  String? _nextCursor;

  bool get hasMore => _nextCursor != null;

  @override
  Future<List<LedgerEntryList>> build() async {
    ref.watch(occupancyScopedProviders);
    final page = await ref
        .read(transparencyRepositoryProvider)
        .listLedger(
          year: ref.watch(ledgerYearProvider),
          month: ref.watch(ledgerMonthProvider),
        );
    _nextCursor = cursorFromNext(page.next);
    return page.results.toList();
  }

  Future<void> loadMore() async {
    final cursor = _nextCursor;
    final current = state.value;
    if (cursor == null || current == null) return;
    final page = await ref
        .read(transparencyRepositoryProvider)
        .listLedger(
          cursor: cursor,
          year: ref.read(ledgerYearProvider),
          month: ref.read(ledgerMonthProvider),
        );
    // A refresh or period change may have replaced the list while this page
    // was in flight; appending onto the stale snapshot would clobber it.
    if (!identical(state.value, current)) return;
    _nextCursor = cursorFromNext(page.next);
    state = AsyncData([...current, ...page.results]);
  }
}

final ledgerListProvider =
    AsyncNotifierProvider<LedgerListController, List<LedgerEntryList>>(
      LedgerListController.new,
    );

final ledgerSegmentProvider = StateProvider<int>((_) => 0);

class _LedgerSegmentControl extends ConsumerWidget {
  const _LedgerSegmentControl();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final selected = ref.watch(ledgerSegmentProvider);
    return SegmentedButton<int>(
      segments: [
        ButtonSegment(value: 0, label: Text(l10n.ledgerSegment)),
        ButtonSegment(value: 1, label: Text(l10n.proposalsSegment)),
      ],
      selected: {selected},
      showSelectedIcon: false,
      onSelectionChanged: (value) =>
          ref.read(ledgerSegmentProvider.notifier).state = value.first,
    );
  }
}

/// Ledger tab (spec 6.3(6)). Body-only: the shell owns chrome.
class LedgerScreen extends ConsumerWidget {
  const LedgerScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final segment = ref.watch(ledgerSegmentProvider);
    if (segment == 1) {
      return const Material(
        color: Colors.transparent,
        child: Column(
          children: [
            Padding(
              padding: EdgeInsets.fromLTRB(16, 16, 16, 0),
              child: SizedBox(
                width: double.infinity,
                child: _LedgerSegmentControl(),
              ),
            ),
            Expanded(child: ProposalsListScreen(showTitle: false)),
          ],
        ),
      );
    }
    final entries = ref.watch(ledgerListProvider);
    final controller = ref.read(ledgerListProvider.notifier);
    final year = ref.watch(ledgerYearProvider);
    final month = ref.watch(ledgerMonthProvider);
    final currentYear = DateTime.now().year;
    final years = [for (var y = currentYear; y >= 2000; y--) y];
    final localeName = Localizations.localeOf(context).toString();

    final header = <Widget>[
      const SizedBox(width: double.infinity, child: _LedgerSegmentControl()),
      const SizedBox(height: 16),
      Text(l10n.ledgerTitle, style: Theme.of(context).textTheme.titleLarge),
      const SizedBox(height: 8),
      Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: DropdownButtonFormField<int?>(
              initialValue: year,
              decoration: InputDecoration(labelText: l10n.ledgerYearLabel),
              items: [
                DropdownMenuItem(value: null, child: Text(l10n.ledgerAllTime)),
                for (final y in years)
                  DropdownMenuItem(value: y, child: Text('$y')),
              ],
              onChanged: (value) {
                // Month is a within-year refinement; a new year resets it.
                ref.read(ledgerYearProvider.notifier).state = value;
                ref.read(ledgerMonthProvider.notifier).state = null;
              },
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: DropdownButtonFormField<int?>(
              initialValue: month,
              decoration: InputDecoration(labelText: l10n.ledgerMonthLabel),
              items: [
                DropdownMenuItem(value: null, child: Text(l10n.ledgerAllTime)),
                for (var m = 1; m <= 12; m++)
                  DropdownMenuItem(
                    value: m,
                    child: Text(formatMonthLabel(m, localeName)),
                  ),
              ],
              onChanged: year == null
                  ? null
                  : (value) =>
                        ref.read(ledgerMonthProvider.notifier).state = value,
            ),
          ),
        ],
      ),
      const SizedBox(height: 8),
      Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            l10n.fundChartTitle,
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          FundChart(range: '12m'),
          const SizedBox(height: 24),
        ],
      ),
    ];

    return Material(
      color: Colors.transparent,
      child: RefreshIndicator.adaptive(
        onRefresh: () async {
          // The error branch below is the retry surface; a failed refresh
          // must not escape as an unhandled zone error.
          ref.invalidate(ledgerListProvider);
          try {
            await ref.read(ledgerListProvider.future);
          } catch (_) {}
        },
        child: switch (entries) {
          // Builder-based so a long paginated history lays out lazily.
          AsyncData(:final value) when value.isNotEmpty => ListView.builder(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(16),
            itemCount:
                header.length + value.length + (controller.hasMore ? 1 : 0),
            itemBuilder: (context, index) {
              if (index < header.length) return header[index];
              final i = index - header.length;
              if (i == value.length) {
                return LoadMoreButton(
                  label: l10n.ledgerLoadMore,
                  onLoadMore: controller.loadMore,
                );
              }
              return _entryTile(context, l10n, value[i]);
            },
          ),
          _ => ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(16),
            children: [
              ...header,
              switch (entries) {
                AsyncData() => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 24),
                  child: Column(
                    children: [
                      Text(l10n.ledgerEmpty),
                      const SizedBox(height: 12),
                      AdaptiveOutlinedButton(
                        onPressed: year == null
                            ? () =>
                                  ref
                                          .read(ledgerSegmentProvider.notifier)
                                          .state =
                                      1
                            : () {
                                ref.read(ledgerYearProvider.notifier).state =
                                    null;
                                ref.read(ledgerMonthProvider.notifier).state =
                                    null;
                              },
                        child: Text(
                          year == null
                              ? l10n.proposalsSegment
                              : l10n.ledgerAllTime,
                        ),
                      ),
                    ],
                  ),
                ),
                AsyncError(:final error) => ErrorRetry(
                  error: error,
                  onRetry: () => ref.invalidate(ledgerListProvider),
                ),
                _ => const Padding(
                  padding: EdgeInsets.symmetric(vertical: 24),
                  child: Center(child: CircularProgressIndicator.adaptive()),
                ),
              },
            ],
          ),
        },
      ),
    );
  }

  Widget _entryTile(
    BuildContext context,
    AppLocalizations l10n,
    LedgerEntryList entry,
  ) => ListTile(
    minTileHeight: 64,
    contentPadding: EdgeInsets.zero,
    // Lead with the story subject; the constant title is only the fallback
    // so a row never renders a bare blank.
    title: Text(
      entry.whatWasFixed.isNotEmpty
          ? entry.whatWasFixed
          : l10n.ledgerDetailTitle,
      maxLines: 2,
      overflow: TextOverflow.ellipsis,
    ),
    subtitle: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          entry.contractorName,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        Text(formatVnd(entry.actualCostVnd), style: listAmountStyle(context)),
        const SizedBox(height: 4),
        EvidenceBadge(level: entry.evidenceLevel),
      ],
    ),
    onTap: () => Navigator.push(
      context,
      adaptivePageRoute(builder: (_) => LedgerDetailScreen(entryId: entry.id)),
    ),
  );
}
