import 'package:test/test.dart';
import 'package:lamto_api/lamto_api.dart';


/// tests for LocationsApi
void main() {
  final instance = LamtoApi().getLocationsApi();

  group(LocationsApi, () {
    //Future<BuiltList<Location>> locationsRetrieve({ int xLamToOccupancy }) async
    test('test locationsRetrieve', () async {
      // TODO
    });

  });
}
