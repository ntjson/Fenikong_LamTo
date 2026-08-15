import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/features/transparency/transparency_repository.dart';
import 'package:mocktail/mocktail.dart';

class _MockAdapter extends Mock implements HttpClientAdapter {}

ResponseBody _json(int status, Object body) => ResponseBody.fromString(
  jsonEncode(body),
  status,
  headers: {
    Headers.contentTypeHeader: [Headers.jsonContentType],
  },
);

void main() {
  setUpAll(() => registerFallbackValue(RequestOptions(path: '/')));

  late _MockAdapter adapter;
  late DioTransparencyRepository repo;
  late RequestOptions lastRequest;

  setUp(() {
    adapter = _MockAdapter();
    final dio = Dio(BaseOptions(baseUrl: 'http://x'));
    dio.httpClientAdapter = adapter;
    repo = DioTransparencyRepository(dio);
  });

  void answerWith(int status, Object body) {
    when(() => adapter.fetch(any(), any(), any())).thenAnswer((inv) async {
      lastRequest = inv.positionalArguments[0] as RequestOptions;
      return _json(status, body);
    });
  }

  test('listLedger passes year/month/cursor query params', () async {
    answerWith(200, {'next': null, 'previous': null, 'results': []});
    await repo.listLedger(year: 2026, month: 7, cursor: 'abc');
    expect(lastRequest.path, '/api/v1/ledger');
    expect(lastRequest.queryParameters['year'], 2026);
    expect(lastRequest.queryParameters['month'], 7);
    expect(lastRequest.queryParameters['cursor'], 'abc');
  });

  test('updatePreference PATCHes one item and parses the list', () async {
    answerWith(200, [
      {
        'event_code': 'ledger.publication',
        'email_enabled': true,
        'push_enabled': false,
      },
    ]);
    final prefs = await repo.updatePreference(
      eventCode: 'ledger.publication',
      pushEnabled: false,
    );
    expect(lastRequest.method, 'PATCH');
    expect(lastRequest.path, '/api/v1/me/notification-preferences');
    final sent = lastRequest.data;
    final map = sent is String ? jsonDecode(sent) : sent;
    expect(map['preferences'][0]['event_code'], 'ledger.publication');
    expect(map['preferences'][0]['push_enabled'], false);
    expect(map['preferences'][0].containsKey('email_enabled'), isFalse);
    expect(prefs.single.pushEnabled, isFalse);
  });

  test('registerDevice posts install/token/platform', () async {
    answerWith(200, {
      'install_id': 'i-1',
      'platform': 'ANDROID',
      'active': true,
    });
    final device = await repo.registerDevice(
      installId: 'i-1',
      fcmToken: 'tok',
      platform: 'ANDROID',
      appVersion: '1.0',
    );
    expect(device.installId, 'i-1');
    final sent = lastRequest.data;
    final map = sent is String ? jsonDecode(sent) : sent as Map;
    expect(map['fcm_token'], 'tok');
  });

  test('markNotificationRead posts to the read route', () async {
    answerWith(204, '');
    await repo.markNotificationRead(9);
    expect(lastRequest.path, '/api/v1/notifications/9/read');
    expect(lastRequest.method, 'POST');
  });
}
