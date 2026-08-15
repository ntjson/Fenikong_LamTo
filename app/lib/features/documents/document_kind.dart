import 'dart:typed_data';

/// What the document viewer can draw.
enum DocumentKind { pdf, image, unsupported }

/// How far into a file a PDF header is still accepted. Readers tolerate a
/// header that is not at byte zero, and a document LamTo refuses to draw but
/// every other reader opens would read as LamTo's failure.
const _pdfHeaderSearchWindow = 1024;

/// Chooses the renderer for a downloaded document.
///
/// The stored [contentType] from the API is the declaration; the leading bytes
/// are the fact, and override it when the two disagree, so a mislabelled
/// record renders instead of blanking. The filename is deliberately not a
/// parameter: an extension is upload data the uploader chose, and choosing a
/// renderer from it would let an upload decide how it is parsed.
DocumentKind detectDocumentKind(Uint8List bytes, String? contentType) {
  final sniffed = _kindFromBytes(bytes);
  if (sniffed != DocumentKind.unsupported) return sniffed;
  return _kindFromContentType(contentType);
}

DocumentKind _kindFromContentType(String? contentType) {
  // Parameters ride along on stored content types ("application/pdf; qs=0.9").
  final declared = (contentType ?? '').split(';').first.trim().toLowerCase();
  if (declared == 'application/pdf' || declared == 'application/x-pdf') {
    return DocumentKind.pdf;
  }
  if (declared.startsWith('image/')) return DocumentKind.image;
  return DocumentKind.unsupported;
}

DocumentKind _kindFromBytes(Uint8List bytes) {
  if (_hasPdfHeader(bytes)) return DocumentKind.pdf;
  if (_hasImageHeader(bytes)) return DocumentKind.image;
  return DocumentKind.unsupported;
}

bool _startsWith(Uint8List bytes, List<int> signature, {int offset = 0}) {
  if (bytes.length < offset + signature.length) return false;
  for (var i = 0; i < signature.length; i++) {
    if (bytes[offset + i] != signature[i]) return false;
  }
  return true;
}

bool _hasPdfHeader(Uint8List bytes) {
  const header = [0x25, 0x50, 0x44, 0x46]; // %PDF
  final limit = bytes.length < _pdfHeaderSearchWindow
      ? bytes.length
      : _pdfHeaderSearchWindow;
  for (var start = 0; start + header.length <= limit; start++) {
    if (_startsWith(bytes, header, offset: start)) return true;
  }
  return false;
}

bool _hasImageHeader(Uint8List bytes) {
  const png = [0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A];
  const jpeg = [0xFF, 0xD8, 0xFF];
  const gif87 = [0x47, 0x49, 0x46, 0x38, 0x37, 0x61]; // GIF87a
  const gif89 = [0x47, 0x49, 0x46, 0x38, 0x39, 0x61]; // GIF89a
  const bmp = [0x42, 0x4D]; // BM
  if (_startsWith(bytes, png) ||
      _startsWith(bytes, jpeg) ||
      _startsWith(bytes, gif87) ||
      _startsWith(bytes, gif89) ||
      _startsWith(bytes, bmp)) {
    return true;
  }
  // RIFF containers carry their format at byte 8; only WEBP is an image.
  const riff = [0x52, 0x49, 0x46, 0x46];
  const webp = [0x57, 0x45, 0x42, 0x50];
  if (_startsWith(bytes, riff) && _startsWith(bytes, webp, offset: 8)) {
    return true;
  }
  // ISO base-media files (HEIC, AVIF) name their brand after the ftyp box.
  const ftyp = [0x66, 0x74, 0x79, 0x70];
  if (_startsWith(bytes, ftyp, offset: 4) && bytes.length >= 12) {
    final brand = String.fromCharCodes(bytes.sublist(8, 12)).toLowerCase();
    return const {
      'heic',
      'heix',
      'hevc',
      'hevx',
      'mif1',
      'msf1',
      'avif',
      'avis',
    }.contains(brand);
  }
  return false;
}
