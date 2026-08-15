import 'package:test/test.dart';
import 'package:lamto_api/lamto_api.dart';


/// tests for RegistrationApi
void main() {
  final instance = LamtoApi().getRegistrationApi();

  group(RegistrationApi, () {
    //Future<RegistrationSubmission> registrationCreate(RegistrationCreateRequest registrationCreateRequest) async
    test('test registrationCreate', () async {
      // TODO
    });

    //Future<BuiltList<RegistrationBuilding>> registrationOptions() async
    test('test registrationOptions', () async {
      // TODO
    });

    //Future<RegistrationStatus> registrationStatus(String xRegistrationStatusToken) async
    test('test registrationStatus', () async {
      // TODO
    });

  });
}
