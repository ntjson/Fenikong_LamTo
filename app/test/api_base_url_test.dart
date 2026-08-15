import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/core/api_base_url.dart';

void main() {
  group('normalizeApiBaseUrl', () {
    test('accepts https tunnel and strips trailing slash', () {
      expect(
        normalizeApiBaseUrl(
          ' https://jurisdiction-photographer-absence-mystery.trycloudflare.com/ ',
        ),
        'https://jurisdiction-photographer-absence-mystery.trycloudflare.com',
      );
    });

    test('accepts emulator host', () {
      expect(
        normalizeApiBaseUrl('http://10.0.2.2:8000'),
        'http://10.0.2.2:8000',
      );
    });

    test('rejects empty and non-http schemes', () {
      expect(normalizeApiBaseUrl(''), isNull);
      expect(normalizeApiBaseUrl('ftp://x'), isNull);
      expect(normalizeApiBaseUrl('not a url'), isNull);
    });
  });
}
