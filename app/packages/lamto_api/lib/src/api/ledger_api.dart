//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

import 'dart:async';

import 'package:built_value/json_object.dart';
import 'package:built_value/serializer.dart';
import 'package:dio/dio.dart';

import 'package:lamto_api/src/api_util.dart';
import 'package:lamto_api/src/model/ledger_entry_detail.dart';
import 'package:lamto_api/src/model/paginated_ledger_entry_list_list.dart';
import 'package:lamto_api/src/model/problem.dart';

class LedgerApi {

  final Dio _dio;

  final Serializers _serializers;

  const LedgerApi(this._dio, this._serializers);

  /// ledgerList
  ///
  ///
  /// Parameters:
  /// * [xLamToOccupancy] - Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404.
  /// * [cursor] - The pagination cursor value.
  /// * [month]
  /// * [year]
  /// * [cancelToken] - A [CancelToken] that can be used to cancel the operation
  /// * [headers] - Can be used to add additional headers to the request
  /// * [extras] - Can be used to add flags to the request
  /// * [validateStatus] - A [ValidateStatus] callback that can be used to determine request success based on the HTTP status of the response
  /// * [onSendProgress] - A [ProgressCallback] that can be used to get the send progress
  /// * [onReceiveProgress] - A [ProgressCallback] that can be used to get the receive progress
  ///
  /// Returns a [Future] containing a [Response] with a [PaginatedLedgerEntryListList] as data
  /// Throws [DioException] if API call or serialization fails
  Future<Response<PaginatedLedgerEntryListList>> ledgerList({
    int? xLamToOccupancy,
    String? cursor,
    int? month,
    int? year,
    CancelToken? cancelToken,
    Map<String, dynamic>? headers,
    Map<String, dynamic>? extra,
    ValidateStatus? validateStatus,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    final _path = r'/api/v1/ledger';
    final _options = Options(
      method: r'GET',
      headers: <String, dynamic>{
        if (xLamToOccupancy != null) r'X-LamTo-Occupancy': xLamToOccupancy,
        ...?headers,
      },
      extra: <String, dynamic>{
        'secure': <Map<String, String>>[
          {
            'type': 'apiKey',
            'name': 'knoxApiToken',
            'keyName': 'Authorization',
            'where': 'header',
          },
        ],
        ...?extra,
      },
      validateStatus: validateStatus,
    );

    final _queryParameters = <String, dynamic>{
      if (cursor != null) r'cursor': encodeQueryParameter(_serializers, cursor, const FullType(String)),
      if (month != null) r'month': encodeQueryParameter(_serializers, month, const FullType(int)),
      if (year != null) r'year': encodeQueryParameter(_serializers, year, const FullType(int)),
    };

    final _response = await _dio.request<Object>(
      _path,
      options: _options,
      queryParameters: _queryParameters,
      cancelToken: cancelToken,
      onSendProgress: onSendProgress,
      onReceiveProgress: onReceiveProgress,
    );

    PaginatedLedgerEntryListList? _responseData;

    try {
      final rawResponse = _response.data;
      _responseData = rawResponse == null ? null : _serializers.deserialize(
        rawResponse,
        specifiedType: const FullType(PaginatedLedgerEntryListList),
      ) as PaginatedLedgerEntryListList;

    } catch (error, stackTrace) {
      throw DioException(
        requestOptions: _response.requestOptions,
        response: _response,
        type: DioExceptionType.unknown,
        error: error,
        stackTrace: stackTrace,
      );
    }

    return Response<PaginatedLedgerEntryListList>(
      data: _responseData,
      headers: _response.headers,
      isRedirect: _response.isRedirect,
      requestOptions: _response.requestOptions,
      redirects: _response.redirects,
      statusCode: _response.statusCode,
      statusMessage: _response.statusMessage,
      extra: _response.extra,
    );
  }

  /// ledgerRetrieve
  ///
  ///
  /// Parameters:
  /// * [id]
  /// * [xLamToOccupancy] - Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404.
  /// * [cancelToken] - A [CancelToken] that can be used to cancel the operation
  /// * [headers] - Can be used to add additional headers to the request
  /// * [extras] - Can be used to add flags to the request
  /// * [validateStatus] - A [ValidateStatus] callback that can be used to determine request success based on the HTTP status of the response
  /// * [onSendProgress] - A [ProgressCallback] that can be used to get the send progress
  /// * [onReceiveProgress] - A [ProgressCallback] that can be used to get the receive progress
  ///
  /// Returns a [Future] containing a [Response] with a [LedgerEntryDetail] as data
  /// Throws [DioException] if API call or serialization fails
  Future<Response<LedgerEntryDetail>> ledgerRetrieve({
    required int id,
    int? xLamToOccupancy,
    CancelToken? cancelToken,
    Map<String, dynamic>? headers,
    Map<String, dynamic>? extra,
    ValidateStatus? validateStatus,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    final _path = r'/api/v1/ledger/{id}'.replaceAll('{' r'id' '}', encodeQueryParameter(_serializers, id, const FullType(int)).toString());
    final _options = Options(
      method: r'GET',
      headers: <String, dynamic>{
        if (xLamToOccupancy != null) r'X-LamTo-Occupancy': xLamToOccupancy,
        ...?headers,
      },
      extra: <String, dynamic>{
        'secure': <Map<String, String>>[
          {
            'type': 'apiKey',
            'name': 'knoxApiToken',
            'keyName': 'Authorization',
            'where': 'header',
          },
        ],
        ...?extra,
      },
      validateStatus: validateStatus,
    );

    final _response = await _dio.request<Object>(
      _path,
      options: _options,
      cancelToken: cancelToken,
      onSendProgress: onSendProgress,
      onReceiveProgress: onReceiveProgress,
    );

    LedgerEntryDetail? _responseData;

    try {
      final rawResponse = _response.data;
      _responseData = rawResponse == null ? null : _serializers.deserialize(
        rawResponse,
        specifiedType: const FullType(LedgerEntryDetail),
      ) as LedgerEntryDetail;

    } catch (error, stackTrace) {
      throw DioException(
        requestOptions: _response.requestOptions,
        response: _response,
        type: DioExceptionType.unknown,
        error: error,
        stackTrace: stackTrace,
      );
    }

    return Response<LedgerEntryDetail>(
      data: _responseData,
      headers: _response.headers,
      isRedirect: _response.isRedirect,
      requestOptions: _response.requestOptions,
      redirects: _response.redirects,
      statusCode: _response.statusCode,
      statusMessage: _response.statusMessage,
      extra: _response.extra,
    );
  }

}
