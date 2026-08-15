import 'package:built_collection/built_collection.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lamto/features/bills/bills_repository.dart';
import 'package:lamto/features/home/home_screen.dart';
import 'package:lamto/features/notifications/notifications_screen.dart';
import 'package:lamto/features/reports/reports_repository.dart';
import 'package:lamto/features/transparency/transparency_repository.dart';
import 'package:lamto/l10n/app_localizations.dart';
import 'package:lamto_api/lamto_api.dart';

NotificationFeed _announcement(int id, String subject, String body) =>
    NotificationFeed(
      (b) => b
        ..id = id
        ..eventCode = 'building.announcement'
        ..eventKey = 'building.announcement:announcement:$id'
        ..subject = subject
        ..body = body
        ..createdAt = DateTime.utc(2026, 7, 20, id),
    );

class _Reports implements ReportsRepository {
  @override
  Future<PaginatedReportSummaryList> listReports({String? cursor}) async =>
      PaginatedReportSummaryList(
        (b) => b..results = ListBuilder<ReportSummary>(),
      );

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class _Repo implements TransparencyRepository {
  final announcements = <NotificationFeed>[
    _announcement(
      2,
      'Mất nước tầng 8',
      'Tạm ngừng cấp nước từ 14:00 đến 16:00.',
    ),
    _announcement(
      1,
      'Bảo trì thang máy',
      'Thang máy B bảo trì vào sáng thứ Bảy.',
    ),
  ];
  final reads = <int>[];
  final queries = <(String?, bool?)>[];

  @override
  Future<PaginatedNotificationFeedList> listNotifications({
    String? cursor,
    String? eventCode,
    bool? unread,
  }) async {
    queries.add((eventCode, unread));
    final results = eventCode == 'building.announcement' && unread == true
        ? announcements.where((item) => !reads.contains(item.id))
        : announcements;
    return PaginatedNotificationFeedList(
      (b) => b..results = ListBuilder<NotificationFeed>(results),
    );
  }

  @override
  Future<void> markNotificationRead(int id) async => reads.add(id);

  @override
  Future<FundSummary> fetchFundSummary() async => FundSummary(
    (b) => b
      ..balanceVnd = 1000000
      ..periodDays = 30
      ..periodInflowsVnd = 0
      ..periodOutflowsVnd = 0,
  );

  @override
  Future<FundSeries> fetchFundSeries({String range = '6m'}) async => FundSeries(
    (b) => b
      ..range = range
      ..points = ListBuilder<FundSeriesPoint>(),
  );

  @override
  Future<PaginatedLedgerEntryListList> listLedger({
    String? cursor,
    int? year,
    int? month,
  }) async => PaginatedLedgerEntryListList(
    (b) => b..results = ListBuilder<LedgerEntryList>(),
  );

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

/// Offline: the mark-read PATCH dies, the announcement must still open.
class _OfflineMarkRepo extends _Repo {
  @override
  Future<void> markNotificationRead(int id) async {
    throw DioException.connectionError(
      requestOptions: RequestOptions(path: '/notifications/$id/read'),
      reason: 'offline',
    );
  }
}

Future<void> _pumpHome(WidgetTester tester, _Repo repo) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        newestUnpaidBillProvider.overrideWith((ref) async => null),
        reportsRepositoryProvider.overrideWithValue(_Reports()),
        transparencyRepositoryProvider.overrideWithValue(repo),
      ],
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: const Locale('vi'),
        home: const Scaffold(body: HomeScreen()),
      ),
    ),
  );
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('newest unread announcement opens then progresses on home', (
    tester,
  ) async {
    final repo = _Repo();
    await _pumpHome(tester, repo);

    expect(repo.queries, contains(('building.announcement', true)));
    expect(find.text('Mất nước tầng 8'), findsOneWidget);
    expect(
      tester.getTopLeft(find.text('Mất nước tầng 8')).dy,
      lessThan(tester.getTopLeft(find.text('1.000.000 ₫')).dy),
    );

    await tester.tap(find.text('Mất nước tầng 8'));
    await tester.pumpAndSettle();

    expect(repo.reads, [2]);
    expect(find.byType(AlertDialog), findsOneWidget);
    expect(find.text('Tạm ngừng cấp nước từ 14:00 đến 16:00.'), findsOneWidget);
    await tester.tap(find.byType(TextButton).last);
    await tester.pumpAndSettle();
    expect(find.text('Mất nước tầng 8'), findsNothing);
    expect(find.text('Bảo trì thang máy'), findsOneWidget);
  });

  testWidgets('bill and announcement peers share one grouped-row pattern', (
    tester,
  ) async {
    final repo = _Repo();
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          newestUnpaidBillProvider.overrideWith(
            (ref) async => BillSummary(
              (b) => b
                ..id = 7
                ..title = 'Phí tháng 7'
                ..amountVnd = 250000
                ..status = BillStatusEnum.ISSUED
                ..period = '2026-07'
                ..issuedAt = DateTime.utc(2026, 7, 1),
            ),
          ),
          reportsRepositoryProvider.overrideWithValue(_Reports()),
          transparencyRepositoryProvider.overrideWithValue(repo),
        ],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('vi'),
          home: const Scaffold(body: HomeScreen()),
        ),
      ),
    );
    await tester.pumpAndSettle();

    // Peer rows read as the same pattern: grouped list rows, no card stack.
    expect(find.byType(Card), findsNothing);
    expect(
      find.ancestor(
        of: find.text('Hóa đơn tòa nhà'),
        matching: find.byType(ListTile),
      ),
      findsOneWidget,
    );
    expect(
      find.ancestor(
        of: find.text('Mất nước tầng 8'),
        matching: find.byType(ListTile),
      ),
      findsOneWidget,
    );
  });

  testWidgets('announcement opens even when mark-read fails offline', (
    tester,
  ) async {
    final repo = _OfflineMarkRepo();
    await _pumpHome(tester, repo);

    await tester.tap(find.text('Mất nước tầng 8'));
    await tester.pumpAndSettle();

    // The dialog opened; the row simply stays unread for a later refresh.
    expect(find.byType(AlertDialog), findsOneWidget);
    expect(find.text('Tạm ngừng cấp nước từ 14:00 đến 16:00.'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('announcement highlight fits compact screens at large text', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(320, 640);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);
    final repo = _Repo();

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          newestUnpaidBillProvider.overrideWith((ref) async => null),
          reportsRepositoryProvider.overrideWithValue(_Reports()),
          transparencyRepositoryProvider.overrideWithValue(repo),
        ],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('vi'),
          home: const MediaQuery(
            data: MediaQueryData(textScaler: TextScaler.linear(2)),
            child: Scaffold(body: HomeScreen()),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Mất nước tầng 8'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets(
    'edited unread delivery resurfaces and absent delivery withdraws',
    (tester) async {
      final repo = _Repo();
      await _pumpHome(tester, repo);
      final container = ProviderScope.containerOf(
        tester.element(find.byType(HomeScreen)),
      );

      repo.reads.add(2);
      repo.announcements[0] = _announcement(
        2,
        'Mất nước tầng 8 - cập nhật',
        'Thời gian mới: 15:00 đến 17:00.',
      );
      repo.reads.remove(2);
      container.invalidate(latestAnnouncementProvider);
      await tester.pumpAndSettle();
      expect(find.text('Mất nước tầng 8 - cập nhật'), findsOneWidget);

      repo.announcements.clear();
      container.invalidate(latestAnnouncementProvider);
      await tester.pumpAndSettle();
      expect(find.text('Mất nước tầng 8 - cập nhật'), findsNothing);
    },
  );
}
