import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/features/auth/auth_repository.dart';
import 'package:lamto/features/transparency/transparency_repository.dart';

void main() {
  late Set<String> openApiPaths;

  setUpAll(() {
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
    final paths = <String>{};
    final pathLine = RegExp(r'^  (/[^:]+):');
    var inPaths = false;
    for (final line in text.split('\n')) {
      if (line.startsWith('paths:')) {
        inPaths = true;
        continue;
      }
      if (inPaths && RegExp(r'^[a-zA-Z]').hasMatch(line)) break;
      if (inPaths) {
        final m = pathLine.firstMatch(line);
        if (m != null) paths.add(m.group(1)!);
      }
    }
    openApiPaths = paths;
    expect(openApiPaths, isNotEmpty);
  });

  test('all transparency path constants exist in OpenAPI', () {
    for (final path in [
      TransparencyApiPaths.ledger,
      TransparencyApiPaths.ledgerDetail,
      TransparencyApiPaths.fundSummary,
      TransparencyApiPaths.fundSeries,
      TransparencyApiPaths.notifications,
      TransparencyApiPaths.notificationRead,
      TransparencyApiPaths.devices,
      TransparencyApiPaths.deviceDelete,
      TransparencyApiPaths.mePreferences,
      AuthApiPaths.logout,
      AuthApiPaths.logoutAll,
    ]) {
      expect(openApiPaths, contains(path), reason: path);
    }
  });
}
