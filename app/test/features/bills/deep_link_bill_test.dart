import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/features/notifications/deep_link.dart';

void main() {
  test('event key and push link map bill to DeepLinkBill', () {
    expect(parseEventKey('building.bill_issued:bill:7'), const DeepLinkBill(7));
    expect(parsePushLink(type: 'bill', id: '7'), const DeepLinkBill(7));
  });

  test('malformed and unknown bill links fall back to notifications', () {
    expect(
      parseEventKey('building.bill_issued:bill:not-an-id'),
      const DeepLinkFeed(),
    );
    expect(
      parseEventKey('building.bill_issued:unknown:7'),
      const DeepLinkFeed(),
    );
    expect(parsePushLink(type: 'bill', id: 'not-an-id'), const DeepLinkFeed());
    expect(parsePushLink(type: 'unknown', id: '7'), const DeepLinkFeed());
  });
}
