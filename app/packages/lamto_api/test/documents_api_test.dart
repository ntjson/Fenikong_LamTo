import 'package:test/test.dart';
import 'package:lamto_api/lamto_api.dart';


/// tests for DocumentsApi
void main() {
  final instance = LamtoApi().getDocumentsApi();

  group(DocumentsApi, () {
    //Future<Uint8List> documentsRetrieve(String token) async
    test('test documentsRetrieve', () async {
      // TODO
    });

  });
}
