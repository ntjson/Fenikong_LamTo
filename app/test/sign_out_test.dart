import 'package:built_collection/built_collection.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lamto/core/providers.dart';
import 'package:lamto/core/token_store.dart';
import 'package:lamto/features/auth/auth_repository.dart';
import 'package:lamto/features/auth/session_controller.dart';
import 'package:lamto/features/push/push_registrar.dart';
import 'package:lamto/features/push/push_token_source.dart';
import 'package:lamto/features/transparency/transparency_repository.dart';
import 'package:lamto_api/lamto_api.dart';
import 'package:shared_preferences/shared_preferences.dart';

class _FakeStore implements TokenStore {
  String? token = 'knox-token';
  @override
  Future<void> clear() async => token = null;
  @override
  Future<String?> read() async => token;
  @override
  Future<void> write(String value) async => token = value;
}

class _FakeAuth implements AuthRepository {
  final calls = <String>[];
  bool throwOnLogout = false;

  @override
  Future<Me> fetchMe() async => Me(
    (b) => b
      ..displayName = 'R'
      ..email = 'r@example.com'
      ..occupancies = ListBuilder<Occupancy>()
      ..notificationPreferences = ListBuilder<NotificationPreference>(),
  );
  @override
  Future<String> login(String i, String p) async => 'tok';
  @override
  Future<void> logout() async {
    calls.add('logout');
    if (throwOnLogout) {
      throw DioException(requestOptions: RequestOptions(path: '/x'));
    }
  }

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

class _FakeDevices implements TransparencyRepository {
  final deactivated = <String>[];
  Object? deactivateError;

  @override
  Future<void> deactivateDevice(String installId) async {
    if (deactivateError != null) throw deactivateError!;
    deactivated.add(installId);
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  ProviderContainer makeContainer(
    _FakeAuth auth, {
    TransparencyRepository? devices,
  }) {
    SharedPreferences.setMockInitialValues({});
    final container = ProviderContainer(
      overrides: [
        tokenStoreProvider.overrideWithValue(_FakeStore()),
        authRepositoryProvider.overrideWithValue(auth),
        pushRegistrarProvider.overrideWithValue(
          PushRegistrar(
            tokenSource: _NoPushSource(),
            repository: devices ?? _FakeDevices(),
            installIdStore: InstallIdStore(),
          ),
        ),
      ],
    );
    addTearDown(container.dispose);
    return container;
  }

  test('signOut calls server logout then clears locally', () async {
    final auth = _FakeAuth();
    final container = makeContainer(auth);
    await container.read(sessionControllerProvider.future);
    await container.read(sessionControllerProvider.notifier).signOut();
    expect(auth.calls, ['logout']);
    final state = await container.read(sessionControllerProvider.future);
    expect(state, isA<SessionUnauthenticated>());
  });

  test(
    'logout-all variant and server failure never block local sign-out',
    () async {
      final auth = _FakeAuth()..throwOnLogout = true;
      final container = makeContainer(auth);
      await container.read(sessionControllerProvider.future);
      // Throws server-side; still signs out locally.
      await container.read(sessionControllerProvider.notifier).signOut();
      expect(
        await container.read(sessionControllerProvider.future),
        isA<SessionUnauthenticated>(),
      );

      final auth2 = _FakeAuth();
      final container2 = makeContainer(auth2);
      await container2.read(sessionControllerProvider.future);
      await container2
          .read(sessionControllerProvider.notifier)
          .signOut(allDevices: true);
      expect(auth2.calls, ['logout-all']);
    },
  );

  test('signOut deregisters push device before server logout (A5)', () async {
    final auth = _FakeAuth();
    final devices = _FakeDevices();
    final container = makeContainer(auth, devices: devices);
    await container.read(sessionControllerProvider.future);
    final installId = await InstallIdStore().get();
    await container.read(sessionControllerProvider.notifier).signOut();
    expect(devices.deactivated, [installId]);
    expect(auth.calls, ['logout']);
  });

  test(
    'signOut still clears session when deregister fails (A5 pending)',
    () async {
      final auth = _FakeAuth();
      final devices = _FakeDevices()..deactivateError = Exception('down');
      final container = makeContainer(auth, devices: devices);
      await container.read(sessionControllerProvider.future);
      final installId = await InstallIdStore().get();
      await container.read(sessionControllerProvider.notifier).signOut();
      expect(devices.deactivated, isEmpty);
      expect(
        await container.read(sessionControllerProvider.future),
        isA<SessionUnauthenticated>(),
      );
      final prefs = await SharedPreferences.getInstance();
      expect(prefs.getString(PushPrefsKeys.pendingDeregister), installId);
    },
  );
}
