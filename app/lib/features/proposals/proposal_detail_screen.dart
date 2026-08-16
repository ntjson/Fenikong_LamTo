import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:lamto_api/lamto_api.dart';

import '../../core/error_retry.dart';
import '../../core/adaptive_buttons.dart';
import '../../core/adaptive_scaffold.dart';
import '../../core/failure.dart';
import '../../core/format.dart';
import '../../core/page_body.dart';
import '../../l10n/app_localizations.dart';
import '../../theme.dart';
import '../ledger/evidence_explorer_tile.dart';
import '../ledger/evidence_labels.dart';
import 'proposals_list_screen.dart';
import 'proposals_repository.dart';

class ProposalDetailScreen extends ConsumerStatefulWidget {
  const ProposalDetailScreen({required this.proposalId, super.key});

  final int proposalId;

  @override
  ConsumerState<ProposalDetailScreen> createState() =>
      _ProposalDetailScreenState();
}

class _ProposalDetailScreenState extends ConsumerState<ProposalDetailScreen> {
  /// Shows the inline thanks notice after a rating — SnackBars never render
  /// under the iOS Cupertino shell.
  bool _rated = false;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final proposal = ref.watch(proposalDetailProvider(widget.proposalId));
    return AdaptiveScaffold(
      title: l10n.proposalsSegment,
      body: PageBody(
        child: switch (proposal) {
          AsyncData(:final value) => _body(context, ref, l10n, value),
          AsyncError(:final error) => Center(
            child: ErrorRetry(
              error: error,
              onRetry: () =>
                  ref.invalidate(proposalDetailProvider(widget.proposalId)),
            ),
          ),
          _ => const Center(child: CircularProgressIndicator.adaptive()),
        },
      ),
    );
  }

  Widget _body(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    Proposal proposal,
  ) {
    final settlement = proposal.settlement;
    final titleStyle = Theme.of(context).textTheme.titleMedium;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Align(
          alignment: Alignment.centerLeft,
          child: StatusChip(
            tone: proposalStatusTone(proposal.status),
            label: proposalStatusLabel(proposal.status, l10n),
          ),
        ),
        _Field(l10n.proposalProblem, proposal.purpose),
        _Field(l10n.proposalAction, proposal.proposedAction),
        _Field(l10n.proposalCost, formatVnd(proposal.amountVnd), amount: true),
        if (proposal.comparison != null)
          _PriceComparisonField(comparison: proposal.comparison!),
        _Field(l10n.proposalContractor, proposal.contractorName),
        _Field(l10n.proposalSchedule, proposal.expectedSchedule),
        const Divider(height: 32),
        Text(l10n.proposalVersions, style: titleStyle),
        for (final version in proposal.versions) ...[
          ListTile(
            contentPadding: EdgeInsets.zero,
            title: Text(l10n.proposalVersion('${version.number}')),
            subtitle: Text(_date(version.publishedAt)),
            trailing: EvidenceBadge(level: version.evidenceLevel),
          ),
          for (final document in version.supportingDocuments)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 0, 8),
              child: Row(
                children: [
                  const Icon(Icons.description_outlined),
                  const SizedBox(width: 12),
                  Expanded(child: Text(document.filename)),
                ],
              ),
            ),
        ],
        if (proposal.progress.isNotEmpty) ...[
          const Divider(height: 32),
          Text(l10n.progressTitle, style: titleStyle),
          for (final update in proposal.progress)
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.build_outlined),
              title: Text(update.result),
              subtitle: Text('${update.cause} · ${_date(update.createdAt)}'),
            ),
        ],
        if (settlement != null) ...[
          const Divider(height: 32),
          Text(l10n.proposalSettlement, style: titleStyle),
          const SizedBox(height: 8),
          Text(l10n.proposalSettled),
        ],
        if (proposal.explorerUrl != null &&
            proposal.explorerUrl!.isNotEmpty) ...[
          const Divider(height: 32),
          EvidenceExplorerTile(url: proposal.explorerUrl!),
        ],
        // Inline where the rate CTA sits (visible on iOS, unlike a SnackBar).
        if (_rated) ...[
          const SizedBox(height: 24),
          StatusNotice(tone: StatusTone.success, message: l10n.rateThanks),
        ],
        if (proposal.status == 'COMPLETED' && proposal.canRate) ...[
          const SizedBox(height: 24),
          AdaptiveFilledButton(
            icon: const Icon(Icons.star_outline),
            child: Text(l10n.proposalRateCta),
            onPressed: () => _openRating(context),
          ),
        ],
      ],
    );
  }

  Future<void> _openRating(BuildContext context) async {
    final rated = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      builder: (_) => _RateProposalSheet(proposalId: widget.proposalId),
    );
    if (rated == true && mounted) {
      ref.invalidate(proposalDetailProvider(widget.proposalId));
      setState(() => _rated = true);
    }
  }
}

