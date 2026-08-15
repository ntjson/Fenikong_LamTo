import 'dart:async';
import 'dart:io' show Platform;

import 'package:shared_preferences/shared_preferences.dart';

import '../../core/uuid.dart';
import '../transparency/transparency_repository.dart';
import 'push_token_source.dart';

/// Stable per-install id (spec 7.2 upsert key). Never the auth token.
class InstallIdStore {
  InstallIdStore([SharedPreferences? prefs]) : _prefsOverride = prefs;
  final SharedPreferences? _prefsOverride;
  static const key = 'lamto_install_id';

  Future<SharedPreferences> _prefs() async =>
      _prefsOverride ?? await SharedPreferences.getInstance();

  Future<String> get() async {
    final prefs = await _prefs();
    final existing = prefs.getString(key);
    if (existing != null && existing.isNotEmpty) return existing;
    final minted = uuidV4();
    await prefs.setString(key, minted);
    return minted;
  }
}

/// SharedPreferences keys for push hygiene (A4 / A5).
abstract final class PushPrefsKeys {
  /// OS permission was requested once for this install (A4).
  static String permissionRequested(String installId) =>
      'push_permission_requested_$installId';

  /// Install id awaiting server deactivation after a failed logout deregister
  /// (A5).
  static const pendingDeregister = 'pending_device_deregister_install_id';
}

/// Client half of spec 7.2/7.5: consent-gated registration, token-refresh
/// re-registration, logout deactivation. Every path is best-effort.
///
/// **A4:** OS permission is requested only once per install (flag keyed by
/// install id). Later submits never re-prompt; register only when permission
/// was granted and a token is available.
///
/// **I1:** the permission-requested flag is set only when the OS was actually
/// consulted ([PushPermissionResult.granted] / [PushPermissionResult.denied]).
/// [PushPermissionResult.unsupported] (e.g. Firebase missing) does not burn
/// the flag so a later production build can still prompt.
///
/// **A5:** failed [deregister] persists [PushPrefsKeys.pendingDeregister] so
/// the next authenticated session can [retryPendingDeregister].
///
/// **I2:** [deregister] bounds the server deactivate call with a short timeout
/// so a stalled network never hangs logout; timeout → same pending path.
class PushRegistrar {
  PushRegistrar({
    required this.tokenSource,
    required this.repository,
    required this.installIdStore,
    SharedPreferences? prefs,
    Duration? deregisterTimeout,
  }) : _prefsOverride = prefs,
       deregisterTimeout =
           deregisterTimeout ?? PushRegistrar.defaultDeregisterTimeout;

  /// Bounds devicesDestroy so logout never hangs on a stalled Dio call (I2).
  static const defaultDeregisterTimeout = Duration(seconds: 8);

  final PushTokenSource tokenSource;
  final TransparencyRepository repository;
  final InstallIdStore installIdStore;
  final SharedPreferences? _prefsOverride;
  final Duration deregisterTimeout;
  StreamSubscription<String>? _refreshSub;

  Future<SharedPreferences> _prefs() async =>
      _prefsOverride ?? await SharedPreferences.getInstance();

  String get _platform {
    try {
      return Platform.isIOS ? 'IOS' : 'ANDROID';
    } catch (_) {
      return 'ANDROID';
    }
  }

  /// Ask OS permission once (in context, spec 7.5 + A4) and register.
  Future<void> registerAfterConsent() async {
    try {
      final installId = await installIdStore.get();
      final prefs = await _prefs();
      final requestedKey = PushPrefsKeys.permissionRequested(installId);
      final alreadyRequested = prefs.getBool(requestedKey) ?? false;

      if (!alreadyRequested) {
        final result = await tokenSource.requestPermission();
        switch (result) {
          case PushPermissionResult.unsupported:
            // OS never consulted — do not burn the once-per-install flag (I1).
            return;
          case PushPermissionResult.denied:
            await prefs.setBool(requestedKey, true);
            return;
          case PushPermissionResult.granted:
            await prefs.setBool(requestedKey, true);
        }
      }
      // Already requested: never re-prompt (A4). Proceed only if a token is
      // available (implies permission still useful for registration).
      await _registerWithCurrentToken(installId);
      watchTokenRefresh();
    } catch (_) {
      // Push failure never blocks any workflow (spec 7.4).
    }
  }

