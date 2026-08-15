import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/features/bills/bill_qr.dart';

void main() {
  test('extracts reference from a LamTo bill QR', () {
    expect(billReferenceFromQr('lamto-bill:abc123'), 'abc123');
  });

  test('rejects non-LamTo QR payloads', () {
    expect(billReferenceFromQr('https://example.test'), isNull);
    expect(billReferenceFromQr('lamto-bill:'), isNull);
  });
}
