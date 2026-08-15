import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/features/gate/reader/reader_credential_store.dart';
import 'package:mocktail/mocktail.dart';

class MockSecureStorage extends Mock implements FlutterSecureStorage {}

void main() {
  test(
    'reader credential uses secure storage for read, write, and clear',
    () async {
      final storage = MockSecureStorage();
      when(
        () => storage.read(key: any(named: 'key')),
      ).thenAnswer((_) async => 'secret');
      when(
        () => storage.write(
          key: any(named: 'key'),
          value: any(named: 'value'),
        ),
      ).thenAnswer((_) async {});
      when(
        () => storage.delete(key: any(named: 'key')),
      ).thenAnswer((_) async {});
      final store = ReaderCredentialStore(storage);
      expect(await store.read(), 'secret');
      await store.write('new-secret');
      await store.clear();
      verify(
        () => storage.write(key: 'gate_reader_credential', value: 'new-secret'),
      ).called(1);
      verify(() => storage.delete(key: 'gate_reader_credential')).called(1);
    },
  );
}
