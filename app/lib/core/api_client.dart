import 'package:dio/dio.dart';

import 'config.dart';
import 'occupancy.dart';
import 'token_store.dart';

/// Default connect timeout for the shared resident Dio client.
const Duration kDioConnectTimeout = Duration(seconds: 15);

/// Default receive timeout for the shared resident Dio client.
const Duration kDioReceiveTimeout = Duration(seconds: 30);

/// One interceptor owns auth (spec 6.4): attach the knox token; on any 401
/// clear secure storage. [onUnauthorized] fires only when [signalSessionLoss]
/// is true (post-login session expiry) — bootstrap handles 401 itself to avoid
/// racing invalidate of the building notifier (review I2).
///
/// Connect/receive timeouts are finite so a stalled network fails into the
/// [Failure] network path instead of hanging indefinitely.
Dio buildDio({
  required TokenStore store,
  required OccupancyHolder occupancy,
  required void Function() onUnauthorized,
  String? baseUrl,
  bool Function()? signalSessionLoss,
  Duration? connectTimeout,
  Duration? receiveTimeout,
}) {
  final dio = Dio(
    BaseOptions(
      baseUrl: baseUrl ?? apiBaseUrl,
      connectTimeout: connectTimeout ?? kDioConnectTimeout,
      receiveTimeout: receiveTimeout ?? kDioReceiveTimeout,
    ),
  );
  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await store.read();
        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = 'Token $token';
          options.extra['had_token'] = true;
        }
        final occ = occupancy.occupancyId;
        if (occ != null && isBuildingScopedPath(options.path)) {
          options.headers['X-LamTo-Occupancy'] = occ;
        }
        handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401 &&
            error.requestOptions.extra['had_token'] == true) {
          await store.clear();
          // Only notify session loss after an established session — not during
          // cold-start bootstrap (session controller owns that 401 path).
          if (signalSessionLoss == null || signalSessionLoss()) {
            onUnauthorized();
          }
        }
        handler.next(error);
      },
    ),
  );
  return dio;
}
