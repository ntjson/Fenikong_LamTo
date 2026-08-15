import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/features/bills/bill_scan_screen.dart';
import 'package:lamto/features/bills/bills_repository.dart';
import 'package:lamto/l10n/app_localizations.dart';
import 'package:lamto_api/lamto_api.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

class _Repo implements BillsRepository {
  _Repo({this.error});

  final Object? error;
  String? confirmedReference;
  int confirmations = 0;

  /// When set, confirmPayment stalls until completed (busy-guard tests).
  Completer<void>? gate;

  @override
  Future<BillDetail> confirmPayment(int id, String reference) async {
    confirmations++;
    confirmedReference = reference;
    if (gate case final gate?) await gate.future;
    if (error case final error?) throw error;
    return BillDetail(
      (builder) => builder
        ..id = id
        ..title = 'Bill'
        ..amountVnd = 1
        ..status = BillStatusEnum.PAID
        ..period = ''
        ..issuedAt = DateTime.utc(2026, 7, 24)
        ..note = ''
        ..documentFilename = 'bill.pdf'
        ..documentDownloadUrl = '/api/v1/documents/token',
    );
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

ProviderContainer _container(_Repo repo) => ProviderContainer(
  overrides: [billsRepositoryProvider.overrideWithValue(repo)],
);

/// Pumps the scan screen and returns its scanner so tests can feed
/// detections directly (no camera in the test environment).
Future<MobileScanner> _pumpScan(WidgetTester tester, _Repo repo) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [billsRepositoryProvider.overrideWithValue(repo)],
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: const Locale('vi'),
        home: const BillScanScreen(billId: 1),
      ),
    ),
  );
  await tester.pump();
  return tester.widget<MobileScanner>(find.byType(MobileScanner));
}

BarcodeCapture _qr(String raw) =>
    BarcodeCapture(barcodes: [Barcode(rawValue: raw)]);

void main() {
  test(
    'refreshes detail, list, and Home bill state before leaving scan',
    () async {
      var detailLoads = 0;
      var listLoads = 0;
      var homeLoads = 0;
      final container = ProviderContainer(
        overrides: [
          billDetailProvider(1).overrideWith((ref) async {
            detailLoads++;
            return _Repo().confirmPayment(1, 'ref');
          }),
          billsProvider.overrideWith((ref) async {
            listLoads++;
            return [];
          }),
          newestUnpaidBillProvider.overrideWith((ref) async {
            homeLoads++;
            return null;
          }),
        ],
      );
      addTearDown(container.dispose);
      final subscriptions = [
        container.listen(billDetailProvider(1), (_, _) {}),
        container.listen(billsProvider, (_, _) {}),
        container.listen(newestUnpaidBillProvider, (_, _) {}),
      ];
      addTearDown(() {
        for (final subscription in subscriptions) {
          subscription.close();
        }
      });
      await Future.wait([
        container.read(billDetailProvider(1).future),
        container.read(billsProvider.future),
        container.read(newestUnpaidBillProvider.future),
      ]);

      invalidateBillViews(container, 1);
      await Future.wait([
        container.read(billDetailProvider(1).future),
        container.read(billsProvider.future),
        container.read(newestUnpaidBillProvider.future),
      ]);

      expect((detailLoads, listLoads, homeLoads), (2, 2, 2));
    },
  );

  test('rejects a non-LamTo QR without confirming payment', () async {
    final repo = _Repo();
    final container = _container(repo);
    addTearDown(container.dispose);

    expect(
      await handleScannedCode(container, 1, 'https://example.test'),
      BillScanResult.invalidQr,
    );
    expect(repo.confirmedReference, isNull);
  });

  test('confirms a LamTo QR using only its bill reference', () async {
    final repo = _Repo();
    final container = _container(repo);
    addTearDown(container.dispose);

    expect(
      await handleScannedCode(container, 7, 'lamto-bill:ref-9'),
      BillScanResult.recorded,
    );
    expect(repo.confirmedReference, 'ref-9');
  });

  testWidgets(
    'transient failure stays on the scan screen with inline copy and rescan',
    (tester) async {
      final repo = _Repo(
        error: DioException(requestOptions: RequestOptions(path: '/confirm')),
      );
      final scanner = await _pumpScan(tester, repo);

      scanner.onDetect!(_qr('lamto-bill:a'));
      await tester.pumpAndSettle();

      // Still here — no pop — with the mapped Vietnamese failure copy inline.
      expect(find.byType(BillScanScreen), findsOneWidget);
      expect(
        find.text(
          'Chưa thể xác nhận thanh toán đã được ghi nhận hay chưa. '
          'Hãy kiểm tra trạng thái hóa đơn trước khi thử lại.',
        ),
        findsOneWidget,
      );

      // Immediate rescan works: the busy flag was released.
      scanner.onDetect!(_qr('lamto-bill:b'));
      await tester.pumpAndSettle();
      expect(repo.confirmations, 2);
      expect(repo.confirmedReference, 'b');
    },
  );

  testWidgets('non-LamTo QR shows inline copy without confirming', (
    tester,
  ) async {
    final repo = _Repo();
    final scanner = await _pumpScan(tester, repo);

    scanner.onDetect!(_qr('https://example.test'));
    await tester.pumpAndSettle();

    expect(find.byType(BillScanScreen), findsOneWidget);
    expect(find.text('Mã QR không hợp lệ.'), findsOneWidget);
    expect(repo.confirmations, 0);
  });

  testWidgets('a second QR hit while confirming is swallowed', (tester) async {
    // Error result so the screen never pops (pop is exercised in the
    // detail-flow test); only the busy guard is under test here.
    final repo = _Repo(
      error: DioException(requestOptions: RequestOptions(path: '/confirm')),
    )..gate = Completer<void>();
    final scanner = await _pumpScan(tester, repo);

    scanner.onDetect!(_qr('lamto-bill:a'));
    await tester.pump();
    scanner.onDetect!(_qr('lamto-bill:b'));
    await tester.pump();

    repo.gate!.complete();
    await tester.pumpAndSettle();
    expect(repo.confirmations, 1);
    expect(repo.confirmedReference, 'a');
  });

  test(
    'distinguishes a voided bill from an unknown confirmation result',
    () async {
      final request = RequestOptions(path: '/bills/1/confirm-payment');
      final voided = _Repo(
        error: DioException(
          requestOptions: request,
          response: Response<void>(requestOptions: request, statusCode: 409),
        ),
      );
      final failed = _Repo(error: DioException(requestOptions: request));
      final voidedContainer = _container(voided);
      final failedContainer = _container(failed);
      addTearDown(voidedContainer.dispose);
      addTearDown(failedContainer.dispose);

      expect(
        await handleScannedCode(voidedContainer, 1, 'lamto-bill:void'),
        BillScanResult.voided,
      );
      expect(
        await handleScannedCode(failedContainer, 1, 'lamto-bill:retry'),
        BillScanResult.error,
      );
    },
  );
}
