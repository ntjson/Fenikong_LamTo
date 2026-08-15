import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lamto_api/lamto_api.dart';

import '../../core/adaptive_buttons.dart';
import '../../core/adaptive_page_route.dart';
import '../../core/adaptive_scaffold.dart';
import '../../core/error_retry.dart';
import '../../core/format.dart';
import '../../core/page_body.dart';
import '../../l10n/app_localizations.dart';
import '../../theme.dart';
import 'bill_detail_screen.dart';
import 'bills_repository.dart';

class BillsScreen extends ConsumerWidget {
  const BillsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final bills = ref.watch(billsProvider);
    return AdaptiveScaffold(
      title: l10n.billsTitle,
      body: PageBody(
        child: switch (bills) {
          AsyncData(:final value) => _list(context, l10n, value),
          AsyncError(:final error) => Center(
            child: ErrorRetry(
              error: error,
              onRetry: () => ref.invalidate(billsProvider),
            ),
          ),
          _ => const Center(child: CircularProgressIndicator.adaptive()),
        },
      ),
    );
  }

  Widget _list(
    BuildContext context,
    AppLocalizations l10n,
    List<BillSummary> bills,
  ) => ListView(
    physics: const AlwaysScrollableScrollPhysics(),
    padding: const EdgeInsets.symmetric(horizontal: 16),
    children: [
      if (bills.isEmpty)
        Padding(
          padding: const EdgeInsets.only(top: 120),
          child: Center(
            child: Column(
              children: [
                Text(l10n.billNone),
                const SizedBox(height: 12),
                AdaptiveOutlinedButton(
                  onPressed: () => Navigator.maybePop(context),
                  child: Text(
                    MaterialLocalizations.of(context).backButtonTooltip,
                  ),
                ),
              ],
            ),
          ),
        ),
      for (final bill in bills) ...[
        ListTile(
          minTileHeight: 64,
          contentPadding: EdgeInsets.zero,
          title: Text(switch (bill.status) {
            BillStatusEnum.PAID => l10n.billStatusPaid,
            BillStatusEnum.VOID => l10n.billStatusVoid,
            _ => l10n.billStatusIssued,
          }),
          subtitle: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(bill.title),
              Text(formatVnd(bill.amountVnd), style: listAmountStyle(context)),
            ],
          ),
          trailing: StatusChip(
            tone: switch (bill.status) {
              BillStatusEnum.PAID => StatusTone.success,
              BillStatusEnum.VOID => StatusTone.error,
              _ => StatusTone.warning,
            },
            label: switch (bill.status) {
              BillStatusEnum.PAID => l10n.billStatusPaid,
              BillStatusEnum.VOID => l10n.billStatusVoid,
              _ => l10n.billStatusIssued,
            },
          ),
          onTap: () => Navigator.push(
            context,
            adaptivePageRoute(
              builder: (_) => BillDetailScreen(billId: bill.id),
            ),
          ),
        ),
        const Divider(height: 1),
      ],
    ],
  );
}
