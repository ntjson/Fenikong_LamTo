import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Knox token storage (spec 3.2) — never plain SharedPreferences.
///
/// Production: platform keystore via [FlutterSecureStorage].
/// Integration / headless CI: [TokenStore.memory] avoids libsecret/keyring.
class TokenStore {
  TokenStore({FlutterSecureStorage? storage, this._key = 'lamto_auth_token'})
    : _storage =
          storage ??
          const FlutterSecureStorage(
            aOptions: AndroidOptions.defaultOptions,
            iOptions: IOSOptions(
              accessibility: KeychainAccessibility.first_unlock,
            ),
          ),
      _memory = null;

  /// In-memory token for `integration_test` and headless Linux CI.
  /// Production apps must use the default constructor (secure storage).
  TokenStore.memory({
    this._key = 'lamto_auth_token',
    Map<String, String>? memory,
  }) : _storage = null,
       _memory = memory ?? <String, String>{};

  final FlutterSecureStorage? _storage;
  final String _key;
  final Map<String, String>? _memory;

  Future<String?> read() async {
    final mem = _memory;
    if (mem != null) return mem[_key];
    return _storage!.read(key: _key);
  }

  Future<void> write(String value) async {
    final mem = _memory;
    if (mem != null) {
      mem[_key] = value;
      return;
    }
    await _storage!.write(key: _key, value: value);
  }

  Future<void> clear() async {
    final mem = _memory;
    if (mem != null) {
      mem.remove(_key);
      return;
    }
    await _storage!.delete(key: _key);
  }
}
