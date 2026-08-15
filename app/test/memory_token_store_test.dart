import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/core/token_store.dart';

void main() {
  test('TokenStore.memory read/write/clear without platform keyring', () async {
    final store = TokenStore.memory();
    expect(await store.read(), isNull);

    await store.write('knox-abc');
    expect(await store.read(), 'knox-abc');

    await store.clear();
    expect(await store.read(), isNull);
  });
}
