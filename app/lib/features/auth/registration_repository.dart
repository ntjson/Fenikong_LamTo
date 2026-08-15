import 'package:built_collection/built_collection.dart';
import 'package:dio/dio.dart';
import 'package:lamto_api/lamto_api.dart';

class RegistrationRepository {
  RegistrationRepository(Dio dio)
    : _api = RegistrationApi(dio, standardSerializers);

  final RegistrationApi _api;

  Future<BuiltList<RegistrationBuilding>> options() async =>
      (await _api.registrationOptions()).data!;

  Future<RegistrationSubmission> submit(
    RegistrationCreateRequest request,
  ) async =>
      (await _api.registrationCreate(registrationCreateRequest: request)).data!;

  Future<RegistrationStatus> status(String token) async =>
      (await _api.registrationStatus(xRegistrationStatusToken: token)).data!;
}
