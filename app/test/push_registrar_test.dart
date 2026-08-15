import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/features/push/push_registrar.dart';
import 'package:lamto/features/push/push_token_source.dart';
import 'package:lamto/features/transparency/transparency_repository.dart';
import 'package:lamto_api/lamto_api.dart';
import 'package:shared_preferences/shared_preferences.dart';

class _FakeSource implements PushTokenSource {
  _FakeSource({
    this.permission = PushPermissionResult.granted,
    this.token = 'tok-1',
  });
  PushPermissionResult permission;
  String? token;
  int requestCount = 0;
  final refresh = StreamController<String>.broadcast();

  @override
  Future<PushPermissionResult> requestPermission() async {
    requestCount++;
    return permission;
  }

  @override
  Future<String?> getToken() async {
    // Realistic: denied / unsupported yields no usable FCM token.
    if (permission != PushPermissionResult.granted) return null;
    return token;
  }

  @override
  Stream<String> get onTokenRefresh => refresh.stream;
  @override
  Future<Map<String, String>?> initialMessageData() async => null;
  @override
  Stream<Map<String, String>> get onMessageOpened => const Stream.empty();
}

class _FakeRepo implements TransparencyRepository {
  final registered = <(String, String)>[];
  final deactivated = <String>[];
  Object? deactivateError;
  Duration? deactivateDelay;
  int deactivateCalls = 0;

  @override
  Future<Device> registerDevice({
    required String installId,
    required String fcmToken,
    required String platform,
    String appVersion = '',
  }) async {
    registered.add((installId, fcmToken));
    return Device(
      (b) => b
        ..installId = installId
        ..platform = platform
        ..active = true,
    );
  }