  /// After login / cold bootstrap: if this install already completed the
  /// OS permission moment, re-register the current FCM token and attach the
  /// refresh listener without re-prompting (spec 7.2; branch review Important).
  Future<void> ensureRegisteredIfConsented() async {
    try {
      final installId = await installIdStore.get();
      final prefs = await _prefs();
      final alreadyRequested =
          prefs.getBool(PushPrefsKeys.permissionRequested(installId)) ?? false;
      if (!alreadyRequested) return;
      await _registerWithCurrentToken(installId);
      watchTokenRefresh();
    } catch (_) {}
  }

  /// Ordered post-auth push hygiene (must not race):
  /// 1. A5: retry any pending logout deactivation first.
  /// 2. Spec 7.2: re-register if OS consent was already completed.
  /// 3. If pending was for **this** install and we re-registered, clear it —
  ///    the user is logged in again; a later deactivate must not land after
  ///    register and leave the install inactive.
  Future<void> onAuthenticatedSession() async {
    try {
      final installId = await installIdStore.get();
      final prefs = await _prefs();
      final pending = prefs.getString(PushPrefsKeys.pendingDeregister);

      // (1) Finish prior failed logout deactivation before any re-register.
      if (pending != null && pending.isNotEmpty) {
        try {
          await repository.deactivateDevice(pending).timeout(deregisterTimeout);
          await prefs.remove(PushPrefsKeys.pendingDeregister);
        } catch (_) {
          // Leave pending; re-register below may still succeed via upsert.
        }
      }

      // (2) Re-attach push without re-prompting when consent already happened.
      final alreadyRequested =
          prefs.getBool(PushPrefsKeys.permissionRequested(installId)) ?? false;
      if (alreadyRequested) {
        await _registerWithCurrentToken(installId);
        watchTokenRefresh();
        // (3) Same install re-authed: register upserted active — drop pending
        // so a stuck offline-logout key cannot deactivate after register.
        if (pending == installId) {
          await prefs.remove(PushPrefsKeys.pendingDeregister);
        }
      }
    } catch (_) {}
  }

  Future<void> _registerWithCurrentToken(String installId) async {
    final token = await tokenSource.getToken();
    if (token == null || token.isEmpty) return;
    await repository.registerDevice(
      installId: installId,
      fcmToken: token,
      platform: _platform,
    );
  }

  /// Re-register whenever FCM rotates the token (spec 7.2).
  void watchTokenRefresh() {
    _refreshSub ??= tokenSource.onTokenRefresh.listen((token) async {
      try {
        if (token.isEmpty) return;
        await repository.registerDevice(
          installId: await installIdStore.get(),
          fcmToken: token,
          platform: _platform,
        );
      } catch (_) {}
    });
  }

  /// Logout deactivates this install's device (spec 7.2 + A5). Best-effort:
  /// on failure or timeout (I2), persist a pending key for the next session.
  Future<void> deregister() async {
    await _refreshSub?.cancel();
    _refreshSub = null;
    final installId = await installIdStore.get();
    try {
      await repository.deactivateDevice(installId).timeout(deregisterTimeout);
      final prefs = await _prefs();
      await prefs.remove(PushPrefsKeys.pendingDeregister);
    } catch (_) {
      final prefs = await _prefs();
      await prefs.setString(PushPrefsKeys.pendingDeregister, installId);
    }
  }

  /// Retry a prior failed [deregister] (A5). No-op when nothing is pending.
  Future<void> retryPendingDeregister() async {
    try {
      final prefs = await _prefs();
      final pending = prefs.getString(PushPrefsKeys.pendingDeregister);
      if (pending == null || pending.isEmpty) return;
      await repository.deactivateDevice(pending).timeout(deregisterTimeout);
      await prefs.remove(PushPrefsKeys.pendingDeregister);
    } catch (_) {
      // Leave the pending key for a later authenticated session.
    }
  }
}
