import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lamto/features/reports/location_picker_screen.dart';
import 'package:lamto/features/reports/reports_repository.dart';
import 'package:lamto/l10n/app_localizations.dart';
import 'package:lamto_api/lamto_api.dart';

Location _loc(int id, String name, {int? parent}) => Location(
  (b) => b
    ..id = id
    ..name = name
    ..parentId = parent,
);

Future<Location?> _open(WidgetTester tester, List<Location> locations) async {
  Location? picked;
  await tester.pumpWidget(
    ProviderScope(
      overrides: [locationsProvider.overrideWith((ref) async => locations)],
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: const Locale('vi'),
        home: Builder(
          builder: (context) => ElevatedButton(
            onPressed: () async {
              picked = await Navigator.push<Location>(
                context,
                MaterialPageRoute(builder: (_) => const LocationPickerScreen()),
              );
            },
            child: const Text('open'),
          ),
        ),
      ),
    ),
  );
  await tester.tap(find.text('open'));
  await tester.pumpAndSettle();
  return picked;
}

void main() {
  testWidgets('leaf tap pops with the location', (tester) async {
    await _open(tester, [_loc(1, 'Sảnh')]);
    await tester.tap(find.text('Sảnh'));
    await tester.pumpAndSettle();
    // Popped back to the host screen.
    expect(find.text('open'), findsOneWidget);
  });

  testWidgets('parent drills down and "choose this area" selects it', (
    tester,
  ) async {
    await _open(tester, [_loc(1, 'Tòa A'), _loc(2, 'Thang máy 2', parent: 1)]);
    await tester.tap(find.text('Tòa A'));
    await tester.pumpAndSettle();
    expect(find.text('Thang máy 2'), findsOneWidget);
    expect(find.text('Chọn khu vực này'), findsOneWidget);
    await tester.tap(find.text('Chọn khu vực này'));
    await tester.pumpAndSettle();
    expect(find.text('open'), findsOneWidget);
  });
}
