import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/features/gate/plate_text.dart';

void main() {
  test('normalizes plates', () {
    expect(normalizePlateText('51F-123.45'), '51F12345');
  });
  test('rejects unusable input', () {
    expect(normalizePlateText('!!!'), '');
    expect(isPlausiblePlate('51F'), false);
  });
}
