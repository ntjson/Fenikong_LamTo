import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/features/documents/document_viewer_screen.dart';
import 'package:lamto/l10n/app_localizations.dart';
import 'package:pdfrx/pdfrx.dart';

import 'document_fixtures.dart';
import 'fake_share_platform.dart';

/// `flutter test` has no PDFium, so these assert which renderer the viewer
/// chooses and what it shows when it cannot draw — not that PDF pages paint.
/// Painting is asserted on a device in integration_test/document_viewer_test.dart.
Widget _host(
  Uint8List bytes, {
  String filename = 'tai-lieu',
  String? contentType,
}) => MaterialApp(
  localizationsDelegates: AppLocalizations.localizationsDelegates,
  supportedLocales: AppLocalizations.supportedLocales,
  locale: const Locale('vi'),
  home: DocumentViewerScreen(
    bytes: bytes,
    filename: filename,
    contentType: contentType,
  ),
);

const _unreadable = 'Không xem trước được tệp này';

late FakeSharePlatform share;

void main() {
  setUpAll(() => share = FakeSharePlatform.install());
  setUp(() => share.reset());

  testWidgets('a PDF opens in the PDF renderer', (tester) async {
    await tester.pumpWidget(_host(minimalPdfBytes, contentType: 'application/pdf'));
    await tester.pump();

    expect(find.byType(PdfViewer), findsOneWidget);
    expect(find.byType(Image), findsNothing);
    expect(find.textContaining(_unreadable), findsNothing);
  });

  testWidgets('an image opens in the image renderer', (tester) async {
    await tester.pumpWidget(_host(onePixelPngBytes, contentType: 'image/png'));
    await tester.pumpAndSettle();

    expect(find.byType(Image), findsOneWidget);
    expect(find.byType(PdfViewer), findsNothing);
    expect(find.textContaining(_unreadable), findsNothing);
  });

  testWidgets('mislabelled bytes render by what they are, not what they claim', (
    tester,
  ) async {
    // A PDF content type over image bytes, and the reverse: the bytes win.
    await tester.pumpWidget(_host(onePixelPngBytes, contentType: 'application/pdf'));
    await tester.pumpAndSettle();
    expect(find.byType(Image), findsOneWidget);
    expect(find.byType(PdfViewer), findsNothing);

    await tester.pumpWidget(_host(minimalPdfBytes, contentType: 'image/png'));
    await tester.pump();
    expect(find.byType(PdfViewer), findsOneWidget);
    expect(find.byType(Image), findsNothing);
  });

  testWidgets('the filename extension is never consulted', (tester) async {
    // Named .pdf, declared nothing, and image bytes: still the image renderer.
    await tester.pumpWidget(_host(onePixelPngBytes, filename: 'bao-gia.pdf'));
    await tester.pumpAndSettle();
    expect(find.byType(Image), findsOneWidget);
    expect(find.byType(PdfViewer), findsNothing);

    // And the reverse: a .png name over PDF bytes stays a PDF.
    await tester.pumpWidget(_host(minimalPdfBytes, filename: 'chung-tu.png'));
    await tester.pump();
    expect(find.byType(PdfViewer), findsOneWidget);
  });

  testWidgets('a render failure is shown in the viewer, share still offered', (
    tester,
  ) async {
    await tester.pumpWidget(
      _host(brokenPngBytes, contentType: 'image/png'),
    );
    await tester.pumpAndSettle();

    expect(find.textContaining(_unreadable), findsOneWidget);
    expect(find.byTooltip('Chia sẻ hoặc lưu'), findsOneWidget);
  });

  testWidgets('a file LamTo cannot draw is not a dead end', (tester) async {
    await tester.pumpWidget(
      _host(
        Uint8List.fromList(List.filled(32, 0x01)),
        contentType: 'application/zip',
      ),
    );
    await tester.pumpAndSettle();

    expect(find.textContaining(_unreadable), findsOneWidget);
    expect(find.byTooltip('Chia sẻ hoặc lưu'), findsOneWidget);
  });

  testWidgets('a PDF the engine refuses shows the same in-viewer failure', (
    tester,
  ) async {
    // PDFium cannot load here, so the engine's failure path is driven
    // directly: this asserts the viewer's own banner replaces pdfrx's
    // developer diagnostic, which is the part LamTo owns.
    await tester.pumpWidget(
      _host(minimalPdfBytes, contentType: 'application/pdf'),
    );
    await tester.pump();

    final viewer = tester.widget<PdfViewer>(find.byType(PdfViewer));
    final banner = viewer.params.errorBannerBuilder;
    expect(banner, isNotNull, reason: 'pdfrx would show its own banner.');

    await tester.pumpWidget(
      MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: const Locale('vi'),
        home: Builder(
          builder: (context) =>
              banner!(context, StateError('broken'), null, viewer.documentRef),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.textContaining(_unreadable), findsOneWidget);
  });

  testWidgets('a refused share is said out loud, over the open document', (
    tester,
  ) async {
    share.failure = StateError('no share target');
    await tester.pumpWidget(
      _host(onePixelPngBytes, contentType: 'image/png'),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.byTooltip('Chia sẻ hoặc lưu'));
    await tester.pumpAndSettle();

    expect(find.textContaining('Chưa chia sẻ được tệp'), findsOneWidget);
    // Reading is unaffected: the document is still on screen.
    expect(find.byType(Image), findsOneWidget);
  });

  testWidgets('sharing hands the document to the OS on request', (
    tester,
  ) async {
    await tester.pumpWidget(_host(onePixelPngBytes, contentType: 'image/png'));
    await tester.pumpAndSettle();

    expect(share.shared, isEmpty, reason: 'Opening must not share by itself.');

    await tester.tap(find.byTooltip('Chia sẻ hoặc lưu'));
    await tester.pumpAndSettle();

    expect(share.shared, hasLength(1));
    // The bytes go across as data under the document's own name; share_plus
    // stages the temporary file, so LamTo writes nothing itself.
    expect(share.shared.single.fileNameOverrides, ['tai-lieu']);
    expect(await share.shared.single.files?.single.readAsBytes(), onePixelPngBytes);
  });
}
