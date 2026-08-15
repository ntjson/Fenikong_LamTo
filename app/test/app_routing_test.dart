import 'package:built_collection/built_collection.dart';
import 'package:dio/dio.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/app.dart';
import 'package:lamto/core/providers.dart';
import 'package:lamto/core/token_store.dart';
import 'package:lamto/features/auth/auth_repository.dart';
import 'package:lamto/features/notifications/notifications_screen.dart';
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

class _Repo implements AuthRepository {
  _Repo(this._me, {this.error});
  final Me? _me;
  final Object? error;
  @override
  Future<String> login(String i, String p) async => 'tok';
  @override
  Future<Me> fetchMe() async {
    final err = error;
    if (err != null) throw err;
    final me = _me;
    if (me == null) throw StateError('none');
    return me;
  }

  @override
  Future<void> logout() async {}

  @override
  Future<void> logoutAll() async {}
}

Me _meWith(int occupancies) => Me((b) {
  final list = ListBuilder<Occupancy>();
  for (var i = 0; i < occupancies; i++) {
    list.add(
      Occupancy(
        (o) => o
          ..id = i + 1
          ..unitLabel = 'A-${i + 1}'
          ..buildingName = 'Toa A',
      ),
    );
  }
  b
    ..displayName = 'R'
    ..email = 'r@example.com'
    ..phone = null
    ..occupancies = list
    ..notificationPreferences = ListBuilder<NotificationPreference>();
});

