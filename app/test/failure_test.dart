import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/core/failure.dart';

DioException _dio(int status, Map<String, dynamic> body) {
  final req = RequestOptions(path: '/x');
  return DioException(
    requestOptions: req,
    response: Response(requestOptions: req, statusCode: status, data: body),
    type: DioExceptionType.badResponse,
  );
}

void main() {
  test('parses problem+json code and per-field errors', () {
    final f = Failure.fromDio(
      _dio(400, {
        'code': 'validation_failed',
        'detail': 'Request validation failed.',
        'errors': {
          'text': [
            {'message': 'This field is required.', 'code': 'required'},
          ],
        },
      }),
    );
    expect(f.code, 'validation_failed');
    expect(f.fieldErrors['text']!.first, 'This field is required.');
  });

  test('maps known codes and falls back generically', () {
    expect(Failure(code: 'occupancy_selection_required').isKnown, isTrue);
    expect(Failure(code: 'weird_unknown').isKnown, isFalse);
    final net = Failure.fromDio(
      DioException(
        requestOptions: RequestOptions(path: '/x'),
        type: DioExceptionType.connectionTimeout,
      ),
    );
    expect(net.code, 'network_error');
  });

  test('fromObject coerces DioException, Failure, and unknowns', () {
    final dio = Failure.fromObject(
      DioException(
        requestOptions: RequestOptions(path: '/x'),
        type: DioExceptionType.connectionTimeout,
      ),
    );
    expect(dio.code, 'network_error');

    final existing = Failure(code: 'throttled', detail: 'slow');
    expect(identical(Failure.fromObject(existing), existing), isTrue);

    expect(Failure.fromObject(StateError('x')).code, 'server_error');
  });
}
