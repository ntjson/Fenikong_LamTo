import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/features/gate/reader/plate_ocr.dart';

void main() {
  test('selects shaped plate', () {
    expect(bestPlateFromLines(['GARAGE', '51F-123.45']), '51F12345');
  });
  test('joins motorbike lines', () {
    expect(
      bestPlateFromLines(['59X1', '999.99'], joinAdjacent: true),
      '59X199999',
    );
  });
  test('returns null without a candidate', () {
    expect(bestPlateFromLines(['WELCOME']), null);
  });
}
