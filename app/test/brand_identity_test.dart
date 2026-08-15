import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/widgets/brand_identity.dart';

void main() {
  testWidgets('full identity exposes the product name without the tagline', (
    tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: BrandIdentity())),
    );

    expect(find.bySemanticsLabel('LÀM TỔ'), findsOneWidget);
    expect(find.bySemanticsLabel(RegExp('KẾT NỐI')), findsNothing);
  });
}
