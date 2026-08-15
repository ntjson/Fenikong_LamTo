import 'package:built_collection/built_collection.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lamto/features/reports/my_issues_screen.dart';
import 'package:lamto/features/reports/reports_repository.dart';
import 'package:lamto/l10n/app_localizations.dart';
import 'package:lamto/l10n/app_localizations_en.dart';
import 'package:lamto/theme.dart';
import 'package:lamto_api/lamto_api.dart';

ReportSummary _report(
  int id,
  String text, {
  StatusEnum status = StatusEnum.SUBMITTED,
  bool isPrivate = false,
}) => ReportSummary(
  (b) => b
    ..id = id
    ..text = text
    ..status = status
    ..isPrivate = isPrivate
    ..locationPathSnapshot = 'B / Hall'
    ..createdAt = DateTime.utc(2026, 7, 17),
);

PaginatedReportSummaryList _page(List<ReportSummary> items, {String? next}) =>
    PaginatedReportSummaryList(
      (b) => b
        ..next = next
        ..results = ListBuilder<ReportSummary>(items),
    );

class _FakeRepo implements ReportsRepository {
  _FakeRepo(this.pages);
  final Map<String?, PaginatedReportSummaryList> pages;
  final cursors = <String?>[];
  int detailFetches = 0;

  @override
  Future<PaginatedReportSummaryList> listReports({String? cursor}) async {
    cursors.add(cursor);
    return pages[cursor]!;
  }

  @override
  Future<ReportSummary> createReport({
    required String clientRef,
    required String text,
    required int locationId,
    bool isPrivate = false,
  }) => throw UnimplementedError();
  @override
  Future<List<Location>> fetchLocations() => throw UnimplementedError();
  @override
  Future<ReportDetail> fetchReport(int id) async {
    detailFetches++;
    throw UnimplementedError();
  }

  @override
  Future<CaseRatingResult> rateCase({
    required int caseId,
    required bool satisfied,
    String comment = '',
  }) => throw UnimplementedError();
  @override
  Future<void> replyInfo({required int reportId, required String text}) =>
      throw UnimplementedError();
  @override
  Future<ReportPhoto> uploadPhoto({
    required int reportId,
    required String path,
    required String filename,
  }) => throw UnimplementedError();
}

void main() {
  test('declined reports are terminal without a success presentation', () {
    expect(isActiveReportStatus(StatusEnum.DECLINED), isFalse);
    expect(
      reportStatusLabel(StatusEnum.DECLINED, AppLocalizationsEn()),
      'Not proceeding',
    );
    expect(reportStatusTone(StatusEnum.DECLINED), StatusTone.warning);
  });

  test('all report statuses have plain-language labels and semantic tones', () {
    final l10n = AppLocalizationsEn();
    expect(
      {for (final status in StatusEnum.values) reportStatusLabel(status, l10n)},
      {
        'Submitted',
        'In review',
        'Needs your information',
        'Not proceeding',
        'In progress',
        'Proposal created',
        'Completed',
        'Closed',
      },
    );
    expect(reportStatusTone(StatusEnum.NEEDS_INFO), StatusTone.warning);
    expect(reportStatusTone(StatusEnum.COMPLETED), StatusTone.success);
  });

  testWidgets('shows a private badge on a private report row', (tester) async {
    final repo = _FakeRepo({
      null: _page([_report(1, 'Private issue', isPrivate: true)]),
    });
    await tester.pumpWidget(
      ProviderScope(
        overrides: [reportsRepositoryProvider.overrideWithValue(repo)],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('vi'),
          home: const MyIssuesScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Riêng tư'), findsOneWidget);
    expect(repo.detailFetches, 0);
  });

  testWidgets('lists reports with status chip and loads the next page', (
    tester,
  ) async {
    final repo = _FakeRepo({
      null: _page([
        _report(1, 'Thang máy kêu'),
      ], next: 'http://x/api/v1/reports?cursor=abc'),
      'abc': _page([_report(2, 'Đèn hành lang hỏng')]),
    });
    await tester.pumpWidget(
      ProviderScope(
        overrides: [reportsRepositoryProvider.overrideWithValue(repo)],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('vi'),
          home: const MyIssuesScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Thang máy kêu'), findsOneWidget);
    expect(find.text('Đã gửi'), findsOneWidget); // status paired with text

    await tester.tap(find.text('Tải thêm'));
    await tester.pumpAndSettle();
    expect(find.text('Đèn hành lang hỏng'), findsOneWidget);
    expect(repo.cursors, [null, 'abc']);
    expect(find.text('Tải thêm'), findsNothing); // no further page
  });

  testWidgets('empty state', (tester) async {
    final repo = _FakeRepo({null: _page([])});
    await tester.pumpWidget(
      ProviderScope(
        overrides: [reportsRepositoryProvider.overrideWithValue(repo)],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('vi'),
          home: const MyIssuesScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Bạn chưa gửi phản ánh nào.'), findsOneWidget);
  });
}
