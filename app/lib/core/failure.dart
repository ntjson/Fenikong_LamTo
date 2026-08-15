import 'package:dio/dio.dart';

import '../l10n/app_localizations.dart';

/// Stable machine codes the resident UI branches on (spec 3.1).
const knownFailureCodes = {
  'validation_failed',
  'authentication_failed',
  'not_authenticated',
  'permission_denied',
  'not_found',
  'occupancy_selection_required',
  'client_ref_conflict',
  'throttled',
  'network_error',
  'server_error',
  'schema_error',
  'gate_no_face_detected',
  'gate_multiple_faces',
  'gate_face_too_small',
  'gate_face_too_blurry',
  'gate_face_unusable',
  'gate_photo_rejected',
  'gate_face_upload_too_large',
  'gate_plate_already_registered',
  'gate_model_unavailable',
  'gate_device_revoked',
  'gate_device_expired',
  'gate_device_unauthenticated',
  'gate_recognition_throttled',
};

class Failure {
  Failure({required this.code, this.detail = '', this.fieldErrors = const {}});

  final String code;
  final String detail; // developer English; never shown raw to residents
  final Map<String, List<String>> fieldErrors;

  bool get isKnown => knownFailureCodes.contains(code);

  factory Failure.fromDio(DioException e) {
    final data = e.response?.data;
    if (data is Map && data['code'] is String) {
      final rawErrors = data['errors'];
      final fieldErrors = <String, List<String>>{};
      if (rawErrors is Map) {
        rawErrors.forEach((key, value) {
          if (value is List) {
            fieldErrors['$key'] = value
                .map(
                  (item) => item is Map && item['message'] != null
                      ? '${item['message']}'
                      : '$item',
                )
                .toList();
          }
        });
      }
      return Failure(
        code: data['code'] as String,
        detail: data['detail'] is String ? data['detail'] as String : '',
        fieldErrors: fieldErrors,
      );
    }
    final status = e.response?.statusCode;
    if (status != null && status >= 500) return Failure(code: 'server_error');
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
      case DioExceptionType.connectionError:
        return Failure(code: 'network_error');
      default:
        return Failure(code: 'server_error');
    }
  }

  /// Coerce any thrown object (DioException or otherwise) into a Failure.
  factory Failure.fromObject(Object error) => error is Failure
      ? error
      : error is DioException
      ? Failure.fromDio(error)
      : Failure(code: 'server_error');
}

/// Resident-facing copy per failure code (spec 6.4 doctrine). Never shows raw
/// HTTP jargon or the developer `detail`.
String failureMessage(Failure f, AppLocalizations l10n) {
  switch (f.code) {
    case 'authentication_failed':
    case 'not_authenticated':
      return l10n.errAuthFailed;
    case 'throttled':
      return l10n.errThrottled;
    case 'occupancy_selection_required':
      return l10n.errOccupancyRequired;
    case 'network_error':
      return l10n.errNetwork;
    case 'gate_no_face_detected':
      return l10n.gateErrorNoFace;
    case 'gate_multiple_faces':
      return l10n.gateErrorMultipleFaces;
    case 'gate_face_too_small':
      return l10n.gateErrorFaceTooSmall;
    case 'gate_face_too_blurry':
      return l10n.gateErrorFaceTooBlurry;
    case 'gate_face_unusable':
      return l10n.gateErrorFaceUnusable;
    case 'gate_photo_rejected':
      return l10n.gateErrorPhotoRejected;
    case 'gate_face_upload_too_large':
      return l10n.gateErrorPhotoTooLarge;
    case 'gate_plate_already_registered':
      return l10n.gateErrorPlateRegistered;
    case 'gate_model_unavailable':
      return l10n.gateErrorUnavailable;
    case 'gate_device_revoked':
      return l10n.gateReaderDeviceRevoked;
    case 'gate_device_expired':
      return l10n.gateReaderDeviceExpired;
    case 'gate_device_unauthenticated':
      return l10n.gateReaderDeviceInvalid;
    case 'gate_recognition_throttled':
      return l10n.gateReaderThrottled;
    case 'server_error':
    case 'schema_error':
      return l10n.errServer;
    default:
      return l10n.errGeneric;
  }
}
