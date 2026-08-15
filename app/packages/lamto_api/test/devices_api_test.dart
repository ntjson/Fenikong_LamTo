import 'package:test/test.dart';
import 'package:lamto_api/lamto_api.dart';


/// tests for DevicesApi
void main() {
  final instance = LamtoApi().getDevicesApi();

  group(DevicesApi, () {
    //Future<Device> devicesCreate(DeviceRegisterRequest deviceRegisterRequest) async
    test('test devicesCreate', () async {
      // TODO
    });

    //Future devicesDestroy(String installId) async
    test('test devicesDestroy', () async {
      // TODO
    });

  });
}
