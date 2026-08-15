import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/core/token_store.dart';
import 'package:lamto/features/auth/registration_status_store.dart';

void main() {
  const key = 'lamto_registration_status';

  test('stores status token and phone in the registration slot', () async {
    final memory = <String, String>{};
    final store = RegistrationStatusStore(
      TokenStore.memory(key: key, memory: memory),
    );

    await store.save(
      const RegistrationStatusSecret(
        token: 'opaque-token',
        phone: '+84901234567',
      ),
    );

    final reconstructed = RegistrationStatusStore(
      TokenStore.memory(key: key, memory: memory),
    );
    expect(
      await reconstructed.read(),
      const RegistrationStatusSecret(
        token: 'opaque-token',
        phone: '+84901234567',
      ),
    );
    expect(memory[key], '{"token":"opaque-token","phone":"+84901234567"}');
  });

  test('malformed status is cleared and returns null', () async {
    final memory = <String, String>{key: '{"token": 1}'};
    final store = RegistrationStatusStore(
      TokenStore.memory(key: key, memory: memory),
    );

    expect(await store.read(), isNull);
    expect(memory, isNot(contains(key)));
  });

  test(
    'clear removes registration status without changing auth token',
    () async {
      final memory = <String, String>{};
      final authStore = TokenStore.memory(memory: memory);
      final registrationStore = RegistrationStatusStore(
        TokenStore.memory(key: key, memory: memory),
      );
      await authStore.write('auth-token');
      await registrationStore.save(
        const RegistrationStatusSecret(token: 'status-token', phone: '+84'),
      );

      await registrationStore.clear();

      expect(await authStore.read(), 'auth-token');
      expect(await registrationStore.read(), isNull);
    },
  );
}
