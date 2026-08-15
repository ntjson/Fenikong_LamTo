import 'package:test/test.dart';
import 'package:lamto_api/lamto_api.dart';


/// tests for CasesApi
void main() {
  final instance = LamtoApi().getCasesApi();

  group(CasesApi, () {
    //Future<CaseRatingResult> casesRatingCreate(int id, CaseRatingRequest caseRatingRequest) async
    test('test casesRatingCreate', () async {
      // TODO
    });

  });
}
