import 'package:test/test.dart';
import 'package:lamto_api/lamto_api.dart';


/// tests for BillsApi
void main() {
  final instance = LamtoApi().getBillsApi();

  group(BillsApi, () {
    //Future<BillDetail> billsConfirmPayment(int id, BillConfirmPaymentRequestRequest billConfirmPaymentRequestRequest) async
    test('test billsConfirmPayment', () async {
      // TODO
    });

    //Future<PaginatedBillSummaryList> billsList({ String cursor }) async
    test('test billsList', () async {
      // TODO
    });

    //Future<BillDetail> billsRetrieve(int id) async
    test('test billsRetrieve', () async {
      // TODO
    });

  });
}
