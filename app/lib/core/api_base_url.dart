import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'config.dart';

/// SharedPreferences key for the resident API base URL override.
const String kApiBaseUrlPrefsKey = 'api_base_url';

/// Compile-time default from `--dart-define=API_BASE_URL=...` (or emulator host).
String get defaultApiBaseUrl => apiBaseUrl;

/// Normalize a user-entered API base URL.
///
/// Returns `null` if the value is not an absolute http(s) URL with a host.
/// Trailing slashes are stripped so Dio path joins stay clean.
String? normalizeApiBaseUrl(String raw) {
  final trimmed = raw.trim();
  if (trimmed.isEmpty) return null;
  final uri = Uri.tryParse(trimmed);
  if (uri == null || !uri.hasScheme || !uri.hasAuthority) return null;
  if (uri.scheme != 'http' && uri.scheme != 'https') return null;
  if (uri.host.isEmpty) return null;
  var out = uri.toString();
  while (out.endsWith('/')) {
    out = out.substring(0, out.length - 1);
  }
  return out;
}

/// Runtime API base URL: prefs override, else [defaultApiBaseUrl].
///
/// Changing this rebuilds [dioProvider] so the next request hits the new host.
/// Prefer editing the URL while signed out (login screen); if changed while
/// signed in, call sites should invalidate the session.
class ApiBaseUrlNotifier extends Notifier<String> {
  @override
  String build() {
    Future.microtask(_hydrate);
    return defaultApiBaseUrl;
  }

  Future<void> _hydrate() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString(kApiBaseUrlPrefsKey);
    final normalized = saved == null ? null : normalizeApiBaseUrl(saved);
    if (normalized != null && normalized != state) {
      state = normalized;
    }
  }

  /// Persist [raw] as the API base URL. Throws [FormatException] if invalid.
  Future<void> setUrl(String raw) async {
    final normalized = normalizeApiBaseUrl(raw);
    if (normalized == null) {
      throw const FormatException('invalid_api_base_url');
    }
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(kApiBaseUrlPrefsKey, normalized);
    state = normalized;
  }

  /// Drop the override and return to the compile-time default.
  Future<void> clearOverride() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(kApiBaseUrlPrefsKey);
    state = defaultApiBaseUrl;
  }
}

final apiBaseUrlProvider = NotifierProvider<ApiBaseUrlNotifier, String>(
  ApiBaseUrlNotifier.new,
);
