import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lamto_api/lamto_api.dart';

import '../../core/failure.dart';
import '../../core/occupancy.dart';
import '../../core/occupancy_store.dart';
import '../../core/providers.dart';
import '../../core/token_store.dart';
import '../reports/report_draft.dart';
import '../reports/report_photo_files.dart';
import 'auth_repository.dart';

sealed class SessionState {
  const SessionState();
}

class SessionUnauthenticated extends SessionState {
  const SessionUnauthenticated();
}

class SessionAuthenticated extends SessionState {
  const SessionAuthenticated(this.me);
  final Me me;
}

/// Retryable bootstrap failure — never route this to Login (clarification #1).
class SessionBootstrapError extends SessionState {
  const SessionBootstrapError(this.failure);
  final Failure failure;
}

class SessionController extends AsyncNotifier<SessionState> {
  AuthRepository get _repo => ref.read(authRepositoryProvider);
  TokenStore get _store => ref.read(tokenStoreProvider);
  OccupancyHolder get _holder => ref.read(occupancyHolderProvider);
  OccupancyStore get _occupancyStore => ref.read(occupancyStoreProvider);

  @override
  Future<SessionState> build() => _bootstrap();

  Future<SessionState> _bootstrap() async {
    // 1. Secure storage first.
    final token = await _store.read();
    if (token == null || token.isEmpty) {
      return const SessionUnauthenticated();
    }

    try {
      final me = await _repo.fetchMe();
      await _restoreOccupancy(me);
      _schedulePendingDeregisterRetry();
      return SessionAuthenticated(me);
    } on DioException catch (e) {
      final failure = Failure.fromDio(e);
      final isAuth =
          e.response?.statusCode == 401 ||
          failure.code == 'authentication_failed' ||
          failure.code == 'not_authenticated';
      if (isAuth) {
        await _store.clear();
        return const SessionUnauthenticated();
      }
      return SessionBootstrapError(failure);
    } catch (_) {
      return SessionBootstrapError(Failure(code: 'schema_error'));
    }
  }

  /// After auth: ordered push hygiene via [PushRegistrar.onAuthenticatedSession]
  /// (await pending deregister **then** re-register if consented — never race
  /// deactivate after register for the same install_id).
  void _schedulePendingDeregisterRetry() {
    unawaited(
      ref
          .read(pushRegistrarProvider)
          .onAuthenticatedSession()
          .catchError((Object _) {}),
    );
  }

  Future<void> _restoreOccupancy(Me me) async {
    final userKey = _userKey(me);
    final stored = await _occupancyStore.read(userKey);
    if (stored != null && me.occupancies.any((o) => o.id == stored)) {
      _holder.occupancyId = stored;
      return;
    }
    if (stored != null) {
      await _occupancyStore.clear(userKey);
    }
    if (me.occupancies.length == 1) {
      final id = me.occupancies.first.id;
      _holder.occupancyId = id;
      await _occupancyStore.write(userKey, id);
    } else {
      _holder.occupancyId = null;
    }
  }

  String _userKey(Me me) {
    final email = me.email;
    if (email != null && email.isNotEmpty) return email;
    final phone = me.phone;
    if (phone != null && phone.isNotEmpty) return phone;
    return 'install';
  }

  /// Login then bootstrap /me. After the knox token is written, a transient
  /// /me failure becomes [SessionBootstrapError] (retryable) — never leave a
  /// valid token while the UI still shows only Login (review M8).
  Future<void> signIn(String identifier, String password) async {
    final token = await _repo.login(identifier, password);
    await _store.write(token);
    try {
      final me = await _repo.fetchMe();
      await _restoreOccupancy(me);
      state = AsyncData(SessionAuthenticated(me));
      _schedulePendingDeregisterRetry();
    } on DioException catch (e) {
      final failure = Failure.fromDio(e);
      final isAuth =
          e.response?.statusCode == 401 ||
          failure.code == 'authentication_failed' ||
          failure.code == 'not_authenticated';
      if (isAuth) {
        await _store.clear();
        state = const AsyncData(SessionUnauthenticated());
        rethrow;
      }
      // Token retained; router shows retry — same taxonomy as cold bootstrap.
      state = AsyncData(SessionBootstrapError(failure));
    } catch (_) {
      state = AsyncData(SessionBootstrapError(Failure(code: 'schema_error')));
    }
  }

  Future<void> signOut({bool allDevices = false}) async {
    // Deactivate this install's push device first (spec 7.2 + A5); best-effort.
    // Failed deregister persists pending_device_deregister_install_id for retry.
    try {
      await ref.read(pushRegistrarProvider).deregister();
    } catch (_) {}
    // Server-side revocation is best-effort: a network failure must never
    // trap the resident in a session (spec 6.4).
    try {
      allDevices ? await _repo.logoutAll() : await _repo.logout();
    } catch (_) {}
    await _store.clear();
    _holder.occupancyId = null;
    // Amendment 7: wipe sensitive draft text/paths on logout.
    await ReportDraftStore().clearAll();
    // Amendment 8: drop app-owned photo copies. path_provider may be
    // unavailable or hang in widget tests — never block session clear.
    unawaited(ReportPhotoFileStore().clearAll().catchError((Object _) {}));
    // My Issues watches sessionControllerProvider and rebuilds on this state.
    state = const AsyncData(SessionUnauthenticated());
  }

  /// Persist selection, update holder, clear occupancy-scoped providers.
  Future<void> selectOccupancy(Me me, int occupancyId) async {
    final previous = _holder.occupancyId;
    _holder.occupancyId = occupancyId;
    await _occupancyStore.write(_userKey(me), occupancyId);
    if (previous != occupancyId) {
      ref.invalidate(occupancyScopedProviders);
    }
  }
}

final sessionControllerProvider =
    AsyncNotifierProvider<SessionController, SessionState>(
      SessionController.new,
    );
