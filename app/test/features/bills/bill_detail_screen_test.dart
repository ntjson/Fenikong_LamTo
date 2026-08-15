import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto_api/lamto_api.dart';
import 'package:lamto/features/bills/bill_detail_screen.dart';
import 'package:lamto/features/bills/bill_scan_screen.dart';
import 'package:lamto/features/bills/bills_repository.dart';
import 'package:lamto/l10n/app_localizations.dart';
import 'package:lamto/theme.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:pdfrx/pdfrx.dart';

import '../documents/document_fixtures.dart';
import '../documents/fake_share_platform.dart';

class _FakeRepo implements BillsRepository {
  _FakeRepo({this.dueDate});

  final DateTime? dueDate;

  /// Flips to PAID once a payment is confirmed, like the server would.
  var _status = BillStatusEnum.ISSUED;

  @override
  Future<BillDetail> fetchBill(int id) async => BillDetail(
    (builder) => builder
      ..id = id
      ..title = 'Phí 07'
      ..amountVnd = 250000
      ..status = _status
      ..period = ''
      ..issuedAt = DateTime.utc(2026, 7, 1)
      ..dueDate = dueDate
      ..note = ''
      ..documentFilename = 'b.pdf'
      ..documentDownloadUrl = '/api/v1/documents/t',
  );

  @override
  Future<BillDetail> confirmPayment(int id, String reference) async {
    _status = BillStatusEnum.PAID;
    return fetchBill(id);
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

/// Serves a PDF, so the document row reaches its viewer.
class _PdfRepo extends _FakeRepo {
  @override
  Future<Uint8List> fetchDocument(String downloadUrl) async => minimalPdfBytes;
}

late FakeSharePlatform share;

void main() {
  // Installed once: SharePlus latches the platform on first use.
  setUpAll(() => share = FakeSharePlatform.install());
  setUp(() => share.reset());

  testWidgets('the bill document opens in the app, never in a share sheet', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [billsRepositoryProvider.overrideWithValue(_PdfRepo())],
        child: const MaterialApp(
          localizationsDelegates: [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
          ],
          supportedLocales: [Locale('en'), Locale('vi')],
          home: BillDetailScreen(billId: 1),
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.ensureVisible(find.text('b.pdf'));
    await tester.tap(find.text('b.pdf'));
    for (var i = 0; i < 20; i++) {
      await tester.pump(const Duration(milliseconds: 100));
    }

    // Where the bytes go, not whether pages paint: `flutter test` has no
    // PDFium. Rendering is asserted in integration_test/document_viewer_test.dart.
    expect(find.byType(PdfViewer), findsOneWidget);
    expect(share.shared, isEmpty);
  });

  testWidgets('issued bill shows its amount, status, and payment action', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [billsRepositoryProvider.overrideWithValue(_FakeRepo())],
        child: const MaterialApp(
          localizationsDelegates: [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
          ],
          supportedLocales: [Locale('en'), Locale('vi')],
          home: BillDetailScreen(billId: 1),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('250.000 ₫'), findsOneWidget);
    expect(find.text('Unpaid'), findsOneWidget);
    // The two-step transfer-then-record model precedes the scan CTA (item E).
    expect(
      find.text(
        'Scanning records a transfer you already made — it does not pay the bill.',
      ),
      findsOneWidget,
    );
    expect(
      find.text('1. Transfer the amount in your banking app.'),
      findsOneWidget,
    );
    expect(
      find.text('2. Come back here and scan the QR on the bill to record it.'),
      findsOneWidget,
    );
    expect(find.text("I've paid"), findsOneWidget);
  });

  testWidgets('unpaid past-due bill names Quá hạn in the deadline pill', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          billsRepositoryProvider.overrideWithValue(
            _FakeRepo(dueDate: DateTime(2026, 6, 30)),
          ),
        ],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('vi'),
          home: const BillDetailScreen(billId: 1),
        ),
      ),
    );
    await tester.pumpAndSettle();

    // Word + tone, never color alone: status pill and overdue deadline pill.
    expect(find.text('30/06/2026 · Quá hạn'), findsOneWidget);
    expect(find.byType(StatusChip), findsNWidgets(2));
  });

  testWidgets('unpaid future-due bill keeps the quiet deadline text', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          billsRepositoryProvider.overrideWithValue(
            _FakeRepo(dueDate: DateTime(2100, 1, 1)),
          ),
        ],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('vi'),
          home: const BillDetailScreen(billId: 1),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('01/01/2100'), findsOneWidget);
    expect(find.textContaining('Quá hạn'), findsNothing);
    expect(find.byType(StatusChip), findsOneWidget); // status pill only
  });

  testWidgets(
    'successful scan pops back to an inline success notice over PAID state',
    (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [billsRepositoryProvider.overrideWithValue(_FakeRepo())],
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('vi'),
            home: const BillDetailScreen(billId: 1),
          ),
        ),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('Tôi đã thanh toán'));
      await tester.pumpAndSettle();
      expect(find.byType(BillScanScreen), findsOneWidget);

      tester.widget<MobileScanner>(find.byType(MobileScanner)).onDetect!(
        BarcodeCapture(barcodes: [Barcode(rawValue: 'lamto-bill:ref-1')]),
      );
      await tester.pumpAndSettle();

      // Back on the detail screen: inline outcome notice + refreshed PAID
      // chip (same resident copy on both, hence two matches).
      expect(find.byType(BillScanScreen), findsNothing);
      expect(find.text('Đã ghi nhận thanh toán'), findsNWidgets(2));
      // The scan CTA is gone: the bill is no longer payable.
      expect(find.text('Tôi đã thanh toán'), findsNothing);
    },
  );
}
