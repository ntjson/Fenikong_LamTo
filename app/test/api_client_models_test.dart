import 'package:flutter_test/flutter_test.dart';
import 'package:lamto_api/lamto_api.dart';

void main() {
  test('generated TokenResponse deserializes via standardSerializers', () {
    final token = standardSerializers.deserializeWith(
      TokenResponse.serializer,
      {'token': 'abc', 'expiry': '2026-08-01T00:00:00Z'},
    );
    expect(token!.token, 'abc');
  });

  test('generated Me deserializes with occupancies', () {
    final me = standardSerializers.deserializeWith(Me.serializer, {
      'display_name': 'R',
      'email': 'r@example.com',
      'phone': null,
      'occupancies': [
        {'id': 1, 'unit_label': 'A-1', 'building_name': 'Toa A'},
      ],
      'notification_preferences': [],
    });
    expect(me!.displayName, 'R');
    expect(me.occupancies.first.id, 1);
  });
}
