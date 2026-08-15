import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/core/failure.dart';
import 'package:lamto/l10n/app_localizations_vi.dart';

void main() {
  final l10n = AppLocalizationsVi();

  test('plate conflict does not leak another resident', () {
    final request = RequestOptions();
    final error = DioException(
      requestOptions: request,
      response: Response(
        requestOptions: request,
        data: {'code': 'gate_plate_already_registered'},
      ),
    );
    final message = failureMessage(Failure.fromObject(error), l10n);
    expect(message, contains('liên hệ ban quản lý'));
    expect(message, isNot(contains('căn hộ')));
  });

  test('every stable face enrollment error has distinct Vietnamese copy', () {
    final codes = [
      'gate_no_face_detected',
      'gate_multiple_faces',
      'gate_face_too_small',
      'gate_face_too_blurry',
      'gate_face_unusable',
      'gate_photo_rejected',
      'gate_face_upload_too_large',
      'gate_model_unavailable',
    ];
    final messages = codes.map((code) {
      final request = RequestOptions();
      return failureMessage(
        Failure.fromObject(
          DioException(
            requestOptions: request,
            response: Response(requestOptions: request, data: {'code': code}),
          ),
        ),
        l10n,
      );
    });
    expect(messages.toSet(), hasLength(codes.length));
  });
}
