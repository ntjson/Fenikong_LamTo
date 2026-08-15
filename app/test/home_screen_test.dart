import 'dart:async';

import 'package:built_collection/built_collection.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lamto/core/error_retry.dart';
import 'package:lamto/core/format.dart';
import 'package:lamto/features/bills/bills_screen.dart';
import 'package:lamto/features/bills/bills_repository.dart';
import 'package:lamto/features/home/home_screen.dart';
import 'package:lamto/features/ledger/ledger_screen.dart';
import 'package:lamto/features/notifications/notifications_screen.dart';
import 'package:lamto/features/reports/reports_repository.dart';
import 'package:lamto/features/shell/home_shell.dart';
import 'package:lamto/features/transparency/fund_chart.dart';
import 'package:lamto/features/transparency/transparency_repository.dart';
import 'package:lamto/l10n/app_localizations.dart';
import 'package:lamto_api/lamto_api.dart';

FundSummary _fund() => FundSummary(
  (b) => b
    ..balanceVnd = 1500000
    ..periodDays = 30
    ..periodInflowsVnd = 200000
    ..periodOutflowsVnd = 50000,
);

FundSeries _series(String range) => FundSeries(
  (b) => b
    ..range = range
    ..points = ListBuilder<FundSeriesPoint>([
      for (var i = 0; i < 6; i++)
        FundSeriesPoint(
          (p) => p
            ..periodStart = DateTime.utc(2026, 2 + i, 1)
            ..inflowsVnd = i == 2 ? 200000 : 0
            ..outflowsVnd = i == 4 ? -50000 : 0
            ..balanceVnd = 1500000 + i * 10000,
        ),
    ]),
);

LedgerEntryList _entry(int id) => LedgerEntryList(
  (b) => b
    ..id = id
    ..contractorName = 'Acme Co'
    ..actualCostVnd = 900000
    ..publishedAt = DateTime.utc(2026, 7, 10)
    ..integrityStatus = 'VERIFIED'
    ..evidenceLevel = 'CHAIN_CONFIRMED'
    ..whatWasFixed = 'Sửa máy bơm nước',
);

ReportSummary _report(String text, StatusEnum status) => ReportSummary(
  (b) => b
    ..id = 1
    ..text = text
    ..status = status
    ..isPrivate = false
    ..locationPathSnapshot = 'B / Hall'
    ..createdAt = DateTime.utc(2026, 7, 9),
);

BillSummary _bill() => BillSummary(
  (builder) => builder
    ..id = 7
    ..title = 'July bill'
    ..amountVnd = 250000
    ..status = BillStatusEnum.ISSUED
    ..period = '2026-07'
    ..issuedAt = DateTime.utc(2026, 7, 1),
);

