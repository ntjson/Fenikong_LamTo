import 'package:test/test.dart';
import 'package:lamto_api/lamto_api.dart';

// tests for DeviceRegisterRequest
void main() {
  final instance = DeviceRegisterRequestBuilder();
  // TODO add properties to the builder and call build()

  group(DeviceRegisterRequest, () {
    // Stable per-install client UUID (spec 7.2).
    // String installId
    test('to test the property `installId`', () async {
      // TODO
    });

    // String fcmToken
    test('to test the property `fcmToken`', () async {
      // TODO
    });

    // PlatformEnum platform
    test('to test the property `platform`', () async {
      // TODO
    });

    // String appVersion (default value: '')
    test('to test the property `appVersion`', () async {
      // TODO
    });

  });
}
