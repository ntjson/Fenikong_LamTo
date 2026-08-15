import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/theme.dart';

void main() {
  test('theme uses Accountability Indigo as primary', () {
    final theme = lamToTheme(Brightness.light);
    expect(theme.colorScheme.primary, LamToColors.primary);
    expect(theme.useMaterial3, isTrue);
  });

  test('dark theme has complete surface tokens', () {
    final theme = lamToTheme(Brightness.dark);
    expect(theme.colorScheme.surface, LamToColorsDark.surface);
    expect(theme.colorScheme.onSurface, LamToColorsDark.ink);
    expect(theme.colorScheme.outline, LamToColorsDark.border);
    expect(theme.scaffoldBackgroundColor, LamToColorsDark.bg);
    expect(theme.brightness, Brightness.dark);
  });

  test('dark filled buttons use Night Ground ink, not white (AA)', () {
    // White on dark-primary #8A97E8 is 2.74:1; the ink pair is ≈6.9:1.
    expect(
      lamToTheme(Brightness.dark).colorScheme.onPrimary,
      LamToColorsDark.onPrimary,
    );
    expect(LamToColorsDark.onPrimary, const Color(0xFF12141C));
    expect(
      lamToTheme(Brightness.light).colorScheme.onPrimary,
      LamToColors.onPrimary,
    );
  });

  test('iOS theme follows platform typography', () {
    final previous = debugDefaultTargetPlatformOverride;
    debugDefaultTargetPlatformOverride = TargetPlatform.iOS;
    try {
      final theme = lamToTheme(Brightness.light);
      expect(
        theme.textTheme.bodyMedium?.fontFamily,
        Typography.material2021(
          platform: TargetPlatform.iOS,
        ).black.bodyMedium?.fontFamily,
      );
    } finally {
      debugDefaultTargetPlatformOverride = previous;
    }
  });

  testWidgets('statusToneColors follows theme brightness', (tester) async {
    late BuildContext ctx;
    Widget probe(Brightness b) => MaterialApp(
      theme: lamToTheme(b),
      home: Builder(
        builder: (c) {
          ctx = c;
          return const SizedBox();
        },
      ),
    );

    await tester.pumpWidget(probe(Brightness.light));
    expect(statusToneColors(ctx, StatusTone.success).fg, LamToColors.success);

    await tester.pumpWidget(probe(Brightness.dark));
    // MaterialApp animates theme changes; settle so the dark theme applies.
    await tester.pumpAndSettle();
    expect(
      statusToneColors(ctx, StatusTone.success).fg,
      LamToColorsDark.success,
    );
  });

  test('moneyTextStyle uses tabular figures', () {
    final theme = lamToTheme(Brightness.light);
    final style = moneyTextStyle(theme.textTheme);
    expect(style.fontFeatures, contains(const FontFeature.tabularFigures()));
    expect(
      theme.textTheme.titleMedium?.fontFeatures,
      contains(const FontFeature.tabularFigures()),
    );
  });
}
