import 'dart:async';

import 'package:built_collection/built_collection.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lamto/app.dart';
import 'package:lamto/core/providers.dart';
import 'package:lamto/core/token_store.dart';
import 'package:lamto/features/auth/auth_repository.dart';
import 'package:lamto/features/bills/bill_detail_screen.dart';
import 'package:lamto/features/bills/bills_repository.dart';
import 'package:lamto/features/ledger/ledger_detail_screen.dart';
import 'package:lamto/features/ledger/ledger_screen.dart';
import 'package:lamto/features/notifications/notifications_screen.dart';
import 'package:lamto/features/push/push_token_source.dart';
import 'package:lamto/features/reports/issue_detail_screen.dart';
import 'package:lamto/features/reports/reports_repository.dart';
import 'package:lamto/features/shell/home_shell.dart';
import 'package:lamto/features/transparency/transparency_repository.dart';
import 'package:lamto_api/lamto_api.dart';
import 'package:shared_preferences/shared_preferences.dart';

class _FakeStore implements TokenStore {
  _FakeStore([this.token]);
  String? token;
  @override
  Future<void> clear() async => token = null;
  @override
  Future<String?> read() async => token;
  @override
  Future<void> write(String value) async => token = value;
}

class _AuthRepo implements AuthRepository {
  _AuthRepo(this._me);
  final Me _me;
  @override
  Future<String> login(String i, String p) async => 'tok';
  @override
  Future<Me> fetchMe() async => _me;
  @override
  Future<void> logout() async {}
  @override
  Future<void> logoutAll() async {}
}

/// Controllable push source for AppRouter cold-start / open stream.
class _ControllablePushSource implements PushTokenSource {
  Map<String, String>? initial;
  final _opened = StreamController<Map<String, String>>.broadcast();

  void emitOpened(Map<String, String> data) => _opened.add(data);

  @override
  Future<PushPermissionResult> requestPermission() async =>
      PushPermissionResult.unsupported;
  @override
  Future<String?> getToken() async => null;
  @override
  Stream<String> get onTokenRefresh => const Stream.empty();
  @override
  Future<Map<String, String>?> initialMessageData() async => initial;
  @override
  Stream<Map<String, String>> get onMessageOpened => _opened.stream;
}

class _EmptyReports implements ReportsRepository {
  @override
  Future<PaginatedReportSummaryList> listReports({String? cursor}) async =>
      PaginatedReportSummaryList(
        (b) => b..results = ListBuilder<ReportSummary>(),
      );

