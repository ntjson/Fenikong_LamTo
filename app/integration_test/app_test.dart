import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:integration_test/integration_test.dart';
import 'package:lamto/app.dart';
import 'package:lamto/core/providers.dart';
import 'package:lamto/core/token_store.dart';

/// §6.5 happy path against a compose-seeded backend (run nightly on a device):
///
///   docker compose up -d              # repo root; then seed the pilot world
///   cd app && flutter test integration_test/app_test.dart \
///     --dart-define=API_BASE_URL=http://10.0.2.2:8000 \
///     --dart-define=INTEGRATION_IDENTIFIER=SEED_RESIDENT_EMAIL \
///     --dart-define=INTEGRATION_PASSWORD=SEED_PASSWORD
///
/// Pilot fixture defaults (from `manage.py seed_pilot --fixture`):
///   pilot-resident@pilot.lamto.test / pilot-test-secret
///
/// Token storage: this harness overrides [tokenStoreProvider] with
/// [TokenStore.memory] so headless Linux CI (no libsecret/keyring) can complete
/// login. Production apps still use platform secure storage via [TokenStore].
const _identifier = String.fromEnvironment('INTEGRATION_IDENTIFIER');
const _password = String.fromEnvironment('INTEGRATION_PASSWORD');

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('login -> home fund -> submit report -> my issues -> ledger',
      (tester) async {
    assert(_identifier.isNotEmpty && _password.isNotEmpty,
        'Pass INTEGRATION_IDENTIFIER / INTEGRATION_PASSWORD dart-defines.');

    await tester.pumpWidget(ProviderScope(
      overrides: [
        // Avoid flutter_secure_storage / libsecret on headless Linux runners.
        tokenStoreProvider.overrideWithValue(TokenStore.memory()),
      ],
      child: const LamToApp(),
    ));
    await tester.pumpAndSettle(const Duration(seconds: 2));

    // Login.
    await tester.enterText(find.byType(TextField).at(0), _identifier);
    await tester.enterText(find.byType(TextField).at(1), _password);
    await tester.tap(find.widgetWithText(FilledButton, 'Đăng nhập'));
    await tester.pumpAndSettle(const Duration(seconds: 5));

    // Home: fund block present (integer VND with dong sign).
    expect(find.text('Quỹ bảo trì'), findsOneWidget);
    expect(find.textContaining('₫'), findsWidgets);

    // Report tab: text + seeded location, submit without photos.
    await tester.tap(find.text('Phản ánh').last);
    await tester.pumpAndSettle();
    final reportText =
        'Kiểm thử tự động ${DateTime.now().millisecondsSinceEpoch}';
    await tester.enterText(find.byType(TextField).first, reportText);
    await tester.tap(find.text('Chọn vị trí'));
    await tester.pumpAndSettle(const Duration(seconds: 3));
    // Pick the first leaf row shown by the seeded location tree.
    await tester.tap(find.byType(ListTile).first);
    await tester.pumpAndSettle();
    await tester.tap(find.text('Gửi phản ánh'));
    await tester.pumpAndSettle(const Duration(seconds: 5));
    expect(find.text('Phản ánh của bạn đã được ghi nhận.'), findsOneWidget);

    // My Issues: the new report is listed.
    await tester.tap(find.text('Việc của tôi').last);
    await tester.pumpAndSettle(const Duration(seconds: 3));
    expect(find.textContaining('Kiểm thử tự động'), findsWidgets);

    // Ledger tab title (seeded world has fund; list may be empty).
    await tester.tap(find.text('Sổ quỹ').last);
    await tester.pumpAndSettle(const Duration(seconds: 3));
    expect(find.text('Sổ quỹ tòa nhà'), findsOneWidget);
  });
}