  @override
  Future<void> deactivateDevice(String installId) async {
    deactivateCalls++;
    if (deactivateDelay != null) {
      await Future<void>.delayed(deactivateDelay!);
    }
    if (deactivateError != null) throw deactivateError!;
    deactivated.add(installId);
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class _OrderTrackingRepo implements TransparencyRepository {
  _OrderTrackingRepo(this._inner, this.order);
  final _FakeRepo _inner;
  final List<String> order;

  List<(String, String)> get registered => _inner.registered;
  List<String> get deactivated => _inner.deactivated;

  @override
  Future<Device> registerDevice({
    required String installId,
    required String fcmToken,
    required String platform,
    String appVersion = '',
  }) async {
    order.add('register');
    return _inner.registerDevice(
      installId: installId,
      fcmToken: fcmToken,
      platform: platform,
      appVersion: appVersion,
    );
  }

  @override
  Future<void> deactivateDevice(String installId) async {
    order.add('deactivate');
    return _inner.deactivateDevice(installId);
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() => SharedPreferences.setMockInitialValues({}));

  test('registers after consent with a stable install id', () async {
    final source = _FakeSource();
    final repo = _FakeRepo();
    final store = InstallIdStore();
    final registrar = PushRegistrar(
      tokenSource: source,
      repository: repo,
      installIdStore: store,
    );

    await registrar.registerAfterConsent();
    await registrar.registerAfterConsent(); // idempotent upsert
    expect(repo.registered, hasLength(2));
    expect(repo.registered[0].$1, repo.registered[1].$1); // same install id
    expect(repo.registered[0].$2, 'tok-1');
  });

  test('no permission or no token -> no registration, no crash', () async {
    final repo = _FakeRepo();
    final denied = PushRegistrar(
      tokenSource: _FakeSource(permission: PushPermissionResult.denied),
      repository: repo,
      installIdStore: InstallIdStore(),
    );
    await denied.registerAfterConsent();
    final tokenless = PushRegistrar(
      tokenSource: _FakeSource(token: null),
      repository: repo,
      installIdStore: InstallIdStore(),
    );
    await tokenless.registerAfterConsent();
    expect(repo.registered, isEmpty);
  });

  test(
    'token refresh re-registers; deregister deactivates the install',
    () async {
      final source = _FakeSource();
      final repo = _FakeRepo();
      final registrar = PushRegistrar(
        tokenSource: source,
        repository: repo,
        installIdStore: InstallIdStore(),
      );
      await registrar.registerAfterConsent();
      registrar.watchTokenRefresh();
      source.refresh.add('tok-2');
      await Future<void>.delayed(Duration.zero);
      expect(repo.registered.last.$2, 'tok-2');

      await registrar.deregister();
      expect(repo.deactivated.single, repo.registered.first.$1);
    },
  );

  test('A4: OS permission requested only once per install', () async {
    final source = _FakeSource();
    final repo = _FakeRepo();
    final registrar = PushRegistrar(
      tokenSource: source,
      repository: repo,
      installIdStore: InstallIdStore(),
    );

    await registrar.registerAfterConsent();
    await registrar.registerAfterConsent();
    await registrar.registerAfterConsent();

    expect(source.requestCount, 1);
    expect(repo.registered, hasLength(3));

    final prefs = await SharedPreferences.getInstance();
    final installId = repo.registered.first.$1;
    expect(prefs.getBool(PushPrefsKeys.permissionRequested(installId)), isTrue);
  });

  test(
    'A4: denied once never re-prompts; later OS grant can register',
    () async {
      final source = _FakeSource(permission: PushPermissionResult.denied);
      final repo = _FakeRepo();
      final registrar = PushRegistrar(
        tokenSource: source,
        repository: repo,
        installIdStore: InstallIdStore(),
      );

      await registrar.registerAfterConsent();
      await registrar.registerAfterConsent(); // still denied
      expect(source.requestCount, 1);
      expect(repo.registered, isEmpty);

      // User enables notifications in system settings: still no OS re-prompt.
      source.permission = PushPermissionResult.granted;
      await registrar.registerAfterConsent();
      expect(source.requestCount, 1);
      expect(repo.registered, hasLength(1));

      final prefs = await SharedPreferences.getInstance();
      final installId = repo.registered.first.$1;
      expect(
        prefs.getBool(PushPrefsKeys.permissionRequested(installId)),
        isTrue,
      );
    },
  );

  test('I1: unsupported does not set permission-requested flag', () async {
    final store = InstallIdStore();
    final installId = await store.get();
    final prefs = await SharedPreferences.getInstance();
    final requestedKey = PushPrefsKeys.permissionRequested(installId);

    // Firebase missing / unsupported — OS never consulted.
    final source = _FakeSource(permission: PushPermissionResult.unsupported);
    final registrar = PushRegistrar(
      tokenSource: source,
      repository: _FakeRepo(),
      installIdStore: store,
    );
    await registrar.registerAfterConsent();
    await registrar.registerAfterConsent();
    expect(source.requestCount, 2); // may retry later
    expect(prefs.getBool(requestedKey), isNull);
  });

  test(
    'I1: real deny burns permission-requested flag (no re-prompt)',
    () async {
      final store = InstallIdStore();
      final installId = await store.get();
      final prefs = await SharedPreferences.getInstance();
      final requestedKey = PushPrefsKeys.permissionRequested(installId);

      final source = _FakeSource(permission: PushPermissionResult.denied);
      final registrar = PushRegistrar(
        tokenSource: source,
        repository: _FakeRepo(),
        installIdStore: store,
      );
      await registrar.registerAfterConsent();
      await registrar.registerAfterConsent();
      expect(source.requestCount, 1);
      expect(prefs.getBool(requestedKey), isTrue);
    },
  );

  test(
    'I1: after unsupported, a later granted consult can still prompt + register',
    () async {
      final source = _FakeSource(permission: PushPermissionResult.unsupported);
      final repo = _FakeRepo();
      final registrar = PushRegistrar(
        tokenSource: source,
        repository: repo,
        installIdStore: InstallIdStore(),
      );

      await registrar.registerAfterConsent();
      expect(source.requestCount, 1);
      expect(repo.registered, isEmpty);

      // Production build with Firebase becomes available — OS may be asked once.
      source.permission = PushPermissionResult.granted;
      source.token = 'tok-prod';
      await registrar.registerAfterConsent();
      expect(source.requestCount, 2);
      expect(repo.registered, hasLength(1));
      expect(repo.registered.first.$2, 'tok-prod');

      final prefs = await SharedPreferences.getInstance();
      final installId = repo.registered.first.$1;
      expect(
        prefs.getBool(PushPrefsKeys.permissionRequested(installId)),
        isTrue,
      );
    },
  );

  test('A5: successful deregister clears any pending retry key', () async {
    final source = _FakeSource();
    final repo = _FakeRepo();
    final registrar = PushRegistrar(
      tokenSource: source,
      repository: repo,
      installIdStore: InstallIdStore(),
    );
    await registrar.registerAfterConsent();
    final installId = repo.registered.first.$1;

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(PushPrefsKeys.pendingDeregister, installId);

    await registrar.deregister();
    expect(repo.deactivated, [installId]);
    expect(prefs.getString(PushPrefsKeys.pendingDeregister), isNull);
  });

  test('A5: failed deregister persists pending id for retry', () async {
    final source = _FakeSource();
    final repo = _FakeRepo()..deactivateError = Exception('network');
    final registrar = PushRegistrar(
      tokenSource: source,
      repository: repo,
      installIdStore: InstallIdStore(),
    );
    await registrar.registerAfterConsent();
    final installId = repo.registered.first.$1;

    await registrar.deregister();
    expect(repo.deactivated, isEmpty);

    final prefs = await SharedPreferences.getInstance();
    expect(prefs.getString(PushPrefsKeys.pendingDeregister), installId);

    // Next authenticated session retries and clears on success.
    repo.deactivateError = null;
    await registrar.retryPendingDeregister();
    expect(repo.deactivated, [installId]);
    expect(prefs.getString(PushPrefsKeys.pendingDeregister), isNull);
  });

  test('I2: deregister timeout takes pending path and completes', () async {
    final source = _FakeSource();
    final repo = _FakeRepo()..deactivateDelay = const Duration(seconds: 30);
    final registrar = PushRegistrar(
      tokenSource: source,
      repository: repo,
      installIdStore: InstallIdStore(),
      deregisterTimeout: const Duration(milliseconds: 50),
    );
    await registrar.registerAfterConsent();
    final installId = repo.registered.first.$1;

    final sw = Stopwatch()..start();
    await registrar.deregister();
    sw.stop();

    expect(sw.elapsed, lessThan(const Duration(seconds: 2)));
    expect(repo.deactivated, isEmpty);
    final prefs = await SharedPreferences.getInstance();
    expect(prefs.getString(PushPrefsKeys.pendingDeregister), installId);
  });

  test('A5: retryPendingDeregister is no-op without pending key', () async {
    final repo = _FakeRepo();
    final registrar = PushRegistrar(
      tokenSource: _FakeSource(),
      repository: repo,
      installIdStore: InstallIdStore(),
    );
    await registrar.retryPendingDeregister();
    expect(repo.deactivated, isEmpty);
  });

  test('A5: failed retry leaves pending key for a later session', () async {
    final repo = _FakeRepo()..deactivateError = Exception('still down');
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(PushPrefsKeys.pendingDeregister, 'install-xyz');

    final registrar = PushRegistrar(
      tokenSource: _FakeSource(),
      repository: repo,
      installIdStore: InstallIdStore(),
    );
    await registrar.retryPendingDeregister();
    expect(repo.deactivated, isEmpty);
    expect(prefs.getString(PushPrefsKeys.pendingDeregister), 'install-xyz');
  });

  test(
    'A6: FirebasePushTokenSource degrades without platform config',
    () async {
      final source = FirebasePushTokenSource();
      // No google-services.json / GoogleService-Info.plist in this environment.
      expect(
        await source.requestPermission(),
        PushPermissionResult.unsupported,
      );
      expect(await source.getToken(), isNull);
      expect(await source.initialMessageData(), isNull);
      await expectLater(source.onTokenRefresh, emitsDone);
      await expectLater(source.onMessageOpened, emitsDone);
    },
  );

  test('ensureRegisteredIfConsented re-registers without re-prompt', () async {
    final source = _FakeSource();
    final repo = _FakeRepo();
    final store = InstallIdStore();
    final installId = await store.get();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(PushPrefsKeys.permissionRequested(installId), true);

    final registrar = PushRegistrar(
      tokenSource: source,
      repository: repo,
      installIdStore: store,
    );
    await registrar.ensureRegisteredIfConsented();
    expect(source.requestCount, 0); // no OS prompt
    expect(repo.registered, hasLength(1));
    expect(repo.registered.single.$1, installId);
    expect(repo.registered.single.$2, 'tok-1');
  });

  test('ensureRegisteredIfConsented no-ops before first consent', () async {
    final source = _FakeSource();
    final repo = _FakeRepo();
    final registrar = PushRegistrar(
      tokenSource: source,
      repository: repo,
      installIdStore: InstallIdStore(),
    );
    await registrar.ensureRegisteredIfConsented();
    expect(source.requestCount, 0);
    expect(repo.registered, isEmpty);
  });

  test(
    'onAuthenticatedSession sequences deactivate then register for pending install',
    () async {
      final source = _FakeSource();
      final repo = _FakeRepo();
      final store = InstallIdStore();
      final installId = await store.get();
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool(PushPrefsKeys.permissionRequested(installId), true);
      await prefs.setString(PushPrefsKeys.pendingDeregister, installId);

      // Slow deactivate so a race would let register win first if parallel.
      repo.deactivateDelay = const Duration(milliseconds: 80);
      final order = <String>[];
      final tracking = _OrderTrackingRepo(repo, order);

      final registrar = PushRegistrar(
        tokenSource: source,
        repository: tracking,
        installIdStore: store,
        deregisterTimeout: const Duration(seconds: 2),
      );
      await registrar.onAuthenticatedSession();

      expect(order, ['deactivate', 'register']);
      expect(tracking.registered, hasLength(1));
      expect(tracking.deactivated, [installId]);
      // Pending cleared so a later session cannot deactivate after register.
      expect(prefs.getString(PushPrefsKeys.pendingDeregister), isNull);
    },
  );

  test(
    'onAuthenticatedSession clears sticky pending when re-registering same install',
    () async {
      final source = _FakeSource();
      final repo = _FakeRepo();
      final store = InstallIdStore();
      final installId = await store.get();
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool(PushPrefsKeys.permissionRequested(installId), true);
      await prefs.setString(PushPrefsKeys.pendingDeregister, installId);
      repo.deactivateError = Exception('still offline');

      final registrar = PushRegistrar(
        tokenSource: source,
        repository: repo,
        installIdStore: store,
        deregisterTimeout: const Duration(milliseconds: 50),
      );
      await registrar.onAuthenticatedSession();

      // Register still happened via upsert path.
      expect(repo.registered, hasLength(1));
      // Pending for this install must not stick (would kill push next bootstrap).
      expect(prefs.getString(PushPrefsKeys.pendingDeregister), isNull);
    },
  );
}
