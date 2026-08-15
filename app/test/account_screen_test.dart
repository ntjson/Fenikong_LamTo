import 'package:built_collection/built_collection.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lamto/core/providers.dart';
import 'package:lamto/core/token_store.dart';
import 'package:lamto/features/account/account_screen.dart';
import 'package:lamto/features/auth/auth_repository.dart';
import 'package:lamto/features/push/push_registrar.dart';
import 'package:lamto/features/push/push_token_source.dart';
import 'package:lamto/features/reports/reports_repository.dart';
import 'package:lamto/features/shell/home_shell.dart';
import 'package:lamto/features/transparency/transparency_repository.dart';
import 'package:lamto/l10n/app_localizations.dart';
import 'package:lamto_api/lamto_api.dart';
import 'package:shared_preferences/shared_preferences.dart';

Me _me() => Me(
  (b) => b
    ..displayName = 'Cư dân A'
    ..email = 'r@example.com'
    ..occupancies = ListBuilder<Occupancy>([
      Occupancy(
        (o) => o
          ..id = 1
          ..unitLabel = 'B-1204'
          ..buildingName = 'Tòa A',
      ),
      Occupancy(
        (o) => o
          ..id = 2
          ..unitLabel = 'C-101'
          ..buildingName = 'Tòa C',
      ),
    ])
    ..notificationPreferences = ListBuilder<NotificationPreference>([
      NotificationPreference(
        (p) => p
          ..eventCode = 'ledger.publication'
          ..emailEnabled = true
          ..pushEnabled = false,
      ),
    ]),
);

Me _phoneOnlyMe() => _me().rebuild(
  (b) => b
    ..email = null
    ..phone = '0901000000',
);

class _FakeAuth implements AuthRepository {
  _FakeAuth([this.me]);
  final Me? me;
  final calls = <String>[];

  @override
  Future<Me> fetchMe() async => me ?? _me();
  @override
  Future<String> login(String i, String p) async => 'tok';
  @override
  Future<void> logout() async => calls.add('logout');
  @override
  Future<void> logoutAll() async => calls.add('logout-all');
}

class _NoPushSource implements PushTokenSource {
  @override
  Future<PushPermissionResult> requestPermission() async =>
      PushPermissionResult.unsupported;
  @override
  Future<String?> getToken() async => null;
  @override
  Stream<String> get onTokenRefresh => const Stream.empty();
  @override
  Future<Map<String, String>?> initialMessageData() async => null;
  @override
  Stream<Map<String, String>> get onMessageOpened => const Stream.empty();
}

/// Bootstrap reads secure storage first; give it an in-memory token.
class _FakeStore implements TokenStore {
  String? token = 'knox-token';
  @override
  Future<void> clear() async => token = null;
  @override
  Future<String?> read() async => token;
  @override
  Future<void> write(String value) async => token = value;
}

class _FakeTransparency implements TransparencyRepository {
  final patches = <(String, bool?, bool?)>[];

  @override
  Future<List<NotificationPreference>> updatePreference({
    required String eventCode,
    bool? emailEnabled,
    bool? pushEnabled,
  }) async {
    patches.add((eventCode, emailEnabled, pushEnabled));
    return [];
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

/// Preference PATCH fails so the account screen must revert + surface error.
/// Fund/ledger still succeed so HomeShell other tabs do not block Account.
class _ThrowingTransparency implements TransparencyRepository {
  @override
  Future<List<NotificationPreference>> updatePreference({
    required String eventCode,
    bool? emailEnabled,
    bool? pushEnabled,
  }) async {
    throw Exception('boom');
  }

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
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class _EmptyReports implements ReportsRepository {
  @override
  Future<PaginatedReportSummaryList> listReports({String? cursor}) async =>
      PaginatedReportSummaryList(
        (b) => b..results = ListBuilder<ReportSummary>(),
      );

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

/// Exception('boom') → Failure.fromObject → server_error → l10n.errServer (vi).
const _errServerVi =
    'Đã có lỗi từ phía hệ thống. Thao tác có thể chưa được lưu. Vui lòng thử lại sau.';

const _unsentWorkVi =
    'Phản ánh đang soạn và ảnh chưa gửi trên thiết bị này sẽ bị xóa.';

/// Pumps the account tab with a sign-out-capable session (inert push stack).
Future<_FakeAuth> _pumpForSignOut(WidgetTester tester) async {
  final auth = _FakeAuth();
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        tokenStoreProvider.overrideWithValue(_FakeStore()),
        authRepositoryProvider.overrideWithValue(auth),
        transparencyRepositoryProvider.overrideWithValue(_FakeTransparency()),
        pushRegistrarProvider.overrideWithValue(
          PushRegistrar(
            tokenSource: _NoPushSource(),
            repository: _FakeTransparency(),
            installIdStore: InstallIdStore(),
          ),
        ),
      ],
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: const Locale('vi'),
        home: const Scaffold(body: AccountScreen()),
      ),
    ),
  );
  await tester.pumpAndSettle();
  return auth;
}

