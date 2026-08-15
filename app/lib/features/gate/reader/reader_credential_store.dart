import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ReaderCredentialStore {
  ReaderCredentialStore([FlutterSecureStorage? storage])
    : _storage = storage ?? const FlutterSecureStorage();
  final FlutterSecureStorage _storage;
  Future<String?> read() => _storage.read(key: 'gate_reader_credential');
  Future<void> write(String value) =>
      _storage.write(key: 'gate_reader_credential', value: value);
  Future<void> clear() => _storage.delete(key: 'gate_reader_credential');
}
