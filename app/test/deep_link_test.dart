import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/features/notifications/deep_link.dart';

void main() {
  test('push data parses through the allowlist with safe fallback', () {
    expect(parsePushLink(type: 'report', id: '5'), DeepLinkReport(5));
    expect(parsePushLink(type: 'ledger', id: '42'), DeepLinkLedger(42));
    expect(parsePushLink(type: 'notifications', id: ''), const DeepLinkFeed());
    // A2: no resident Case detail — type case falls back to the feed.
    expect(parsePushLink(type: 'case', id: '3'), const DeepLinkFeed());
    expect(parsePushLink(type: 'evil', id: '1'), const DeepLinkFeed());
    expect(parsePushLink(type: 'report', id: 'abc'), const DeepLinkFeed());
    expect(parsePushLink(type: null, id: null), const DeepLinkFeed());
  });

  test('event keys parse entity segments with safe fallback', () {
    expect(parseEventKey('report.receipt:report:5'), DeepLinkReport(5));
    expect(parseEventKey('ledger.publication:entry:42'), DeepLinkLedger(42));
    // Corrections/cases/work have no resident screen of their own -> feed.
    expect(
      parseEventKey('correction.status:correction:7:PENDING'),
      const DeepLinkFeed(),
    );
    // A2: triage.status:case:… → feed (no Case detail screen).
    expect(parseEventKey('triage.status:case:3'), const DeepLinkFeed());
    expect(parseEventKey('work.update:work:9'), const DeepLinkFeed());
    expect(parseEventKey('garbage'), const DeepLinkFeed());
  });
}
