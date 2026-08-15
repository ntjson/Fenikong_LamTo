import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

import '../../l10n/app_localizations.dart';
import '../../core/adaptive_scaffold.dart';
import '../../theme.dart';
import 'bill_qr.dart';
import 'bills_repository.dart';

enum BillScanResult { invalidQr, recorded, voided, error }

void invalidateBillViews(ProviderContainer container, int billId) {
  container.invalidate(billDetailProvider(billId));
  container.invalidate(billsProvider);
  container.invalidate(newestUnpaidBillProvider);
}

Future<BillScanResult> handleScannedCode(
  ProviderContainer container,
  int billId,
  String raw,
) async {
  final reference = billReferenceFromQr(raw);
  if (reference == null) return BillScanResult.invalidQr;
  try {
    await container
        .read(billsRepositoryProvider)
        .confirmPayment(billId, reference);
    return BillScanResult.recorded;
  } on DioException catch (error) {
    return error.response?.statusCode == 409
        ? BillScanResult.voided
        : BillScanResult.error;
  } catch (_) {
    return BillScanResult.error;
  }
}

class BillScanScreen extends ConsumerStatefulWidget {
  const BillScanScreen({required this.billId, super.key});

  final int billId;

  @override
  ConsumerState<BillScanScreen> createState() => _BillScanScreenState();
}

class _BillScanScreenState extends ConsumerState<BillScanScreen> {
  bool _handling = false;

  /// Inline failure copy (SnackBars never render under the iOS Cupertino
  /// shell). Non-null keeps the resident on this screen for an instant
  /// rescan; the camera session stays alive because the screen never pops.
  String? _failure;

  Future<void> _onDetect(BarcodeCapture capture) async {
    if (_handling) return;
    String? raw;
    for (final barcode in capture.barcodes) {
      if (barcode.rawValue case final value?) {
        raw = value;
        break;
      }
    }
    if (raw == null) return;
    setState(() {
      _handling = true;
      _failure = null;
    });

    final result = await handleScannedCode(
      ProviderScope.containerOf(context),
      widget.billId,
      raw,
    );
    if (!mounted) return;

    final l10n = AppLocalizations.of(context)!;
    if (result != BillScanResult.invalidQr) {
      // Even on an unknown failure the payment may have landed server-side;
      // refresh so the detail screen shows the authoritative status.
      invalidateBillViews(ProviderScope.containerOf(context), widget.billId);
    }
    switch (result) {
      case BillScanResult.invalidQr:
      case BillScanResult.error:
        // Transient: stay here, say what happened, allow immediate rescan.
        setState(() {
          _handling = false;
          _failure = result == BillScanResult.invalidQr
              ? l10n.billInvalidQr
              : l10n.billPaymentUnknown;
        });
      case BillScanResult.recorded:
      case BillScanResult.voided:
        // Conclusive: the bill detail screen renders the outcome notice
        // (visible on iOS, unlike a SnackBar) over the refreshed status.
        Navigator.of(context).pop(result);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return AdaptiveScaffold(
      title: l10n.billScanTitle,
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(l10n.billScanInstruction, textAlign: TextAlign.center),
          ),
          if (_failure case final failure?)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              child: StatusNotice(tone: StatusTone.error, message: failure),
            ),
          Expanded(
            child: Semantics(
              label: l10n.billScanInstruction,
              child: MobileScanner(
                onDetect: _onDetect,
                errorBuilder: (context, error) => Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Text(
                      l10n.billCameraUnavailable,
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
              ),
            ),
          ),
          if (_handling)
            const Padding(
              padding: EdgeInsets.all(16),
              child: CircularProgressIndicator.adaptive(),
            ),
        ],
      ),
    );
  }
}
