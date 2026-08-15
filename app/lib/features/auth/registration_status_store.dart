import 'dart:convert';

import '../../core/token_store.dart';

class RegistrationStatusSecret {
  const RegistrationStatusSecret({required this.token, required this.phone});

  final String token;
  final String phone;

  @override
  bool operator ==(Object other) =>
      other is RegistrationStatusSecret &&
      other.token == token &&
      other.phone == phone;

  @override
  int get hashCode => Object.hash(token, phone);
}

class RegistrationStatusStore {
  RegistrationStatusStore(this._store);

  final TokenStore _store;

  Future<RegistrationStatusSecret?> read() async {
    final value = await _store.read();
    if (value == null) return null;

    try {
      final json = jsonDecode(value);
      if (json is! Map<String, dynamic> ||
          json.length != 2 ||
          json['token'] is! String ||
          json['phone'] is! String) {
        throw const FormatException('Invalid registration status');
      }
      return RegistrationStatusSecret(
        token: json['token'] as String,
        phone: json['phone'] as String,
      );
    } on FormatException {
      await clear();
      return null;
    }
  }

  Future<void> save(RegistrationStatusSecret secret) =>
      _store.write(jsonEncode({'token': secret.token, 'phone': secret.phone}));

  Future<void> clear() => _store.clear();
}