String _date(DateTime value) =>
    DateFormat('dd/MM/yyyy').format(value.toLocal());

class _Field extends StatelessWidget {
  const _Field(this.label, this.value, {this.amount = false});

  final String label;
  final Object? value;
  final bool amount;

  @override
  Widget build(BuildContext context) => ListTile(
    contentPadding: EdgeInsets.zero,
    title: Text(label),
    subtitle: Text(
      value?.toString() ?? '',
      style: amount ? listAmountStyle(context) : null,
    ),
  );
}

class _PriceComparisonField extends StatelessWidget {
  const _PriceComparisonField({required this.comparison});

  final ProposalComparison comparison;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final direction = comparison.direction;

    final String arrow;
    final Color? arrowColor;
    final String comparisonText;

    if (direction == 'below') {
      arrow = '↓';
      arrowColor = statusToneColors(context, StatusTone.success).fg;
      comparisonText = l10n.proposalPriceComparisonBelow(
        comparison.percentage,
        comparison.range,
      );
    } else if (direction == 'above') {
      arrow = '↑';
      arrowColor = statusToneColors(context, StatusTone.error).fg;
      comparisonText = l10n.proposalPriceComparisonAbove(
        comparison.percentage,
        comparison.range,
      );
    } else {
      arrow = '';
      arrowColor = null;
      comparisonText = l10n.proposalPriceComparisonEqual;
    }

    final mutedColor = Theme.of(context).colorScheme.onSurfaceVariant;
    final textTheme = Theme.of(context).textTheme;

    return ListTile(
      contentPadding: EdgeInsets.zero,
      title: Text(l10n.proposalPriceComparison),
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 2),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (arrow.isNotEmpty) ...[
                Text(
                  arrow,
                  style: TextStyle(
                    color: arrowColor,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(width: 4),
              ],
              Expanded(
                child: Text(
                  comparisonText,
                ),
              ),
            ],
          ),
          if (comparison.reasoning.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(
              comparison.reasoning,
              style: textTheme.bodySmall?.copyWith(color: mutedColor),
            ),
          ],
          const SizedBox(height: 4),
          Text(
            l10n.proposalPriceComparisonCaveat,
            style: textTheme.bodySmall?.copyWith(color: mutedColor),
          ),
        ],
      ),
    );
  }
}

class _RateProposalSheet extends ConsumerStatefulWidget {
  const _RateProposalSheet({required this.proposalId});

  final int proposalId;

  @override
  ConsumerState<_RateProposalSheet> createState() => _RateProposalSheetState();
}

class _RateProposalSheetState extends ConsumerState<_RateProposalSheet> {
  bool _satisfied = true;
  final _comment = TextEditingController();
  bool _busy = false;
  String? _error;

  @override
  void dispose() {
    _comment.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Padding(
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: 16,
        bottom: 16 + MediaQuery.viewInsetsOf(context).bottom,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            l10n.rateWorkTitle,
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          SegmentedButton<bool>(
            segments: [
              ButtonSegment(value: true, label: Text(l10n.rateSatisfied)),
              ButtonSegment(value: false, label: Text(l10n.rateNotSatisfied)),
            ],
            selected: {_satisfied},
            onSelectionChanged: _busy
                ? null
                : (value) => setState(() => _satisfied = value.first),
          ),
          TextField(
            controller: _comment,
            maxLength: 500,
            decoration: InputDecoration(labelText: l10n.rateCommentLabel),
          ),
          if (_error != null)
            Text(
              _error!,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
          const SizedBox(height: 8),
          AdaptiveFilledButton(
            onPressed: _busy ? null : _submit,
            child: Text(l10n.rateSubmit),
          ),
        ],
      ),
    );
  }

  Future<void> _submit() async {
    final l10n = AppLocalizations.of(context)!;
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await ref
          .read(proposalsRepositoryProvider)
          .rateProposal(
            id: widget.proposalId,
            satisfied: _satisfied,
            comment: _comment.text.trim(),
          );
      if (mounted) Navigator.pop(context, true);
    } catch (error) {
      if (mounted) {
        setState(
          () => _error = failureMessage(Failure.fromObject(error), l10n),
        );
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }
}
