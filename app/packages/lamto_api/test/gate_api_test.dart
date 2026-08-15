import 'package:test/test.dart';
import 'package:lamto_api/lamto_api.dart';


/// tests for GateApi
void main() {
  final instance = LamtoApi().getGateApi();

  group(GateApi, () {
    //Future<GateDevice> gateDeviceRetrieve() async
    test('test gateDeviceRetrieve', () async {
      // TODO
    });

    //Future<FaceEnrollment> gateFaceCreate(MultipartFile photo, { int xLamToOccupancy }) async
    test('test gateFaceCreate', () async {
      // TODO
    });

    //Future gateFaceDestroy({ int xLamToOccupancy }) async
    test('test gateFaceDestroy', () async {
      // TODO
    });

    //Future<VehiclePlate> gatePlatesCreate(PlateCreateRequest plateCreateRequest, { int xLamToOccupancy }) async
    test('test gatePlatesCreate', () async {
      // TODO
    });

    //Future gatePlatesDestroy(int id, { int xLamToOccupancy }) async
    test('test gatePlatesDestroy', () async {
      // TODO
    });

    //Future<RecognitionOutcome> gateRecognizeFaceCreate(MultipartFile photo) async
    test('test gateRecognizeFaceCreate', () async {
      // TODO
    });

    //Future<RecognitionOutcome> gateRecognizePlateCreate(PlateRecognizeRequest plateRecognizeRequest) async
    test('test gateRecognizePlateCreate', () async {
      // TODO
    });

    //Future<GateRegistrations> gateRegistrationsRetrieve({ int xLamToOccupancy }) async
    test('test gateRegistrationsRetrieve', () async {
      // TODO
    });

  });
}
