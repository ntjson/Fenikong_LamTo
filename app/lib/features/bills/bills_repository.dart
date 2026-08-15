import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lamto_api/lamto_api.dart';

import '../../core/providers.dart';

abstract class BillsRepository {
  Future<PaginatedBillSummaryList> listBills({String? cursor});
  Future<BillDetail> fetchBill(int id);
  Future<BillDetail> confirmPayment(int id, String reference);
  Future<Uint8List> fetchDocument(String downloadUrl);
}

class DioBillsRepository implements BillsRepository {
  DioBillsRepository(Dio dio)
    : _bills = BillsApi(dio, standardSerializers),
      _documents = DocumentsApi(dio, standardSerializers);

  final BillsApi _bills;
  final DocumentsApi _documents;

  @override
  Future<PaginatedBillSummaryList> listBills({String? cursor}) async =>
      (await _bills.billsList(cursor: cursor)).data!;

  @override
  Future<BillDetail> fetchBill(int id) async =>
      (await _bills.billsRetrieve(id: id)).data!;

  @override
  Future<BillDetail> confirmPayment(int id, String reference) async {
    final response = await _bills.billsConfirmPayment(
      id: id,
      billConfirmPaymentRequestRequest: BillConfirmPaymentRequestRequest(
        (builder) => builder.reference = reference,
      ),
    );
    return response.data!;
  }

  @override
  Future<Uint8List> fetchDocument(String downloadUrl) async {
    final segments = Uri.parse(downloadUrl).pathSegments;
    if (segments.isEmpty || segments.last.isEmpty) {
      throw StateError('Document URL has no access token');
    }
    return (await _documents.documentsRetrieve(token: segments.last)).data!;
  }
}

final billsRepositoryProvider = Provider<BillsRepository>(
  (ref) => DioBillsRepository(ref.watch(dioProvider)),
);

final billsProvider = FutureProvider.autoDispose<List<BillSummary>>((
  ref,
) async {
  ref.watch(occupancyScopedProviders);
  final page = await ref.watch(billsRepositoryProvider).listBills();
  return page.results.toList();
});

final newestUnpaidBillProvider = FutureProvider.autoDispose<BillSummary?>((
  ref,
) async {
  final bills = await ref.watch(billsProvider.future);
  for (final bill in bills) {
    if (bill.status == BillStatusEnum.ISSUED) return bill;
  }
  return null;
});

final billDetailProvider = FutureProvider.autoDispose.family<BillDetail, int>((
  ref,
  id,
) {
  ref.watch(occupancyScopedProviders);
  return ref.watch(billsRepositoryProvider).fetchBill(id);
});
