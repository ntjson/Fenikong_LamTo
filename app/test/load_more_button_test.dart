import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/core/failure.dart';
import 'package:lamto/core/load_more_button.dart';
import 'package:lamto/l10n/app_localizations.dart';

Widget _wrap(Widget child) => MaterialApp(
  localizationsDelegates: AppLocalizations.localizationsDelegates,
  supportedLocales: AppLocalizations.supportedLocales,
  locale: const Locale('vi'),
  home: Scaffold(body: child),
);

void main() {
  testWidgets('disables while in flight — double tap loads one page', (
    tester,
  ) async {
    var calls = 0;
    final gate = Completer<void>();
    await tester.pumpWidget(
      _wrap(
        LoadMoreButton(
          label: 'Tải thêm',
          onLoadMore: () {
            calls++;
            return gate.future;
          },
        ),
      ),
    );
    await tester.tap(find.text('Tải thêm'));
    await tester.pump();
    // Busy keeps the label laid out (invisible under the spinner); tap the
    // button itself — the text is intentionally not hit-testable.
    final button = find.widgetWithText(OutlinedButton, 'Tải thêm');
    final busySize = tester.getSize(button);
    await tester.tap(button); // disabled: no second page
    await tester.pump();
    expect(calls, 1);
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    gate.complete();
    await tester.pumpAndSettle();
    // Stable geometry: the busy spinner never shifted the button's size.
    expect(tester.getSize(button), busySize);
  });

  testWidgets('failed page shows resident copy inline and retries', (
    tester,
  ) async {
    var calls = 0;
    await tester.pumpWidget(
      _wrap(
        LoadMoreButton(
          label: 'Tải thêm',
          onLoadMore: () async {
            calls++;
            if (calls == 1) throw Failure(code: 'network_error');
          },
        ),
      ),
    );
    await tester.tap(find.text('Tải thêm'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Không có kết nối'), findsOneWidget);

    await tester.tap(find.text('Tải thêm')); // button doubles as retry
    await tester.pumpAndSettle();
    expect(calls, 2);
    expect(find.textContaining('Không có kết nối'), findsNothing);
  });
}
