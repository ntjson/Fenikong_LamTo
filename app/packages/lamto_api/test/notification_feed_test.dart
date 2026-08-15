import 'package:test/test.dart';
import 'package:lamto_api/lamto_api.dart';

// tests for NotificationFeed
void main() {
  final instance = NotificationFeedBuilder();
  // TODO add properties to the builder and call build()

  group(NotificationFeed, () {
    // int id
    test('to test the property `id`', () async {
      // TODO
    });

    // String eventCode
    test('to test the property `eventCode`', () async {
      // TODO
    });

    // Deep-link reference '{code}:{entity}:{id}' (spec 6.3/7.4). Entity ids are resident-visible resources the API re-authorizes on fetch. Authorization-neutral and non-sensitive: codes/entity/ids only — no PII, bodies, or tokens.
    // String eventKey
    test('to test the property `eventKey`', () async {
      // TODO
    });

    // String subject
    test('to test the property `subject`', () async {
      // TODO
    });

    // String body
    test('to test the property `body`', () async {
      // TODO
    });

    // DateTime createdAt
    test('to test the property `createdAt`', () async {
      // TODO
    });

    // DateTime readAt
    test('to test the property `readAt`', () async {
      // TODO
    });

  });
}
