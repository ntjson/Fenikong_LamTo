import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:lamto/features/documents/document_viewer_screen.dart';
import 'package:lamto/l10n/app_localizations.dart';
import 'package:pdfrx/pdfrx.dart';

/// Proves the document viewer really renders a PDF, which only a device build
/// can show: `flutter test` has no PDFium, so its widget tests can only prove
/// the viewer is opened, never that pages appear.
///
///   cd app && flutter test integration_test/document_viewer_test.dart -d linux
///
/// A minimal but valid single-page PDF, built inline so the test needs no
/// asset and no network.
Uint8List _onePagePdf() {
  final objects = <String>[
    '<</Type/Catalog/Pages 2 0 R>>',
    '<</Type/Pages/Kids[3 0 R]/Count 1>>',
    '<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 200]/Contents 4 0 R'
        '/Resources<</Font<</F1 5 0 R>>>>>>',
    '<</Length 44>>\nstream\nBT /F1 24 Tf 20 100 Td (LamTo) Tj ET\nendstream',
    '<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>',
  ];
  final buffer = StringBuffer('%PDF-1.4\n');
  final offsets = <int>[];
  for (var i = 0; i < objects.length; i++) {
    offsets.add(buffer.length);
    buffer.write('${i + 1} 0 obj\n${objects[i]}\nendobj\n');
  }
  final xref = buffer.length;
  buffer.write('xref\n0 ${objects.length + 1}\n0000000000 65535 f \n');
  for (final offset in offsets) {
    buffer.write('${offset.toString().padLeft(10, '0')} 00000 n \n');
  }
  buffer.write(
    'trailer\n<</Size ${objects.length + 1}/Root 1 0 R>>\n'
    'startxref\n$xref\n%%EOF\n',
  );
  return Uint8List.fromList(buffer.toString().codeUnits);
}

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('a PDF renders its pages inside the app', (tester) async {
    final controller = PdfViewerController();
    await tester.pumpWidget(
      MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: const Locale('vi'),
        home: DocumentViewerScreen(
          bytes: _onePagePdf(),
          filename: 'bao-gia.pdf',
          contentType: 'application/pdf',
          controller: controller,
        ),
      ),
    );

    // PDFium loads off the platform thread; give it real time to finish.
    final deadline = DateTime.now().add(const Duration(seconds: 20));
    while (!controller.isReady && DateTime.now().isBefore(deadline)) {
      await tester.pump(const Duration(milliseconds: 100));
    }

    expect(controller.isReady, isTrue, reason: 'The PDF never loaded.');
    expect(controller.pageCount, 1);
    expect(find.textContaining('Không xem trước được'), findsNothing);
  });
}
