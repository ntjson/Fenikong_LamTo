import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/core/api_client.dart';
import 'package:lamto/core/occupancy.dart';
import 'package:lamto/core/token_store.dart';
import 'package:mocktail/mocktail.dart';

class _FakeStore implements TokenStore {
  String? token;
  @override
  Future<void> clear() async => token = null;
  @override
  Future<String?> read() async => token;
  @override
  Future<void> write(String value) async => token = value;
}

class _MockAdapter extends Mock implements HttpClientAdapter {}

void main() {
  setUpAll(() => registerFallbackValue(RequestOptions(path: '/')));

  test('attaches token and clears it on 401', () async {
    final store = _FakeStore()..token = 'knox-123';
    final adapter = _MockAdapter();
    var unauthorized = false;
    final dio = buildDio(
      store: store,
      occupancy: OccupancyHolder(),
      onUnauthorized: () => unauthorized = true,
      baseUrl: 'http://x',
    );
    dio.httpClientAdapter = adapter;

    when(() => adapter.fetch(any(), any(), any())).thenAnswer((inv) async {
      final opts = inv.positionalArguments[0] as RequestOptions;
      expect(opts.headers['Authorization'], 'Token knox-123');
      return ResponseBody.fromString(
        '{}',
        200,
        headers: {
          Headers.contentTypeHeader: [Headers.jsonContentType],
        },
      );
    });
    await dio.get<dynamic>('/api/v1/me');

    when(() => adapter.fetch(any(), any(), any())).thenAnswer(
      (_) async => ResponseBody.fromString(
        '{}',
        401,
        headers: {
          Headers.contentTypeHeader: [Headers.jsonContentType],
        },
      ),
    );
    await expectLater(
      dio.get<dynamic>('/api/v1/me'),
      throwsA(isA<DioException>()),
    );
    expect(store.token, isNull);
    expect(unauthorized, isTrue);
  });
}
