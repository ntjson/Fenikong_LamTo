import 'package:dio/dio.dart';
import '../gate_repository.dart';

class ReaderResult {
  ReaderResult.fromJson(Map data)
    : matched = data['matched'] == true,
      name = '${data['display_name'] ?? ''}',
      unit = '${data['unit_label'] ?? ''}',
      direction = '${data['direction'] ?? ''}',
      score = data['score'] as num?;
  final bool matched;
  final String name;
  final String unit;
  final String direction;
  final num? score;
}

class ReaderDevice {
  ReaderDevice.fromJson(Map data)
    : label = '${data['label'] ?? ''}',
      direction = '${data['direction'] ?? ''}';
  final String label;
  final String direction;
}

abstract class ReaderApi {
  Future<ReaderDevice> getDevice();
  Future<ReaderResult> recognizePlate(String plate);
  Future<ReaderResult> recognizeFace(String path);
}

class ReaderRepository implements ReaderApi {
  ReaderRepository(this.dio, this.credential);
  final Dio dio;
  final String credential;
  Options get _options =>
      Options(headers: {'Authorization': 'GateDevice $credential'});
  @override
  Future<ReaderDevice> getDevice() async => ReaderDevice.fromJson(
    (await dio.get(GateApiPaths.device, options: _options)).data as Map,
  );
  @override
  Future<ReaderResult> recognizePlate(String plate) async =>
      ReaderResult.fromJson(
        (await dio.post(
              GateApiPaths.recognizePlate,
              data: {'plate': plate},
              options: _options,
            )).data
            as Map,
      );
  @override
  Future<ReaderResult> recognizeFace(String path) async =>
      ReaderResult.fromJson(
        (await dio.post(
              GateApiPaths.recognizeFace,
              data: FormData.fromMap({
                'photo': MultipartFile.fromFileSync(path),
              }),
              options: _options,
            )).data
            as Map,
      );
}
