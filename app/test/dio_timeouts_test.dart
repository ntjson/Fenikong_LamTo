import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/core/api_client.dart';
import 'package:lamto/core/occupancy.dart';
import 'package:lamto/core/token_store.dart';

class _FakeStore implements TokenStore {
  @override
  Future<void> clear() async {}
  @override
  Future<String?> read() async => null;
  @override
  Future<void> write(String value) async {}
}

void main() {
  test('buildDio sets finite connect and receive timeouts', () {
    final dio = buildDio(
      store: _FakeStore(),
      occupancy: OccupancyHolder(),
      onUnauthorized: () {},
      baseUrl: 'http://x',
    );

    expect(dio.options.connectTimeout, isNotNull);
    expect(dio.options.receiveTimeout, isNotNull);
    expect(dio.options.connectTimeout!.inMilliseconds, greaterThan(0));
    expect(dio.options.receiveTimeout!.inMilliseconds, greaterThan(0));
    // Shipped defaults (production path via dioProvider → buildDio).
    expect(dio.options.connectTimeout, kDioConnectTimeout);
    expect(dio.options.receiveTimeout, kDioReceiveTimeout);
  });

  test('buildDio allows overriding timeouts for tests', () {
    final dio = buildDio(
      store: _FakeStore(),
      occupancy: OccupancyHolder(),
      onUnauthorized: () {},
      baseUrl: 'http://x',
      connectTimeout: const Duration(seconds: 3),
      receiveTimeout: const Duration(seconds: 7),
    );
    expect(dio.options.connectTimeout, const Duration(seconds: 3));
    expect(dio.options.receiveTimeout, const Duration(seconds: 7));
  });
}
