import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/core/uuid.dart';

void main() {
  test('uuidV4 shape, version, variant, uniqueness', () {
    final re = RegExp(
      r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    );
    final seen = <String>{};
    for (var i = 0; i < 200; i++) {
      final id = uuidV4();
      expect(re.hasMatch(id), isTrue, reason: id);
      expect(seen.add(id), isTrue);
    }
  });
}
