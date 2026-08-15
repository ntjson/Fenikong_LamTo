import 'package:test/test.dart';
import 'package:lamto_api/lamto_api.dart';


/// tests for LedgerApi
void main() {
  final instance = LamtoApi().getLedgerApi();

  group(LedgerApi, () {
    //Future<PaginatedLedgerEntryListList> ledgerList({ int xLamToOccupancy, String cursor, int month, int year }) async
    test('test ledgerList', () async {
      // TODO
    });

    //Future<LedgerEntryDetail> ledgerRetrieve(int id, { int xLamToOccupancy }) async
    test('test ledgerRetrieve', () async {
      // TODO
    });

  });
}