void main() {
  testWidgets('phone-only account omits a blank email row', (tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          tokenStoreProvider.overrideWithValue(_FakeStore()),
          authRepositoryProvider.overrideWithValue(_FakeAuth(_phoneOnlyMe())),
          transparencyRepositoryProvider.overrideWithValue(_FakeTransparency()),
        ],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: const Scaffold(body: AccountScreen()),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('0901000000'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets(
    'shows profile, occupancies, preference toggles; patches a flip',
    (tester) async {
      SharedPreferences.setMockInitialValues({}); // occupancy store backing
      final repo = _FakeTransparency();
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            tokenStoreProvider.overrideWithValue(_FakeStore()),
            authRepositoryProvider.overrideWithValue(_FakeAuth()),
            transparencyRepositoryProvider.overrideWithValue(repo),
          ],
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('vi'),
            home: const Scaffold(body: AccountScreen()),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Cư dân A'), findsOneWidget);
      expect(find.text('Tòa A · B-1204'), findsOneWidget);
      expect(find.text('Tòa C · C-101'), findsOneWidget);
      expect(find.text('Nhận tất cả thông báo'), findsOneWidget);

      // ledger.publication has pushEnabled=false server-side, so the master
      // switch starts OFF; flipping it PATCHes every code on both channels.
      final master = find.byKey(const Key('notifications_all'));
      expect(tester.widget<SwitchListTile>(master).value, isFalse);
      await tester.tap(master);
      await tester.pumpAndSettle();
      expect(tester.widget<SwitchListTile>(master).value, isTrue);
      expect(
        repo.patches,
        containsAll([
          ('report.receipt', true, true),
          ('triage.status', true, true),
          ('work.completed', true, true),
          ('ledger.publication', true, true),
          ('correction.status', true, true),
          ('building.announcement', true, true),
        ]),
      );
      expect(find.text('Đăng xuất'), findsOneWidget);
      expect(find.text('Đăng xuất mọi thiết bị'), findsOneWidget);
    },
  );

  testWidgets(
    'preference PATCH failure reverts switch and shows inline resident error',
    (tester) async {
      SharedPreferences.setMockInitialValues({});
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            tokenStoreProvider.overrideWithValue(_FakeStore()),
            authRepositoryProvider.overrideWithValue(_FakeAuth()),
            transparencyRepositoryProvider.overrideWithValue(
              _ThrowingTransparency(),
            ),
          ],
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('vi'),
            home: const Scaffold(body: AccountScreen()),
          ),
        ),
      );
      await tester.pumpAndSettle();

      final master = find.byKey(const Key('notifications_all'));
      // ledger.publication starts pushEnabled = false → master OFF.
      expect(tester.widget<SwitchListTile>(master).value, isFalse);

      await tester.tap(master);
      // Optimistic flip then async PATCH fail + revert.
      await tester.pump();
      await tester.pumpAndSettle();

      expect(tester.widget<SwitchListTile>(master).value, isFalse);
      // Inline error — not SnackBar (works under Cupertino shell too).
      expect(find.byKey(const Key('account_pref_error')), findsOneWidget);
      expect(find.text(_errServerVi), findsOneWidget);
      expect(find.byType(SnackBar), findsNothing);
    },
  );

  testWidgets(
    'iOS HomeShell CupertinoPageScaffold: PATCH fail shows visible error',
    (tester) async {
      // Production iOS path: CupertinoTabScaffold + CupertinoPageScaffold has no
      // Material ScaffoldMessenger. Inline error must still appear.
      final previous = debugDefaultTargetPlatformOverride;
      debugDefaultTargetPlatformOverride = TargetPlatform.iOS;
      try {
        SharedPreferences.setMockInitialValues({});
        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              tokenStoreProvider.overrideWithValue(_FakeStore()),
              authRepositoryProvider.overrideWithValue(_FakeAuth()),
              transparencyRepositoryProvider.overrideWithValue(
                _ThrowingTransparency(),
              ),
              reportsRepositoryProvider.overrideWithValue(_EmptyReports()),
            ],
            child: MaterialApp(
              // MaterialApp still supplies Theme/l10n; body is real HomeShell.
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
              locale: const Locale('vi'),
              home: const HomeShell(),
            ),
          ),
        );
        await tester.pumpAndSettle();

        // HomeShell iOS uses Cupertino chrome, not Material Scaffold.
        expect(find.byType(CupertinoTabScaffold), findsOneWidget);
        expect(find.byType(CupertinoPageScaffold), findsWidgets);
        // No Material Scaffold wrapping tab bodies on iOS.
        expect(find.byType(Scaffold), findsNothing);

        // Switch to Account tab (index 4).
        await tester.tap(find.text('Tài khoản'));
        await tester.pumpAndSettle();

        expect(find.byType(AccountScreen), findsOneWidget);

        final master = find.byKey(const Key('notifications_all'));
        expect(tester.widget<SwitchListTile>(master).value, isFalse);

        await tester.tap(master);
        await tester.pump();
        await tester.pumpAndSettle();

        // Toggle reverted + resident-visible inline error (no SnackBar host).
        expect(tester.widget<SwitchListTile>(master).value, isFalse);
        expect(find.byKey(const Key('account_pref_error')), findsOneWidget);
        expect(find.text(_errServerVi), findsOneWidget);
        expect(tester.takeException(), isNull);
      } finally {
        debugDefaultTargetPlatformOverride = previous;
      }
    },
  );

  testWidgets('sign out asks for confirmation and cancel keeps the session', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final auth = await _pumpForSignOut(tester);

    await tester.ensureVisible(find.text('Đăng xuất'));
    await tester.tap(find.text('Đăng xuất'));
    await tester.pumpAndSettle();

    expect(find.byType(AlertDialog), findsOneWidget);
    // Lean confirm: no consequence line when nothing unsent exists.
    expect(find.text(_unsentWorkVi), findsNothing);

    await tester.tap(find.text('Hủy'));
    await tester.pumpAndSettle();

    expect(find.byType(AlertDialog), findsNothing);
    expect(auth.calls, isEmpty);
    expect(find.text('Cư dân A'), findsOneWidget); // still signed in
  });

  testWidgets('confirming the sign-out dialog signs out', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final auth = await _pumpForSignOut(tester);

    await tester.ensureVisible(find.text('Đăng xuất'));
    await tester.tap(find.text('Đăng xuất'));
    await tester.pumpAndSettle();
    // The dialog's confirm action names the action, never "OK".
    await tester.tap(find.widgetWithText(TextButton, 'Đăng xuất'));
    await tester.pump();
    await tester.pump();

    expect(auth.calls, ['logout']);
  });

  testWidgets(
    'sign out of all devices warns about unsent work, then proceeds',
    (tester) async {
      SharedPreferences.setMockInitialValues({
        'lamto_report_draft_1':
            '{"client_ref":"c0ffee","text":"vòi nước rò rỉ"}',
      });
      final auth = await _pumpForSignOut(tester);

      await tester.ensureVisible(find.text('Đăng xuất mọi thiết bị'));
      await tester.tap(find.text('Đăng xuất mọi thiết bị'));
      await tester.pumpAndSettle();

      expect(find.byType(AlertDialog), findsOneWidget);
      expect(find.text(_unsentWorkVi), findsOneWidget);

      await tester.tap(find.widgetWithText(TextButton, 'Đăng xuất'));
      await tester.pump();
      await tester.pump();

      expect(auth.calls, ['logout-all']);
      final prefs = await SharedPreferences.getInstance();
      expect(prefs.getString('lamto_report_draft_1'), isNull); // draft wiped
    },
  );
}
