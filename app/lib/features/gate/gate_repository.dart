import 'package:dio/dio.dart';

abstract final class GateApiPaths {
  static const registrations = '/api/v1/gate/registrations';
  static const plates = '/api/v1/gate/plates';
  static const face = '/api/v1/gate/face';
  static const device = '/api/v1/gate/device';
  static const recognizeFace = '/api/v1/gate/recognize/face';
  static const recognizePlate = '/api/v1/gate/recognize/plate';
}

abstract class GateRepository {
  Future<Map<String, dynamic>> registrations();
  Future<void> addPlate(String plate);
  Future<void> deletePlate(int id);
  Future<void> submitFace(String path);
  Future<void> deleteFace();
}

class DioGateRepository implements GateRepository {
  DioGateRepository(this.dio);
  final Dio dio;
  @override
  Future<Map<String, dynamic>> registrations() async =>
      Map<String, dynamic>.from(
        (await dio.get(GateApiPaths.registrations)).data as Map,
      );
  @override
  Future<void> addPlate(String plate) async =>
      dio.post(GateApiPaths.plates, data: {'plate': plate});
  @override
  Future<void> deletePlate(int id) async =>
      dio.delete('${GateApiPaths.plates}/$id');
  @override
  Future<void> submitFace(String path) async => dio.post(
    GateApiPaths.face,
    data: FormData.fromMap({'photo': MultipartFile.fromFileSync(path)}),
  );
  @override
  Future<void> deleteFace() async => dio.delete(GateApiPaths.face);
}
