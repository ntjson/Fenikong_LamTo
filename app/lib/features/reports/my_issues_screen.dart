import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lamto_api/lamto_api.dart';

import '../../core/adaptive_buttons.dart';
import '../../core/adaptive_page_route.dart';
import '../../core/error_retry.dart';
import '../../core/load_more_button.dart';
import '../../core/providers.dart';
import '../../l10n/app_localizations.dart';
import '../../theme.dart';
import '../auth/session_controller.dart';
import 'issue_detail_screen.dart';
import 'report_form_screen.dart';
import 'reports_repository.dart';

/// Plain-language status labels (DESIGN.md: color never alone).
String reportStatusLabel(StatusEnum status, AppLocalizations l10n) =>
    switch (status) {
      StatusEnum.SUBMITTED => l10n.statusSubmitted,
      StatusEnum.IN_REVIEW => l10n.statusInReview,
      StatusEnum.NEEDS_INFO => l10n.statusNeedsInfo,
      StatusEnum.DECLINED => l10n.statusDeclined,
      StatusEnum.IN_PROGRESS => l10n.statusInProgress,
      StatusEnum.PROPOSED => l10n.statusProposed,
      StatusEnum.COMPLETED => l10n.statusCompleted,
      StatusEnum.CLOSED => l10n.statusClosed,
      _ => status.name,
    };

bool isActiveReportStatus(StatusEnum status) =>
    status != StatusEnum.DECLINED &&
    status != StatusEnum.COMPLETED &&
    status != StatusEnum.CLOSED;

StatusTone reportStatusTone(StatusEnum status) => switch (status) {
  StatusEnum.COMPLETED || StatusEnum.CLOSED => StatusTone.success,
  StatusEnum.DECLINED || StatusEnum.NEEDS_INFO => StatusTone.warning,
  _ => StatusTone.info,
};

/// Cursor-paginated list of **all** reports submitted by the authenticated
/// user across units (user-global; amendment 12). Not filtered to the
/// selected occupancy. Rebuilds when session identity changes so a later
/// sign-in cannot show the previous user's cached list.
class MyReportsController extends AsyncNotifier<List<ReportSummary>> {
  String? _nextCursor;
  bool get hasMore => _nextCursor != null;

  @override
  Future<List<ReportSummary>> build() async {
    // Session identity: drop cross-user cache on logout / re-login.
    ref.watch(sessionControllerProvider);
    ref.watch(occupancyScopedProviders);
    final page = await ref.read(reportsRepositoryProvider).listReports();
    _nextCursor = cursorFromNext(page.next);
    return page.results.toList();
  }

  Future<void> loadMore() async {
    final cursor = _nextCursor;
    final current = state.value;
    if (cursor == null || current == null) return;
    final page = await ref
        .read(reportsRepositoryProvider)
        .listReports(cursor: cursor);
    // A refresh may have replaced the list while this page was in flight;
    // appending onto the stale snapshot would clobber the fresh state.
    if (!identical(state.value, current)) return;
    _nextCursor = cursorFromNext(page.next);
    state = AsyncData([...current, ...page.results]);
  }
}

final myReportsProvider =
    AsyncNotifierProvider<MyReportsController, List<ReportSummary>>(
      MyReportsController.new,
    );

/// Issues tab body: user-global "My issues" / "Việc của tôi" list with
/// semantic status chips, pull-to-refresh, and load-more (spec §6.3(5)).
///
/// Scope is **user-global** (amendment 12): every report the authenticated
/// resident submitted, across all units — not limited to the currently
/// selected occupancy.
class MyIssuesScreen extends ConsumerWidget {
  const MyIssuesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final reports = ref.watch(myReportsProvider);
    // Body-only: shell owns Scaffold/CupertinoPageScaffold chrome (no nested
    // AppBar). Material provides ListTile ink without a second scaffold.
    final title = Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
      child: Text(
        l10n.issuesTitle,
        style: Theme.of(context).textTheme.titleLarge,
      ),
    );
    final body = switch (reports) {
      AsyncData(:final value) => RefreshIndicator.adaptive(
        onRefresh: () async {
          // The error branch below is the retry surface; a failed refresh
          // must not escape as an unhandled zone error.
          ref.invalidate(myReportsProvider);
          try {
            await ref.read(myReportsProvider.future);
          } catch (_) {}
        },
        child: value.isEmpty
            ? ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                children: [
                  title,
                  const SizedBox(height: 120),
                  Center(
                    child: Column(
                      children: [
                        Text(l10n.issuesEmpty),
                        const SizedBox(height: 12),
                        AdaptiveFilledButton(
                          onPressed: () => openReportForm(context),
                          child: Text(l10n.tabReport),
                        ),
                      ],
                    ),
                  ),
                ],
              )
            // Builder-based so a long paginated history lays out lazily.
            : ListView.builder(
                physics: const AlwaysScrollableScrollPhysics(),
                itemCount:
                    1 +
                    value.length +
                    (ref.read(myReportsProvider.notifier).hasMore ? 1 : 0),
                itemBuilder: (context, index) {
                  if (index == 0) return title;
                  final i = index - 1;
                  if (i == value.length) {
                    return LoadMoreButton(
                      label: l10n.issuesLoadMore,
                      onLoadMore: ref.read(myReportsProvider.notifier).loadMore,
                    );
                  }
                  return _ReportTile(report: value[i]);
                },
              ),
      ),
      AsyncError(:final error) => ListView(
        children: [
          title,
          const SizedBox(height: 48),
          ErrorRetry(
            error: error,
            onRetry: () => ref.invalidate(myReportsProvider),
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
    };
    return Material(
      color: Theme.of(context).scaffoldBackgroundColor,
      child: body,
    );
  }
}

class _ReportTile extends StatelessWidget {
  const _ReportTile({required this.report});

  final ReportSummary report;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return ListTile(
      minTileHeight: 64,
      title: Align(
        alignment: Alignment.centerLeft,
        child: StatusChip(
          tone: reportStatusTone(report.status),
          label: reportStatusLabel(report.status, l10n),
        ),
      ),
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(report.text, maxLines: 2, overflow: TextOverflow.ellipsis),
          Text(
            report.locationPathSnapshot,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          if (report.isPrivate) Text(l10n.privateBadge),
        ],
      ),
      onTap: () => Navigator.push(
        context,
        adaptivePageRoute(
          builder: (_) => IssueDetailScreen(reportId: report.id),
        ),
      ),
    );
  }
}
