import 'package:test/test.dart';
import 'package:lamto_api/lamto_api.dart';

// tests for Problem
void main() {
  final instance = ProblemBuilder();
  // TODO add properties to the builder and call build()

  group(Problem, () {
    // Problem type URI reference; usually about:blank.
    // String type
    test('to test the property `type`', () async {
      // TODO
    });

    // Short human-readable summary (HTTP status phrase).
    // String title
    test('to test the property `title`', () async {
      // TODO
    });

    // HTTP status code.
    // int status
    test('to test the property `status`', () async {
      // TODO
    });

    // Stable machine code for client branching (e.g. validation_failed, authentication_failed, not_authenticated, permission_denied, not_found, occupancy_selection_required, throttled).
    // String code
    test('to test the property `code`', () async {
      // TODO
    });

    // Developer-English explanation; not shown raw to residents.
    // String detail
    test('to test the property `detail`', () async {
      // TODO
    });

    // Per-field validation errors when code is validation_failed. Values are lists of {message, code} objects (may nest for non-field errors).
    // BuiltMap<String, JsonObject> errors
    test('to test the property `errors`', () async {
      // TODO
    });

  });
}
