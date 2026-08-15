import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/features/documents/document_kind.dart';

Uint8List _bytes(List<int> leading) =>
    Uint8List.fromList([...leading, ...List.filled(64, 0)]);

final _pdf = _bytes('%PDF-1.7'.codeUnits);
final _png = _bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]);
final _jpeg = _bytes([0xFF, 0xD8, 0xFF, 0xE0]);
final _gif = _bytes('GIF89a'.codeUnits);
final _bmp = _bytes('BM'.codeUnits);
final _webp = _bytes([
  ...'RIFF'.codeUnits,
  0, 0, 0, 0, //
  ...'WEBP'.codeUnits,
]);
final _heic = _bytes([
  0, 0, 0, 0, //
  ...'ftyp'.codeUnits,
  ...'heic'.codeUnits,
]);
final _unknown = _bytes([0x01, 0x02, 0x03, 0x04]);

void main() {
  group('the content type selects the renderer', () {
    test('a PDF content type renders as a PDF', () {
      expect(
        detectDocumentKind(_pdf, 'application/pdf'),
        DocumentKind.pdf,
      );
    });

    test('an image content type renders as an image', () {
      expect(detectDocumentKind(_png, 'image/png'), DocumentKind.image);
    });

    test('the content type decides when the bytes say nothing', () {
      expect(detectDocumentKind(_unknown, 'application/pdf'), DocumentKind.pdf);
      expect(detectDocumentKind(_unknown, 'image/jpeg'), DocumentKind.image);
    });

    test('a content type with parameters is still read', () {
      expect(
        detectDocumentKind(_pdf, 'application/pdf; charset=binary'),
        DocumentKind.pdf,
      );
    });
  });

  group('the leading bytes override a disagreeing content type', () {
    test('image bytes labelled as a PDF render as an image', () {
      expect(detectDocumentKind(_png, 'application/pdf'), DocumentKind.image);
    });

    test('PDF bytes labelled as an image render as a PDF', () {
      expect(detectDocumentKind(_pdf, 'image/png'), DocumentKind.pdf);
    });

    test('bytes decide when nothing is declared', () {
      expect(detectDocumentKind(_pdf, null), DocumentKind.pdf);
      expect(detectDocumentKind(_jpeg, ''), DocumentKind.image);
    });
  });

  group('image signatures', () {
    test('the common resident-camera and scan formats are recognised', () {
      for (final bytes in [_png, _jpeg, _gif, _bmp, _webp, _heic]) {
        expect(detectDocumentKind(bytes, null), DocumentKind.image);
      }
    });
  });

  test('a PDF header behind leading junk is still found', () {
    // Readers tolerate a header that is not at byte zero; so does this.
    expect(
      detectDocumentKind(
        _bytes([0x0A, 0x20, ...'%PDF-1.4'.codeUnits]),
        null,
      ),
      DocumentKind.pdf,
    );
  });

  test('bytes and content type both silent is unsupported', () {
    expect(detectDocumentKind(_unknown, null), DocumentKind.unsupported);
    expect(
      detectDocumentKind(_unknown, 'application/octet-stream'),
      DocumentKind.unsupported,
    );
  });

  test('empty bytes with nothing declared are unsupported', () {
    expect(detectDocumentKind(Uint8List(0), null), DocumentKind.unsupported);
  });
}
