import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/core/api_client.dart';
import 'package:lamto/core/occupancy.dart';
import 'package:lamto/core/token_store.dart';
import 'package:mocktail/mocktail.dart';

class _FakeStore implements TokenStore {
  @override
  Future<void> clear() async {}
  @override
  Future<String?> read() async => 'tok';
  @override
  Future<void> write(String value) async {}
}

class _MockAdapter extends Mock implements HttpClientAdapter {}

void main() {
  setUpAll(() => registerFallbackValue(RequestOptions(path: '/')));

  test(
    'injects X-LamTo-Occupancy only on building-scoped paths when set',
    () async {
      final holder = OccupancyHolder()..occupancyId = 42;
      final adapter = _MockAdapter();
      final dio = buildDio(
        store: _FakeStore(),
        occupancy: holder,
        onUnauthorized: () {},
        baseUrl: 'http://x',
      );
      dio.httpClientAdapter = adapter;

      String? seen;
      when(() => adapter.fetch(any(), any(), any())).thenAnswer((inv) async {
        seen = (inv.positionalArguments[0] as RequestOptions)
            .headers['X-LamTo-Occupancy']
            ?.toString();
        return ResponseBody.fromString(
          '{}',
          200,
          headers: {
            Headers.contentTypeHeader: [Headers.jsonContentType],
          },
        );
      });

      await dio.get<dynamic>('/api/v1/me');
      expect(seen, isNull);

      await dio.get<dynamic>('/api/v1/ledger');
      expect(seen, '42');

      holder.occupancyId = null;
      seen = 'sentinel';
      await dio.get<dynamic>('/api/v1/ledger');
      expect(seen, isNull);
    },
  );

  test('isBuildingScopedPath allowlist', () {
    expect(isBuildingScopedPath('/api/v1/ledger'), isTrue);
    expect(isBuildingScopedPath('/api/v1/reports'), isTrue);
    expect(isBuildingScopedPath('/api/v1/locations/1'), isTrue);
    expect(isBuildingScopedPath('/api/v1/me'), isFalse);
    expect(isBuildingScopedPath('/api/v1/auth/login'), isFalse);
    expect(isBuildingScopedPath('/api/v1/devices'), isFalse);
  });
}
