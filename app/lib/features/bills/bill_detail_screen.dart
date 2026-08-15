import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:lamto_api/lamto_api.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

import '../../core/adaptive_buttons.dart';
import '../../core/adaptive_page_route.dart';
import '../../core/adaptive_scaffold.dart';
import '../../core/error_retry.dart';
import '../../core/format.dart';
import '../../core/page_body.dart';
import '../../l10n/app_localizations.dart';
import '../../theme.dart';
import 'bill_scan_screen.dart';
import 'bills_repository.dart';

class BillDetailScreen extends ConsumerStatefulWidget {
  const BillDetailScreen({required this.billId, super.key});

  final int billId;

  @override
  ConsumerState<BillDetailScreen> createState() => _BillDetailScreenState();
}

class _BillDetailScreenState extends ConsumerState<BillDetailScreen> {
  bool _openingDocument = false;

  /// Outcome of the scan flow, rendered as an inline notice (a SnackBar
  /// would never appear under the iOS Cupertino shell).
  BillScanResult? _scanResult;

  /// Inline document-open failure, shown under the document row.
  bool _documentFailed = false;

  Future<void> _openDocument(BillDetail bill) async {
    if (_openingDocument) return;
    setState(() {
      _openingDocument = true;
      _documentFailed = false;
    });
    File? file;
    try {
      final bytes = await ref
          .read(billsRepositoryProvider)
          .fetchDocument(bill.documentDownloadUrl);
      final directory = await getTemporaryDirectory();
      final filename = bill.documentFilename.replaceAll(
        RegExp(r'[/\\]|\.\.'),
        '_',
      );
      file = File('${directory.path}/${filename.isEmpty ? 'bill' : filename}');
      await file.writeAsBytes(bytes, flush: true);
      if (!mounted) return;
      final box = context.findRenderObject() as RenderBox?;
      await SharePlus.instance.share(
        ShareParams(
          files: [XFile(file.path)],
          sharePositionOrigin: box != null && box.hasSize
              ? box.localToGlobal(Offset.zero) & box.size
              : null,
        ),
      );
    } catch (_) {
      if (mounted) setState(() => _documentFailed = true);
    } finally {
      try {
        if (await file?.exists() ?? false) await file!.delete();
      } catch (_) {}
      if (mounted) setState(() => _openingDocument = false);
    }
  }

  Future<void> _scanPayment() async {
    final result = await Navigator.of(context).push(
      adaptivePageRoute<BillScanResult>(
        builder: (_) => BillScanScreen(billId: widget.billId),
      ),
    );
    // Back-navigation without a scan returns null: no notice.
    if (result != null && mounted) setState(() => _scanResult = result);
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final detail = ref.watch(billDetailProvider(widget.billId));
    return AdaptiveScaffold(
      title: l10n.billsTitle,
      body: PageBody(
        child: switch (detail) {
          AsyncData(:final value) => _body(context, l10n, value),
          AsyncError(:final error) => Center(
            child: ErrorRetry(
              error: error,
              onRetry: () => ref.invalidate(billDetailProvider(widget.billId)),
            ),
          ),
          _ => const Center(child: CircularProgressIndicator.adaptive()),
        },
      ),
    );
  }

  Widget _body(BuildContext context, AppLocalizations l10n, BillDetail bill) {
    final issued = bill.status == BillStatusEnum.ISSUED;
    final paid = bill.status == BillStatusEnum.PAID;
    final voided = bill.status == BillStatusEnum.VOID;
    final dueDate = bill.dueDate?.toLocal();
    // DESIGN.md deadline vocabulary: unpaid past its due day is Mismatch Red
    // with the explicit word; unpaid-but-not-due keeps the quiet treatment.
    final now = DateTime.now();
    final overdue =
        issued &&
        dueDate != null &&
        DateTime(
          now.year,
          now.month,
          now.day,
        ).isAfter(DateTime(dueDate.year, dueDate.month, dueDate.day));
    final amountStyle = Theme.of(context).textTheme.headlineMedium?.copyWith(
      fontWeight: FontWeight.w700,
      fontFeatures: const [FontFeature.tabularFigures()],
    );

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Scan outcome where the eye lands on return, above the refreshed
        // status chip it explains. Only conclusive results pop the scanner.
        if (_scanResult case final scan?) ...[
          StatusNotice(
            tone: scan == BillScanResult.recorded
                ? StatusTone.success
                : StatusTone.error,
            message: scan == BillScanResult.recorded
                ? l10n.billPaymentRecorded
                : l10n.billPaymentVoided,
          ),
          const SizedBox(height: 16),
        ],
        Text(bill.title, style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 12),
        Text(formatVnd(bill.amountVnd), style: amountStyle),
        const SizedBox(height: 12),
        Align(
          alignment: Alignment.centerLeft,
          child: StatusChip(
            tone: paid
                ? StatusTone.success
                : voided
                ? StatusTone.error
                : StatusTone.warning,
            icon: paid
                ? Icons.check_circle_outline
                : voided
                ? Icons.cancel_outlined
                : Icons.schedule,
            label: paid
                ? l10n.billStatusPaid
                : voided
                ? l10n.billStatusVoid
                : l10n.billStatusIssued,
          ),
        ),
        if (dueDate != null) ...[
          const SizedBox(height: 24),
          ListTile(
            minTileHeight: 48,
            contentPadding: EdgeInsets.zero,
            title: Text(l10n.billDueLabel),
            trailing: overdue
                ? StatusChip(
                    tone: StatusTone.error,
                    icon: Icons.event_busy_outlined,
                    label:
                        '${DateFormat('dd/MM/yyyy').format(dueDate)}'
                        ' · ${l10n.billOverdue}',
                  )
                : Text(DateFormat('dd/MM/yyyy').format(dueDate)),
          ),
          const Divider(),
        ] else
          const SizedBox(height: 24),
        ListTile(
          minTileHeight: 56,
          contentPadding: EdgeInsets.zero,
          leading: const Icon(Icons.description_outlined),
          title: Text(l10n.billViewFile),
          subtitle: Text(bill.documentFilename),
          trailing: _openingDocument
              ? const SizedBox.square(
                  dimension: 24,
                  child: CircularProgressIndicator.adaptive(strokeWidth: 2),
                )
              : const Icon(Icons.open_in_new),
          onTap: _openingDocument ? null : () => _openDocument(bill),
        ),
        if (_documentFailed) ...[
          const SizedBox(height: 8),
          StatusNotice(
            tone: StatusTone.error,
            message: l10n.ledgerDocumentFailure,
          ),
        ],
        if (bill.note.isNotEmpty) ...[
          const Divider(),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 12),
            child: Text(bill.note),
          ),
        ],
        if (issued) ...[
          const SizedBox(height: 24),
          Text(l10n.billPayExplainer),
          const SizedBox(height: 8),
          Text(l10n.billPayStep1),
          Text(l10n.billPayStep2),
          const SizedBox(height: 16),
          AdaptiveFilledButton(
            onPressed: _scanPayment,
            child: Text(l10n.billPayAction),
          ),
        ],
      ],
    );
  }
}