  @override
  Future<ReportDetail> fetchReport(int id) async => ReportDetail(
    (b) => b
      ..id = id
      ..text = 'report $id'
      ..status = StatusEnum.SUBMITTED
      ..locationPathSnapshot = 'B'
      ..unitLabel = 'A-1'
      ..createdAt = DateTime.utc(2026, 7, 1)
      ..photos = ListBuilder<ReportPhoto>()
      ..cases = ListBuilder(),
  );

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class _EmptyTransparency implements TransparencyRepository {
  @override
  Future<FundSummary> fetchFundSummary() async => FundSummary(
    (b) => b
      ..balanceVnd = 0
      ..periodDays = 30
      ..periodInflowsVnd = 0
      ..periodOutflowsVnd = 0,
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
  Future<LedgerEntryDetail> fetchLedgerEntry(int id) async {
    throw Exception('not needed');
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

Me _me() => Me(
  (b) => b
    ..displayName = 'R'
    ..email = 'r@example.com'
    ..phone = null
    ..occupancies = ListBuilder<Occupancy>([
      Occupancy(
        (o) => o
          ..id = 1
          ..unitLabel = 'A-1'
          ..buildingName = 'Toa A',
      ),
    ])
    ..notificationPreferences = ListBuilder<NotificationPreference>(),
);

List _overrides({
  required TokenStore store,
  required AuthRepository auth,
  required PushTokenSource push,
}) => [
  tokenStoreProvider.overrideWithValue(store),
  authRepositoryProvider.overrideWithValue(auth),
  pushTokenSourceProvider.overrideWithValue(push),
  reportsRepositoryProvider.overrideWithValue(_EmptyReports()),
  transparencyRepositoryProvider.overrideWithValue(_EmptyTransparency()),
];

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  testWidgets(
    'unauthenticated push open does not navigate; buffers until auth',
    (tester) async {
      SharedPreferences.setMockInitialValues({});
      final store = _FakeStore(); // no token → Login
      final push = _ControllablePushSource();
      final auth = _AuthRepo(_me());

      await tester.pumpWidget(
        ProviderScope(
          overrides: [..._overrides(store: store, auth: auth, push: push)],
          child: const LamToApp(),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('Đăng nhập'), findsWidgets);
      expect(find.byType(IssueDetailScreen), findsNothing);

      // Background/foreground open while still on Login — must not push routes.
      push.emitOpened({'type': 'report', 'id': '42'});
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));
      expect(find.byType(IssueDetailScreen), findsNothing);
      expect(find.byType(LedgerDetailScreen), findsNothing);
      expect(find.byType(NotificationsScreen), findsNothing);

      // Sign in → buffered allowlisted link applies once.
      await tester.enterText(find.byType(TextField).at(0), 'r@example.com');
      await tester.enterText(find.byType(TextField).at(1), 'secret');
      await tester.tap(find.widgetWithText(FilledButton, 'Đăng nhập'));
      await tester.pumpAndSettle();

      expect(find.byType(IssueDetailScreen), findsOneWidget);
    },
  );

  testWidgets(
    'authenticated cold-start initial message navigates allowlisted report',
    (tester) async {
      SharedPreferences.setMockInitialValues({});
      final store = _FakeStore('knox');
      final push = _ControllablePushSource()
        ..initial = {'type': 'report', 'id': '7'};
      final auth = _AuthRepo(_me());

      await tester.pumpWidget(
        ProviderScope(
          overrides: [..._overrides(store: store, auth: auth, push: push)],
          child: const LamToApp(),
        ),
      );
      // Bootstrap + post-frame wire + flush.
      await tester.pumpAndSettle();

      expect(find.byType(IssueDetailScreen), findsOneWidget);
    },
  );

  testWidgets('bill push opens bill detail', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final store = _FakeStore('knox');
    final push = _ControllablePushSource()
      ..initial = {'type': 'bill', 'id': '7'};

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          ..._overrides(store: store, auth: _AuthRepo(_me()), push: push),
          billDetailProvider(7).overrideWith(
            (ref) async => BillDetail(
              (builder) => builder
                ..id = 7
                ..title = 'July bill'
                ..amountVnd = 250000
                ..status = BillStatusEnum.ISSUED
                ..period = '2026-07'
                ..issuedAt = DateTime.utc(2026, 7, 1)
                ..note = ''
                ..documentFilename = 'bill.pdf'
                ..documentDownloadUrl = '/api/v1/documents/t',
            ),
          ),
        ],
        child: const LamToApp(),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byType(BillDetailScreen), findsOneWidget);
  });

  testWidgets('authenticated stream open navigates ledger without re-open', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final store = _FakeStore('knox');
    final push = _ControllablePushSource();
    final auth = _AuthRepo(_me());

    await tester.pumpWidget(
      ProviderScope(
        overrides: [..._overrides(store: store, auth: auth, push: push)],
        child: const LamToApp(),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.byType(LedgerDetailScreen), findsNothing);

    final container = ProviderScope.containerOf(
      tester.element(find.byType(HomeShell)),
    );
    container.read(ledgerSegmentProvider.notifier).state = 1;

    push.emitOpened({'type': 'ledger', 'id': '99'});
    await tester.pumpAndSettle();

    expect(find.byType(LedgerDetailScreen), findsOneWidget);
    expect(container.read(ledgerSegmentProvider), 0);
  });
}
