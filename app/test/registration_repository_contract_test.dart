import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  late String schema;

  setUpAll(() {
    final candidates = [
      File('../docs/api/openapi-v1.yaml'),
      File('docs/api/openapi-v1.yaml'),
      File('../../docs/api/openapi-v1.yaml'),
    ];
    schema = candidates
        .firstWhere(
          (file) => file.existsSync(),
          orElse: () => throw StateError('openapi-v1.yaml not found'),
        )
        .readAsStringSync();
  });

  test('registration API contract exposes the generated paths and header', () {
    expect(schema, contains('  /api/v1/registration-requests:'));
    expect(schema, contains('  /api/v1/registration-requests/status:'));
    expect(schema, contains('  /api/v1/registration/options:'));
    expect(schema, contains('        name: X-Registration-Status-Token'));
  });
}
