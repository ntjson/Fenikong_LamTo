import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/features/ledger/evidence_labels.dart';
import 'package:lamto/l10n/app_localizations.dart';
import 'package:lamto/theme.dart';

Future<AppLocalizations> _l10n(WidgetTester tester) async {
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
  return l10n;
}

void main() {
  testWidgets('the three levels get distinct copy; LOCAL never says chain', (
    tester,
  ) async {
    final l10n = await _l10n(tester);
    final chain = evidenceLevelLabel('CHAIN_CONFIRMED', l10n);
    final local = evidenceLevelLabel('LOCAL_SIGNED', l10n);
    final mismatch = evidenceLevelLabel('MISMATCH', l10n);
    expect({chain, local, mismatch}.length, 3); // all distinct
    expect(local.toLowerCase(), isNot(contains('đã neo'))); // spec 5.2
    expect(mismatch, 'Phát hiện sai lệch dữ liệu');
  });

  testWidgets('EvidenceBadge pairs color with text and marks mismatch error', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: const Locale('vi'),
        home: const Scaffold(
          body: Column(
            children: [
              EvidenceBadge(level: 'MISMATCH'),
              EvidenceBadge(level: 'LOCAL_SIGNED'),
            ],
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Phát hiện sai lệch dữ liệu'), findsOneWidget);
    final mismatchText = tester.widget<Text>(
      find.text('Phát hiện sai lệch dữ liệu'),
    );
    expect(mismatchText.style?.color, LamToColors.error); // prominent
  });
}
