import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/core/adaptive_buttons.dart';
import 'package:lamto/core/adaptive_scaffold.dart';
import 'package:lamto/core/page_body.dart';

void main() {
  testWidgets('iOS AdaptiveScaffold starts content below the nav bar', (
    tester,
  ) async {
    final previous = debugDefaultTargetPlatformOverride;
    debugDefaultTargetPlatformOverride = TargetPlatform.iOS;
    try {
      // Explicit-padding scrollables discard MediaQuery.padding, the exact
      // shape that used to hide the first ~90pt under the translucent bar.
      await tester.pumpWidget(
        MaterialApp(
          home: AdaptiveScaffold(
            title: 'Chi tiết',
            body: ListView(
              padding: const EdgeInsets.all(16),
              children: const [Text('first')],
            ),
          ),
        ),
      );
      final barBottom = tester
          .getBottomLeft(find.byType(CupertinoNavigationBar))
          .dy;
      expect(
        tester.getTopLeft(find.text('first')).dy,
        greaterThanOrEqualTo(barBottom),
      );
    } finally {
      debugDefaultTargetPlatformOverride = previous;
    }
  });

  testWidgets('busy filled button keeps its size and disables', (tester) async {
    for (final platform in [TargetPlatform.android, TargetPlatform.iOS]) {
      final previous = debugDefaultTargetPlatformOverride;
      debugDefaultTargetPlatformOverride = platform;
      try {
        Widget host(bool busy) => MaterialApp(
          home: Scaffold(
            body: Center(
              child: AdaptiveFilledButton(
                busy: busy,
                onPressed: () {},
                child: const Text('Gửi phản ánh'),
              ),
            ),
          ),
        );
        await tester.pumpWidget(host(false));
        final idle = tester.getSize(find.byType(AdaptiveFilledButton));
        expect(find.byType(CircularProgressIndicator), findsNothing);

        await tester.pumpWidget(host(true));
        // No width/height jump when the spinner replaces the label.
        expect(tester.getSize(find.byType(AdaptiveFilledButton)), idle);
        expect(find.byType(CircularProgressIndicator), findsOneWidget);
        if (platform == TargetPlatform.iOS) {
          expect(
            tester
                .widget<CupertinoButton>(find.byType(CupertinoButton))
                .enabled,
            isFalse,
          );
        } else {
          expect(
            tester.widget<FilledButton>(find.byType(FilledButton)).onPressed,
            isNull,
          );
        }
        // Leave no live spinner ticker behind for the next iteration.
        await tester.pumpWidget(host(false));
      } finally {
        debugDefaultTargetPlatformOverride = previous;
      }
    }
  });
  testWidgets('PageBody caps content width on wide screens', (tester) async {
    tester.view.physicalSize = const Size(1000, 700);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(body: PageBody(child: SizedBox.expand())),
      ),
    );
    expect(tester.getSize(find.byType(SizedBox)).width, 640);
  });

  Widget buttons() => MaterialApp(
    home: Scaffold(
      body: Column(
        children: [
          AdaptiveFilledButton(onPressed: () {}, child: const Text('primary')),
          AdaptiveFilledButton(
            tonal: true,
            onPressed: () {},
            icon: const Icon(Icons.star_outline),
            child: const Text('tonal'),
          ),
          AdaptiveOutlinedButton(onPressed: null, child: const Text('second')),
          AdaptiveTextButton(onPressed: () {}, child: const Text('tertiary')),
        ],
      ),
    ),
  );

  testWidgets('adaptive buttons speak Material on Android', (tester) async {
    final previous = debugDefaultTargetPlatformOverride;
    debugDefaultTargetPlatformOverride = TargetPlatform.android;
    try {
      await tester.pumpWidget(buttons());
      expect(find.widgetWithText(FilledButton, 'primary'), findsOneWidget);
      expect(find.widgetWithText(FilledButton, 'tonal'), findsOneWidget);
      expect(find.byIcon(Icons.star_outline), findsOneWidget);
      final second = tester.widget<OutlinedButton>(
        find.widgetWithText(OutlinedButton, 'second'),
      );
      expect(second.onPressed, isNull); // disabled passes through
      expect(find.widgetWithText(TextButton, 'tertiary'), findsOneWidget);
      expect(find.byType(CupertinoButton), findsNothing);
    } finally {
      debugDefaultTargetPlatformOverride = previous;
    }
  });

  testWidgets('adaptive buttons speak Cupertino on iOS', (tester) async {
    final previous = debugDefaultTargetPlatformOverride;
    debugDefaultTargetPlatformOverride = TargetPlatform.iOS;
    try {
      await tester.pumpWidget(buttons());
      expect(find.widgetWithText(CupertinoButton, 'primary'), findsOneWidget);
      expect(find.widgetWithText(CupertinoButton, 'tonal'), findsOneWidget);
      expect(find.byIcon(Icons.star_outline), findsOneWidget);
      final second = tester.widget<CupertinoButton>(
        find.widgetWithText(CupertinoButton, 'second'),
      );
      expect(second.enabled, isFalse); // disabled passes through
      expect(find.widgetWithText(CupertinoButton, 'tertiary'), findsOneWidget);
      expect(find.byType(FilledButton), findsNothing);
      expect(find.byType(OutlinedButton), findsNothing);
      expect(find.byType(TextButton), findsNothing);
      // 44pt iOS floor on every role.
      for (final label in ['primary', 'tonal', 'second', 'tertiary']) {
        expect(
          tester.getSize(find.widgetWithText(CupertinoButton, label)).height,
          greaterThanOrEqualTo(44),
        );
      }
    } finally {
      debugDefaultTargetPlatformOverride = previous;
    }
  });
}
