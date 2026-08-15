import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/features/auth/auth_repository.dart';

/// Contract tests: every hand/generated path constant must exist in OpenAPI.
void main() {
  late Set<String> openApiPaths;

  setUpAll(() {
    // Resolve schema relative to package root (app/) or monorepo root.
    final candidates = [
      File('../docs/api/openapi-v1.yaml'),
      File('docs/api/openapi-v1.yaml'),
      File('../../docs/api/openapi-v1.yaml'),
    ];
    final schema = candidates.firstWhere(
      (f) => f.existsSync(),
      orElse: () =>
          throw StateError('openapi-v1.yaml not found for contract tests'),
    );
    final text = schema.readAsStringSync();
    // Collect OpenAPI path keys under `paths:`.
    final paths = <String>{};
    final pathLine = RegExp(r'^  (/[^:]+):');
    var inPaths = false;
    for (final line in text.split('\n')) {
      if (line.startsWith('paths:')) {
        inPaths = true;
        continue;
      }
      if (inPaths && RegExp(r'^[a-zA-Z]').hasMatch(line)) {
        break; // next top-level key
      }
      if (inPaths) {
        final m = pathLine.firstMatch(line);
        if (m != null) paths.add(m.group(1)!);
      }
    }
    openApiPaths = paths;
    expect(openApiPaths, isNotEmpty);
  });

  test('login path exists in OpenAPI', () {
    expect(openApiPaths, contains(AuthApiPaths.login));
  });

  test('me path exists in OpenAPI', () {
    expect(openApiPaths, contains(AuthApiPaths.me));
  });
}
