import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../features/auth/auth_repository.dart';
import '../features/auth/registration_repository.dart';
import '../features/auth/registration_status_store.dart';
import '../features/auth/session_controller.dart';
import '../features/push/push_registrar.dart';
import '../features/push/push_token_source.dart';
import '../features/transparency/transparency_repository.dart';
import '../features/gate/gate_repository.dart';
import 'api_base_url.dart';
import 'api_client.dart';
import 'occupancy.dart';
import 'occupancy_store.dart';
import 'token_store.dart';

export 'api_base_url.dart';

final tokenStoreProvider = Provider<TokenStore>((ref) => TokenStore());
final registrationTokenStoreProvider = Provider<TokenStore>(
  (ref) => TokenStore(key: 'lamto_registration_status'),
);
final registrationStatusStoreProvider = Provider<RegistrationStatusStore>(
  (ref) => RegistrationStatusStore(ref.watch(registrationTokenStoreProvider)),
);
final occupancyHolderProvider = Provider<OccupancyHolder>(
  (ref) => OccupancyHolder(),
);
final occupancyStoreProvider = Provider<OccupancyStore>(
  (ref) => OccupancyStore(),
);

/// Feature providers that cache occupancy-scoped data MUST `ref.watch` this
/// so they rebuild when occupancy changes (clarification #2).
final occupancyScopedProviders = Provider<void>((ref) {});

/// True once the user has completed a successful sign-in or bootstrap in this
/// process; gates interceptor-driven session invalidation (review I2).
final sessionEstablishedProvider = Provider<bool>((ref) {
  final session = ref.watch(sessionControllerProvider);
  return switch (session) {
    AsyncData(:final value) => value is SessionAuthenticated,
    _ => false,
  };
});

final dioProvider = Provider<Dio>((ref) {
  final baseUrl = ref.watch(apiBaseUrlProvider);
  return buildDio(
    store: ref.watch(tokenStoreProvider),
    occupancy: ref.watch(occupancyHolderProvider),
    baseUrl: baseUrl,
    signalSessionLoss: () => ref.read(sessionEstablishedProvider),
    onUnauthorized: () => ref.invalidate(sessionControllerProvider),
  );
});

final authRepositoryProvider = Provider<AuthRepository>(
  (ref) => DioAuthRepository(ref.watch(dioProvider)),
);
final registrationRepositoryProvider = Provider<RegistrationRepository>(
  (ref) => RegistrationRepository(ref.watch(dioProvider)),
);
final gateRepositoryProvider = Provider<GateRepository>(
  (ref) => DioGateRepository(ref.watch(dioProvider)),
);

final pushTokenSourceProvider = Provider<PushTokenSource>(
  (ref) => FirebasePushTokenSource(),
);
final installIdStoreProvider = Provider<InstallIdStore>(
  (ref) => InstallIdStore(),
);
final pushRegistrarProvider = Provider<PushRegistrar>(
  (ref) => PushRegistrar(
    tokenSource: ref.watch(pushTokenSourceProvider),
    repository: ref.watch(transparencyRepositoryProvider),
    installIdStore: ref.watch(installIdStoreProvider),
  ),
);
