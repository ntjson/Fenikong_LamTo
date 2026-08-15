import 'package:test/test.dart';
import 'package:lamto_api/lamto_api.dart';


/// tests for FundApi
void main() {
  final instance = LamtoApi().getFundApi();

  group(FundApi, () {
    //Future<FundSeries> fundSeriesRetrieve({ int xLamToOccupancy, String range }) async
    test('test fundSeriesRetrieve', () async {
      // TODO
    });

    //Future<FundSummary> fundSummaryRetrieve({ int xLamToOccupancy }) async
    test('test fundSummaryRetrieve', () async {
      // TODO
    });

  });
}
