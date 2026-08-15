import 'package:built_collection/built_collection.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/core/occupancy.dart';
import 'package:lamto/core/occupancy_store.dart';
import 'package:lamto/core/providers.dart';
import 'package:lamto/core/token_store.dart';
import 'package:lamto/features/auth/auth_repository.dart';
import 'package:lamto/features/auth/session_controller.dart';
import 'package:lamto/features/push/push_registrar.dart';
import 'package:lamto/features/push/push_token_source.dart';
import 'package:lamto/features/reports/report_draft.dart';
import 'package:lamto/features/transparency/transparency_repository.dart';
import 'package:lamto_api/lamto_api.dart';
import 'package:shared_preferences/shared_preferences.dart';

class _FakeStore implements TokenStore {
  String? token;
  @override
  Future<void> clear() async => token = null;
  @override
  Future<String?> read() async => token;
  @override
  Future<void> write(String value) async => token = value;
}

class _FakeRepo implements AuthRepository {
  _FakeRepo({this.me, this.fetchError});
  Me? me;
  Object? fetchError;
  int fetchCount = 0;

  @override
  Future<String> login(String identifier, String password) async => 'tok';

  @override
  Future<Me> fetchMe() async {
    fetchCount++;
    final err = fetchError;
    if (err != null) {
      throw err;
    }
    if (me == null) throw StateError('no session');
    return me!;
  }

  @override
  Future<void> logout() async {}

  @override
  Future<void> logoutAll() async {}
}

Me _me({int occupancies = 0, List<int>? ids}) => Me(
  (b) => b
    ..displayName = 'Resident'
    ..email = 'r@example.com'
    ..phone = null
    ..occupancies = ListBuilder<Occupancy>([
      for (var i = 0; i < (ids?.length ?? occupancies); i++)
        Occupancy(
          (o) => o
            ..id = ids?[i] ?? (i + 1)
            ..unitLabel = 'A-${ids?[i] ?? (i + 1)}'
            ..buildingName = 'Toa A',
        ),
    ])
    ..notificationPreferences = ListBuilder<NotificationPreference>(),
);

