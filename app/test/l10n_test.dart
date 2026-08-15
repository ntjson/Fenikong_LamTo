import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/core/failure.dart';
import 'package:lamto/l10n/app_localizations.dart';

void main() {
  testWidgets('Vietnamese failure copy is used and mentions save state', (
    tester,
  ) async {
    late AppLocalizations l10n;
    await tester.pumpWidget(
      MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: const Locale('vi'),
        home: Builder(
          builder: (context) {
            l10n = AppLocalizations.of(context)!;
            return const SizedBox();
          },
        ),
      ),
    );
    expect(
      failureMessage(Failure(code: 'throttled'), l10n),
      contains('Chưa có gì được gửi'),
    );
    expect(l10n.loginSubmit, 'Đăng nhập');
    expect(
      failureMessage(Failure(code: 'network_error'), l10n),
      isNot(contains('HTTP')),
    );
    expect(
      failureMessage(Failure(code: 'network_error'), l10n),
      isNot(contains('401')),
    );
  });
}