class _FakeReports implements ReportsRepository {
  @override
  Future<PaginatedReportSummaryList> listReports({String? cursor}) async =>
      PaginatedReportSummaryList(
        (b) => b
          ..results = ListBuilder<ReportSummary>([
            _report('Thang máy kêu', StatusEnum.SUBMITTED),
            _report('Đèn hỏng', StatusEnum.COMPLETED),
          ]),
      );

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

/// Reports list throws; used to assert home active-reports error copy.
class _ThrowingReports implements ReportsRepository {
  @override
  Future<PaginatedReportSummaryList> listReports({String? cursor}) async {
    throw Exception('boom');
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class _PendingReports implements ReportsRepository {
  final pending = Completer<PaginatedReportSummaryList>();

  @override
  Future<PaginatedReportSummaryList> listReports({String? cursor}) =>
      pending.future;

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class _FakeTransparency implements TransparencyRepository {
  @override
  Future<FundSummary> fetchFundSummary() async => _fund();

  @override
  Future<FundSeries> fetchFundSeries({String range = '6m'}) async =>
      _series(range);

  @override
  Future<PaginatedLedgerEntryListList> listLedger({
    String? cursor,
    int? year,
    int? month,
  }) async => PaginatedLedgerEntryListList(
    (b) => b..results = ListBuilder<LedgerEntryList>([_entry(1)]),
  );

  @override
  Future<PaginatedNotificationFeedList> listNotifications({
    String? cursor,
    String? eventCode,
    bool? unread,
  }) async => PaginatedNotificationFeedList(
    (builder) => builder.results = ListBuilder<NotificationFeed>(),
  );

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

NotificationFeed _notice(int id, {DateTime? readAt}) => NotificationFeed(
  (b) => b
    ..id = id
    ..eventCode = 'ledger.publication'
    ..eventKey = 'ledger.publication:entry:$id'
    ..subject = 'Khoản chi $id'
    ..body = 'Một khoản chi vừa được công bố.'
    ..createdAt = DateTime.utc(2026, 7, 15)
    ..readAt = readAt,
);

/// Two unread + one read in the general feed; no unread announcements.
class _UnreadTransparency extends _FakeTransparency {
  @override
  Future<PaginatedNotificationFeedList> listNotifications({
    String? cursor,
    String? eventCode,
    bool? unread,
  }) async => PaginatedNotificationFeedList(
    (b) => b
      ..results = ListBuilder<NotificationFeed>(
        eventCode == null
            ? [
                _notice(1),
                _notice(2),
                _notice(3, readAt: DateTime.utc(2026, 7, 16)),
              ]
            : const <NotificationFeed>[],
      ),
  );
}

class _ThrowingSeriesTransparency extends _FakeTransparency {
  @override
  Future<FundSeries> fetchFundSeries({String range = '6m'}) async {
    throw Exception('series down');
  }
}

class _PendingSeriesTransparency extends _FakeTransparency {
  final series = Completer<FundSeries>();

  @override
  Future<FundSeries> fetchFundSeries({String range = '6m'}) => series.future;
}

class _PendingTransparency implements TransparencyRepository {
  final fund = Completer<FundSummary>();
  final series = Completer<FundSeries>();
  final ledger = Completer<PaginatedLedgerEntryListList>();

  @override
  Future<FundSummary> fetchFundSummary() => fund.future;

  @override
  Future<FundSeries> fetchFundSeries({String range = '6m'}) => series.future;

  @override
  Future<PaginatedLedgerEntryListList> listLedger({
    String? cursor,
    int? year,
    int? month,
  }) => ledger.future;

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

Future<void> _pumpShell(WidgetTester tester) async {
  tester.view.physicalSize = const Size(400, 800);
  tester.view.devicePixelRatio = 1;
  addTearDown(tester.view.reset);
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        newestUnpaidBillProvider.overrideWith((ref) async => null),
        reportsRepositoryProvider.overrideWithValue(_FakeReports()),
        transparencyRepositoryProvider.overrideWithValue(_FakeTransparency()),
      ],
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: const Locale('vi'),
        home: const HomeShell(),
      ),
    ),
  );
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('Home bills action opens the empty bills list', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          newestUnpaidBillProvider.overrideWith((ref) async => null),
          billsProvider.overrideWith((ref) async => []),
          reportsRepositoryProvider.overrideWithValue(_FakeReports()),
          transparencyRepositoryProvider.overrideWithValue(_FakeTransparency()),
        ],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: const Scaffold(body: HomeScreen()),
        ),
      ),
    );
    await tester.pumpAndSettle();

    // The entry is a labeled row, not icon-only chrome behind a tooltip.
    await tester.tap(find.text('Bills'));
    await tester.pumpAndSettle();

    expect(find.byType(BillsScreen), findsOneWidget);
    expect(find.text('No bills.'), findsOneWidget);
  });

  testWidgets('Home notifications row is labeled and opens the list', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          newestUnpaidBillProvider.overrideWith((ref) async => null),
          reportsRepositoryProvider.overrideWithValue(_FakeReports()),
          transparencyRepositoryProvider.overrideWithValue(_FakeTransparency()),
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

    await tester.tap(find.text('Thông báo'));
    await tester.pumpAndSettle();

    expect(find.byType(NotificationsScreen), findsOneWidget);
  });

  testWidgets('Home notifications row carries an announced unread badge', (
    tester,
  ) async {
    final semantics = tester.ensureSemantics();
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          newestUnpaidBillProvider.overrideWith((ref) async => null),
          reportsRepositoryProvider.overrideWithValue(_FakeReports()),
          transparencyRepositoryProvider.overrideWithValue(
            _UnreadTransparency(),
          ),
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

    // Count-bearing badge on the row, announced for screen readers.
    expect(find.byType(Badge), findsOneWidget);
    expect(find.text('2'), findsOneWidget);
    // The tile merges descendant semantics; match within the row's label.
    expect(
      find.bySemanticsLabel(RegExp('2 thông báo chưa đọc')),
      findsOneWidget,
    );
    semantics.dispose();
  });

  testWidgets('Home shows the newest unpaid bill', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          newestUnpaidBillProvider.overrideWith((ref) async => _bill()),
          reportsRepositoryProvider.overrideWithValue(_FakeReports()),
          transparencyRepositoryProvider.overrideWithValue(_FakeTransparency()),
        ],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: const Scaffold(body: HomeScreen()),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Building bill'), findsOneWidget);
    expect(find.textContaining('250.000 ₫'), findsOneWidget);
  });

  testWidgets('Home names bill loading', (tester) async {
    final pending = Completer<BillSummary?>();
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          newestUnpaidBillProvider.overrideWith((ref) => pending.future),
          reportsRepositoryProvider.overrideWithValue(_FakeReports()),
          transparencyRepositoryProvider.overrideWithValue(_FakeTransparency()),
        ],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: const Scaffold(body: HomeScreen()),
        ),
      ),
    );
    await tester.pump();

    expect(find.text('Loading building bill…'), findsOneWidget);
  });

  testWidgets('Home refresh exposes a newest bill failure', (tester) async {
    var calls = 0;
    await tester.pumpWidget(
      ProviderScope(
        retry: (_, _) => null,
        overrides: [
          newestUnpaidBillProvider.overrideWith((ref) async {
            if (calls++ == 0) return _bill();
            throw Exception('bill failed');
          }),
          reportsRepositoryProvider.overrideWithValue(_FakeReports()),
          transparencyRepositoryProvider.overrideWithValue(_FakeTransparency()),
        ],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: const Scaffold(body: HomeScreen()),
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.drag(find.byType(ListView).first, const Offset(0, 300));
    await tester.pumpAndSettle();

    expect(find.byType(ErrorRetry), findsOneWidget);
  });

  testWidgets('home renders fund chart card', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          newestUnpaidBillProvider.overrideWith((ref) async => null),
          reportsRepositoryProvider.overrideWithValue(_FakeReports()),
          transparencyRepositoryProvider.overrideWithValue(_FakeTransparency()),
        ],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: const Scaffold(body: HomeScreen()),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byType(FundChart), findsOneWidget);
    expect(find.byType(LineChart), findsOneWidget);
  });

  testWidgets('series loading keeps a named chart placeholder', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          newestUnpaidBillProvider.overrideWith((ref) async => null),
          reportsRepositoryProvider.overrideWithValue(_FakeReports()),
          transparencyRepositoryProvider.overrideWithValue(
            _PendingSeriesTransparency(),
          ),
        ],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: const Scaffold(body: HomeScreen()),
        ),
      ),
    );
    await tester.pump();

    expect(find.byType(FundChart), findsOneWidget);
    expect(find.byType(CircularProgressIndicator), findsWidgets);
  });

  testWidgets('series failure shows retry but keeps balance', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        retry: (_, _) => null,
        overrides: [
          newestUnpaidBillProvider.overrideWith((ref) async => null),
          reportsRepositoryProvider.overrideWithValue(_FakeReports()),
          transparencyRepositoryProvider.overrideWithValue(
            _ThrowingSeriesTransparency(),
          ),
        ],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: const Scaffold(body: HomeScreen()),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text(formatVnd(1500000)), findsOneWidget);
    expect(find.byType(ErrorRetry), findsWidgets);
    expect(find.byType(LineChart), findsNothing);
  });

  testWidgets('Android Home chart opens the shell Ledger tab', (tester) async {
    final previous = debugDefaultTargetPlatformOverride;
    debugDefaultTargetPlatformOverride = TargetPlatform.android;
    try {
      await _pumpShell(tester);
      expect(
        tester.widget<NavigationBar>(find.byType(NavigationBar)).destinations,
        hasLength(4),
      );
      await tester.tap(find.byType(FundChart));
      await tester.pumpAndSettle();

      expect(
        tester.widget<NavigationBar>(find.byType(NavigationBar)).selectedIndex,
        ledgerTabIndex,
      );
      expect(find.byType(LedgerScreen), findsOneWidget);
    } finally {
      debugDefaultTargetPlatformOverride = previous;
    }
  });

  testWidgets('Ledger navigation resets a previous Proposals segment', (
    tester,
  ) async {
    final previous = debugDefaultTargetPlatformOverride;
    debugDefaultTargetPlatformOverride = TargetPlatform.android;
    try {
      await _pumpShell(tester);
      final container = ProviderScope.containerOf(
        tester.element(find.byType(HomeShell)),
      );
      container.read(ledgerSegmentProvider.notifier).state = 1;
      container.read(shellTabProvider.notifier).state = ledgerTabIndex;
      await tester.pump();
      expect(container.read(ledgerSegmentProvider), 1);

      await tester.tap(find.text('Trang chính').last);
      await tester.pumpAndSettle();
      await tester.tap(find.byType(FundChart));
      await tester.pumpAndSettle();

      expect(container.read(ledgerSegmentProvider), 0);
      expect(find.byType(LedgerScreen), findsOneWidget);
    } finally {
      debugDefaultTargetPlatformOverride = previous;
    }
  });

  testWidgets('iOS Home chart opens the shell Ledger tab', (tester) async {
    final previous = debugDefaultTargetPlatformOverride;
    debugDefaultTargetPlatformOverride = TargetPlatform.iOS;
    try {
      await _pumpShell(tester);
      final controller = tester
          .widget<CupertinoTabScaffold>(find.byType(CupertinoTabScaffold))
          .controller!;

      await tester.tap(find.byType(FundChart));
      await tester.pumpAndSettle();

      expect(controller.index, ledgerTabIndex);
      expect(find.byType(LedgerScreen), findsOneWidget);
    } finally {
      debugDefaultTargetPlatformOverride = previous;
    }
  });

  testWidgets('home shows fund block, open reports only, recent spending', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          newestUnpaidBillProvider.overrideWith((ref) async => null),
          reportsRepositoryProvider.overrideWithValue(_FakeReports()),
          transparencyRepositoryProvider.overrideWithValue(_FakeTransparency()),
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

    expect(find.text('Quỹ bảo trì'), findsOneWidget);
    expect(find.text('1.500.000 ₫'), findsOneWidget); // tabular integer VND
    // 30-day stats and 6-month chart each state their window (item G).
    expect(find.textContaining('Thu (30 ngày)'), findsOneWidget);
    expect(find.text('Số dư quỹ · 6 tháng gần nhất'), findsOneWidget);
    // Below-the-fold sections still render; search offstage rows too.
    expect(
      find.text('Thang máy kêu', skipOffstage: false),
      findsOneWidget,
    ); // OPEN shown
    expect(
      find.text('Đèn hỏng', skipOffstage: false),
      findsNothing,
    ); // RESOLVED filtered out
    expect(
      find.text('Acme Co', skipOffstage: false),
      findsOneWidget,
    ); // recent spending row
    expect(
      find.text('Sửa máy bơm nước', skipOffstage: false),
      findsOneWidget,
    ); // spending subject leads the row
    // Bills/Notifications are visibly labeled rows outside the fund heading.
    expect(find.text('Hóa đơn'), findsOneWidget);
    expect(find.text('Thông báo'), findsOneWidget);
    expect(find.byIcon(Icons.notifications_outlined), findsOneWidget);
  });

  testWidgets(
    'home active-reports AsyncError shows resident failure copy, not empty',
    (tester) async {
      // Riverpod 3 auto-retries Exceptions; disable so AsyncError surfaces
      // immediately (production still retries then settles on AsyncError).
      await tester.pumpWidget(
        ProviderScope(
          retry: (_, _) => null,
          overrides: [
            newestUnpaidBillProvider.overrideWith((ref) async => null),
            reportsRepositoryProvider.overrideWithValue(_ThrowingReports()),
            transparencyRepositoryProvider.overrideWithValue(
              _FakeTransparency(),
            ),
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

      // Fund / spending still succeed.
      expect(find.text('Quỹ bảo trì'), findsOneWidget);
      expect(find.text('1.500.000 ₫'), findsOneWidget);
      expect(find.text('Acme Co', skipOffstage: false), findsOneWidget);

      // Active-reports section header + resident-facing errServer (generic throw
      // → Failure.fromObject → server_error), not a silent empty list.
      expect(
        find.text('Phản ánh đang mở', skipOffstage: false),
        findsOneWidget,
      );
      expect(
        find.text(
          'Đã có lỗi từ phía hệ thống. Thao tác có thể chưa được lưu. Vui lòng thử lại sau.',
          skipOffstage: false,
        ),
        findsOneWidget,
      );
    },
  );

  testWidgets('home names section loading states instead of leaving blanks', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          newestUnpaidBillProvider.overrideWith((ref) async => null),
          reportsRepositoryProvider.overrideWithValue(_PendingReports()),
          transparencyRepositoryProvider.overrideWithValue(
            _PendingTransparency(),
          ),
        ],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('vi'),
          home: const Scaffold(body: HomeScreen()),
        ),
      ),
    );
    await tester.pump();

    expect(find.text('Đang tải phản ánh…'), findsOneWidget);
    expect(find.text('Đang tải khoản chi…'), findsOneWidget);
  });

  testWidgets('fund period stats stack at large text sizes', (tester) async {
    tester.view.physicalSize = const Size(320, 640);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          newestUnpaidBillProvider.overrideWith((ref) async => null),
          reportsRepositoryProvider.overrideWithValue(_FakeReports()),
          transparencyRepositoryProvider.overrideWithValue(_FakeTransparency()),
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

    expect(find.byKey(const Key('fund-period-stats-stacked')), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