Future<void> _pump(
  WidgetTester tester, {
  required Me? me,
  String? token,
  Object? fetchError,
}) async {
  SharedPreferences.setMockInitialValues({});
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        tokenStoreProvider.overrideWithValue(
          _FakeStore(token ?? (me != null ? 't' : null)),
        ),
        authRepositoryProvider.overrideWithValue(_Repo(me, error: fetchError)),
      ],
      child: const LamToApp(),
    ),
  );
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('no session shows Login', (tester) async {
    await _pump(tester, me: null);
    expect(find.text('Đăng nhập'), findsWidgets);
  });

  testWidgets('multi-occupancy shows the picker', (tester) async {
    await _pump(tester, me: _meWith(2));
    expect(find.text('Chọn căn hộ của bạn'), findsOneWidget);
  });

  testWidgets('single occupancy lands on the tab shell', (tester) async {
    await _pump(tester, me: _meWith(1));
    expect(find.text('Trang chính'), findsWidgets);
  });

  testWidgets('bootstrap network error shows retry not Login', (tester) async {
    await _pump(
      tester,
      me: null,
      token: 't',
      fetchError: DioException(
        requestOptions: RequestOptions(path: '/api/v1/me'),
        type: DioExceptionType.connectionTimeout,
      ),
    );
    // Should show bootstrap error with retry, not the login form primary.
    expect(find.text('Thử lại'), findsOneWidget);
    expect(find.textContaining('Không có kết nối'), findsWidgets);
    expect(find.text('Đăng nhập'), findsNothing);
  });

  testWidgets('Android shell uses NavigationBar', (tester) async {
    // Compact width: the default 800px test view now gets a NavigationRail.
    tester.view.physicalSize = const Size(400, 800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);
    final previous = debugDefaultTargetPlatformOverride;
    debugDefaultTargetPlatformOverride = TargetPlatform.android;
    try {
      await _pump(tester, me: _meWith(1));
      expect(find.byType(NavigationBar), findsOneWidget);
      expect(
        tester.widget<NavigationBar>(find.byType(NavigationBar)).destinations,
        hasLength(4),
      );
      expect(find.byType(FloatingActionButton), findsOneWidget);
      expect(find.byType(CupertinoTabBar), findsNothing);
    } finally {
      debugDefaultTargetPlatformOverride = previous;
    }
  });

  testWidgets('Android shell uses NavigationRail at expanded width', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(900, 600);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);
    final previous = debugDefaultTargetPlatformOverride;
    debugDefaultTargetPlatformOverride = TargetPlatform.android;
    try {
      await _pump(tester, me: _meWith(1));
      expect(find.byType(NavigationRail), findsOneWidget);
      expect(
        tester.widget<NavigationRail>(find.byType(NavigationRail)).destinations,
        hasLength(4),
      );
      expect(find.byType(FloatingActionButton), findsOneWidget);
      expect(find.byType(NavigationBar), findsNothing);
    } finally {
      debugDefaultTargetPlatformOverride = previous;
    }
  });

  testWidgets('iOS shell uses CupertinoTabBar', (tester) async {
    final previous = debugDefaultTargetPlatformOverride;
    debugDefaultTargetPlatformOverride = TargetPlatform.iOS;
    try {
      await _pump(tester, me: _meWith(1));
      expect(find.byType(CupertinoTabBar), findsOneWidget);
      expect(
        tester.widget<CupertinoTabBar>(find.byType(CupertinoTabBar)).items,
        hasLength(4),
      );
      expect(find.byIcon(CupertinoIcons.add), findsOneWidget);
    } finally {
      debugDefaultTargetPlatformOverride = previous;
    }
  });

  testWidgets('iOS detail navigation uses a Cupertino route', (tester) async {
    final previous = debugDefaultTargetPlatformOverride;
    debugDefaultTargetPlatformOverride = TargetPlatform.iOS;
    try {
      await _pump(tester, me: _meWith(1));
      await tester.tap(find.byIcon(Icons.notifications_outlined));
      await tester.pumpAndSettle();
      final route = ModalRoute.of(
        tester.element(find.byType(NotificationsScreen)),
      );
      expect(route, isA<CupertinoPageRoute<void>>());
    } finally {
      debugDefaultTargetPlatformOverride = previous;
    }
  });

  testWidgets('multi-occupancy pick lands on tab shell without re-login', (
    tester,
  ) async {
    await _pump(tester, me: _meWith(2));
    expect(find.text('Chọn căn hộ của bạn'), findsOneWidget);
    await tester.tap(find.text('Toa A · A-1'));
    await tester.pumpAndSettle();
    expect(find.text('Trang chính'), findsWidgets);
    expect(find.text('Chọn căn hộ của bạn'), findsNothing);
  });

  testWidgets('zero occupancy shows dedicated empty state and sign-out', (
    tester,
  ) async {
    await _pump(tester, me: _meWith(0));
    expect(find.text('Chưa có căn hộ liên kết'), findsOneWidget);
    expect(find.textContaining('chưa có căn hộ'), findsWidgets);
    expect(find.text('Đăng xuất'), findsOneWidget);
    // Not the generic failure string.
    expect(find.text('Đã có lỗi xảy ra. Vui lòng thử lại.'), findsNothing);

    await tester.tap(find.text('Đăng xuất'));
    await tester.pumpAndSettle();
    expect(find.text('Đăng nhập'), findsWidgets);
  });

  testWidgets('iOS CupertinoTabScaffold uses CupertinoTabController', (
    tester,
  ) async {
    final previous = debugDefaultTargetPlatformOverride;
    debugDefaultTargetPlatformOverride = TargetPlatform.iOS;
    try {
      await _pump(tester, me: _meWith(1));
      final scaffold = tester.widget<CupertinoTabScaffold>(
        find.byType(CupertinoTabScaffold),
      );
      expect(scaffold.controller, isNotNull);
      expect(scaffold.controller!.index, 0);
      // Tap second destination via bar; Report is now a primary action.
      await tester.tap(find.text('Việc của tôi'));
      await tester.pumpAndSettle();
      expect(scaffold.controller!.index, 1);
      expect(find.text('Việc của tôi'), findsWidgets);
    } finally {
      debugDefaultTargetPlatformOverride = previous;
    }
  });
}