DioException _dio(
  int? status, {
  DioExceptionType type = DioExceptionType.badResponse,
}) {
  final req = RequestOptions(path: '/api/v1/me');
  return DioException(
    requestOptions: req,
    response: status == null
        ? null
        : Response(requestOptions: req, statusCode: status, data: {}),
    type: type,
  );
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

class _NoopDevices implements TransparencyRepository {
  @override
  Future<void> deactivateDevice(String installId) async {}
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

/// Override push so signOut never hits the real Dio (no connect timeout).
PushRegistrar get _noopPushRegistrar => PushRegistrar(
  tokenSource: _NoPushSource(),
  repository: _NoopDevices(),
  installIdStore: InstallIdStore(),
);

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  test('bootstrap with no token -> unauthenticated without fetchMe', () async {
    final store = _FakeStore();
    final repo = _FakeRepo();
    final container = ProviderContainer(
      overrides: [
        tokenStoreProvider.overrideWithValue(store),
        authRepositoryProvider.overrideWithValue(repo),
        occupancyStoreProvider.overrideWithValue(OccupancyStore()),
      ],
    );
    addTearDown(container.dispose);
    final state = await container.read(sessionControllerProvider.future);
    expect(state, isA<SessionUnauthenticated>());
    expect(repo.fetchCount, 0);
  });

  test('bootstrap with session -> authenticated', () async {
    final store = _FakeStore()..token = 't';
    final container = ProviderContainer(
      overrides: [
        tokenStoreProvider.overrideWithValue(store),
        authRepositoryProvider.overrideWithValue(
          _FakeRepo(me: _me(occupancies: 1)),
        ),
        occupancyStoreProvider.overrideWithValue(OccupancyStore()),
      ],
    );
    addTearDown(container.dispose);
    final state = await container.read(sessionControllerProvider.future);
    expect(state, isA<SessionAuthenticated>());
  });

  test('bootstrap 401 -> unauthenticated and clears token', () async {
    final store = _FakeStore()..token = 't';
    final container = ProviderContainer(
      overrides: [
        tokenStoreProvider.overrideWithValue(store),
        authRepositoryProvider.overrideWithValue(
          _FakeRepo(fetchError: _dio(401)),
        ),
        occupancyStoreProvider.overrideWithValue(OccupancyStore()),
      ],
    );
    addTearDown(container.dispose);
    final state = await container.read(sessionControllerProvider.future);
    expect(state, isA<SessionUnauthenticated>());
    expect(store.token, isNull);
  });

  test('bootstrap network error -> SessionBootstrapError not Login', () async {
    final store = _FakeStore()..token = 't';
    final container = ProviderContainer(
      overrides: [
        tokenStoreProvider.overrideWithValue(store),
        authRepositoryProvider.overrideWithValue(
          _FakeRepo(
            fetchError: _dio(null, type: DioExceptionType.connectionTimeout),
          ),
        ),
        occupancyStoreProvider.overrideWithValue(OccupancyStore()),
      ],
    );
    addTearDown(container.dispose);
    final state = await container.read(sessionControllerProvider.future);
    expect(state, isA<SessionBootstrapError>());
    final err = state as SessionBootstrapError;
    expect(err.failure.code, 'network_error');
    expect(store.token, 't'); // token not cleared on transient failure
  });

  test('bootstrap schema error -> SessionBootstrapError', () async {
    final store = _FakeStore()..token = 't';
    final container = ProviderContainer(
      overrides: [
        tokenStoreProvider.overrideWithValue(store),
        authRepositoryProvider.overrideWithValue(
          _FakeRepo(fetchError: FormatException('bad json')),
        ),
        occupancyStoreProvider.overrideWithValue(OccupancyStore()),
      ],
    );
    addTearDown(container.dispose);
    final state = await container.read(sessionControllerProvider.future);
    expect(state, isA<SessionBootstrapError>());
    expect((state as SessionBootstrapError).failure.code, 'schema_error');
  });

  test('invalid persisted occupancy is cleared', () async {
    SharedPreferences.setMockInitialValues({
      'lamto_occupancy_r@example.com': 99,
    });
    final store = _FakeStore()..token = 't';
    final holder = OccupancyHolder();
    final container = ProviderContainer(
      overrides: [
        tokenStoreProvider.overrideWithValue(store),
        occupancyHolderProvider.overrideWithValue(holder),
        authRepositoryProvider.overrideWithValue(
          _FakeRepo(me: _me(ids: [1, 2])),
        ),
        occupancyStoreProvider.overrideWithValue(OccupancyStore()),
      ],
    );
    addTearDown(container.dispose);
    await container.read(sessionControllerProvider.future);
    expect(holder.occupancyId, isNull);
    final prefs = await SharedPreferences.getInstance();
    expect(prefs.getInt('lamto_occupancy_r@example.com'), isNull);
  });

  test('selectOccupancy invalidates occupancy-scoped providers', () async {
    SharedPreferences.setMockInitialValues({});
    final store = _FakeStore()..token = 't';
    final holder = OccupancyHolder();
    var scopedBuildCount = 0;
    final container = ProviderContainer(
      overrides: [
        tokenStoreProvider.overrideWithValue(store),
        occupancyHolderProvider.overrideWithValue(holder),
        authRepositoryProvider.overrideWithValue(
          _FakeRepo(me: _me(ids: [1, 2])),
        ),
        occupancyStoreProvider.overrideWithValue(OccupancyStore()),
        occupancyScopedProviders.overrideWith((ref) {
          scopedBuildCount++;
        }),
      ],
    );
    addTearDown(container.dispose);
    final me = _me(ids: [1, 2]);
    await container.read(sessionControllerProvider.future);
    container.read(occupancyScopedProviders); // build once
    final before = scopedBuildCount;
    await container
        .read(sessionControllerProvider.notifier)
        .selectOccupancy(me, 2);
    container.read(occupancyScopedProviders); // rebuild after invalidate
    expect(holder.occupancyId, 2);
    expect(scopedBuildCount, greaterThan(before));
  });

  test(
    'signIn then fetchMe network error -> SessionBootstrapError keeps token',
    () async {
      final store = _FakeStore();
      final repo = _FakeRepo(
        fetchError: _dio(null, type: DioExceptionType.connectionTimeout),
      );
      final container = ProviderContainer(
        overrides: [
          tokenStoreProvider.overrideWithValue(store),
          authRepositoryProvider.overrideWithValue(repo),
          occupancyStoreProvider.overrideWithValue(OccupancyStore()),
        ],
      );
      addTearDown(container.dispose);
      // Cold start: unauthenticated
      await container.read(sessionControllerProvider.future);
      await container
          .read(sessionControllerProvider.notifier)
          .signIn('r@example.com', 'pw');
      final state = container.read(sessionControllerProvider).value;
      expect(state, isA<SessionBootstrapError>());
      expect((state as SessionBootstrapError).failure.code, 'network_error');
      expect(store.token, 'tok'); // token retained for retry
    },
  );

  test('signIn then fetchMe 401 -> unauthenticated and clears token', () async {
    final store = _FakeStore();
    final repo = _FakeRepo(fetchError: _dio(401));
    final container = ProviderContainer(
      overrides: [
        tokenStoreProvider.overrideWithValue(store),
        authRepositoryProvider.overrideWithValue(repo),
        occupancyStoreProvider.overrideWithValue(OccupancyStore()),
      ],
    );
    addTearDown(container.dispose);
    await container.read(sessionControllerProvider.future);
    await expectLater(
      container
          .read(sessionControllerProvider.notifier)
          .signIn('r@example.com', 'pw'),
      throwsA(isA<DioException>()),
    );
    final state = container.read(sessionControllerProvider).value;
    expect(state, isA<SessionUnauthenticated>());
    expect(store.token, isNull);
  });

  test('signOut clears every report draft key (logout privacy)', () async {
    SharedPreferences.setMockInitialValues({});
    final draftStore = ReportDraftStore();
    await draftStore.write(
      1,
      ReportDraft.fresh().copyWith(text: 'sensitive a'),
    );
    await draftStore.write(
      2,
      ReportDraft.fresh().copyWith(text: 'sensitive b'),
    );

    final store = _FakeStore()..token = 't';
    final holder = OccupancyHolder()..occupancyId = 1;
    final container = ProviderContainer(
      overrides: [
        tokenStoreProvider.overrideWithValue(store),
        occupancyHolderProvider.overrideWithValue(holder),
        authRepositoryProvider.overrideWithValue(
          _FakeRepo(me: _me(occupancies: 1)),
        ),
        occupancyStoreProvider.overrideWithValue(OccupancyStore()),
        pushRegistrarProvider.overrideWithValue(_noopPushRegistrar),
      ],
    );
    addTearDown(container.dispose);
    await container.read(sessionControllerProvider.future);

    await container.read(sessionControllerProvider.notifier).signOut();

    expect(
      container.read(sessionControllerProvider).value,
      isA<SessionUnauthenticated>(),
    );
    expect(store.token, isNull);
    expect(holder.occupancyId, isNull);
    expect(await draftStore.read(1), isNull);
    expect(await draftStore.read(2), isNull);
    final prefs = await SharedPreferences.getInstance();
    expect(
      prefs.getKeys().where((k) => k.startsWith('lamto_report_draft_')),
      isEmpty,
    );
  });
}
