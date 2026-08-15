import 'dart:typed_data';

import 'package:built_value/json_object.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:lamto_api/lamto_api.dart';

import '../../core/error_retry.dart';
import '../../core/adaptive_buttons.dart';
import '../../core/adaptive_page_route.dart';
import '../../core/adaptive_scaffold.dart';
import '../../core/failure.dart';
import '../../core/format.dart';
import '../../core/page_body.dart';
import '../../l10n/app_localizations.dart';
import '../../theme.dart';
import '../documents/document_viewer_screen.dart';
import '../proposals/proposal_detail_screen.dart';
import '../transparency/transparency_repository.dart';
import 'evidence_explorer_tile.dart';
import 'evidence_labels.dart';

String _jsonField(JsonObject? object, String key) =>
    ((object?.value as Map?)?[key] ?? '').toString();

/// Ledger entry detail (spec 6.3(6) / A1): plain language first — what was
/// fixed, why, amount, who approved, payment verification — then expandable
/// proof. Mono identifiers appear ONLY inside the expansion.
class LedgerDetailScreen extends ConsumerWidget {
  const LedgerDetailScreen({required this.entryId, super.key});
  final int entryId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final detail = ref.watch(ledgerDetailProvider(entryId));
    return AdaptiveScaffold(
      title: l10n.ledgerDetailTitle,
      body: PageBody(
        child: switch (detail) {
          AsyncData(:final value) => _body(context, l10n, value),
          AsyncError(:final error) => Center(
            child: ErrorRetry(
              error: error,
              onRetry: () => ref.invalidate(ledgerDetailProvider(entryId)),
            ),
          ),
          _ => const Center(child: CircularProgressIndicator.adaptive()),
        },
      ),
    );
  }

  Widget _body(
    BuildContext context,
    AppLocalizations l10n,
    LedgerEntryDetail entry,
  ) {
    final date = DateFormat('dd/MM/yyyy').format(entry.publishedAt.toLocal());
    final verification = entry.verification;
    // Wire values (serializers.py effective_integrity_status): VERIFIED,
    // MISMATCH, UNAVAILABLE, UNCHECKED. Tampering (MISMATCH) must not dress
    // as routine pending, so it gets its own Mismatch Red conclusion; the
    // amber branch keeps the genuinely-pending states.
    final verified = entry.integrityStatus == 'VERIFIED';
    final mismatch = entry.integrityStatus == 'MISMATCH';
    final mono = Theme.of(context).textTheme.bodySmall?.copyWith(
      fontFamily: 'SFMono-Regular',
      fontFamilyFallback: const ['Menlo', 'Roboto Mono', 'monospace'],
    );
    final titleStyle = Theme.of(context).textTheme.titleMedium;
    final proposalId = (entry.payload?.value as Map?)?['proposal_id'] as int?;
    final conclusionColor = statusToneColors(
      context,
      verified
          ? StatusTone.success
          : mismatch
          ? StatusTone.error
          : StatusTone.warning,
    ).fg;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Semantics(
          container: true,
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(
                verified
                    ? Icons.verified_outlined
                    : mismatch
                    ? Icons.error_outline
                    : Icons.pending_outlined,
                color: conclusionColor,
                size: 32,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      verified
                          ? l10n.ledgerConclusionVerified
                          : mismatch
                          ? l10n.ledgerConclusionMismatch
                          : l10n.ledgerConclusionUnverified,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        color: conclusionColor,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      verified
                          ? l10n.ledgerConclusionVerifiedBody
                          : mismatch
                          ? l10n.ledgerConclusionMismatchBody
                          : l10n.ledgerConclusionUnverifiedBody,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),
        if (proposalId != null) ...[
          ListTile(
            minTileHeight: 48,
            contentPadding: EdgeInsets.zero,
            title: Text(l10n.proposalViewFromLedger),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => Navigator.push(
              context,
              adaptivePageRoute(
                builder: (_) => ProposalDetailScreen(proposalId: proposalId),
              ),
            ),
          ),
          const Divider(),
        ],
        Text(l10n.ledgerChainTitle, style: titleStyle),
        const SizedBox(height: 4),
        Text(l10n.ledgerChainHint),
        _ChainStep(number: 1, title: l10n.ledgerChainReports, body: entry.why),
        _ChainStep(
          number: 2,
          title: l10n.ledgerChainWork,
          body: entry.whatWasFixed,
        ),
        _ChainStep(
          number: 3,
          title: l10n.ledgerChainApprovals,
          body: entry.approvers
              .map(
                (a) => approverLine(
                  _jsonField(a, 'role'),
                  _jsonField(a, 'name'),
                  l10n,
                ),
              )
              .join('\n'),
        ),
        _ChainStep(
          number: 4,
          title: l10n.ledgerChainPayment,
          body:
              '${l10n.ledgerAmount}: ${formatVnd(entry.actualCostVnd)}\n'
              '${l10n.ledgerContractor}: ${entry.contractorName}\n'
              '${l10n.ledgerPublishedOn(date)}',
        ),
        _ChainStep(
          number: 5,
          title: l10n.ledgerChainVerification,
          body: [
            if (verification != null)
              l10n.ledgerVerifiedBy(verification.verifiedBy),
            integrityStatusLabel(entry.integrityStatus, l10n),
          ].join('\n'),
          child: Padding(
            padding: const EdgeInsets.only(top: 8),
            child: EvidenceBadge(level: entry.proof.evidenceLevel),
          ),
        ),
        const SizedBox(height: 16),
        Text(l10n.ledgerDocuments, style: titleStyle),
        if (entry.documents.isNotEmpty)
          for (final doc in entry.documents) _DocumentTile(document: doc),
        const Divider(height: 32),
        if (entry.explorerUrl != null && entry.explorerUrl!.isNotEmpty)
          EvidenceExplorerTile(url: entry.explorerUrl!)
        else
          ExpansionTile(
            tilePadding: EdgeInsets.zero,
            childrenPadding: const EdgeInsets.only(bottom: 16),
            title: Text(l10n.ledgerProofTitle, style: titleStyle),
            children: [
              ListTile(
                contentPadding: EdgeInsets.zero,
                title: Text(l10n.ledgerProofHash),
                subtitle: Text(entry.proof.payloadHash, style: mono),
              ),
              Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  l10n.ledgerProofEvents,
                  style: Theme.of(context).textTheme.labelLarge,
                ),
              ),
              for (final event in entry.proof.events)
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  title: Text(event.eventId, style: mono),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (event.transactionHash.isNotEmpty)
                        Text(event.transactionHash, style: mono),
                      const SizedBox(height: 4),
                      EvidenceBadge(level: event.evidenceLevel),
                    ],
                  ),
                ),
            ],
          ),
        if (entry.corrections.isNotEmpty) ...[
          const SizedBox(height: 24),
          Text(l10n.ledgerCorrections, style: titleStyle),
          for (final correction in entry.corrections)
            ListTile(
              minTileHeight: 48,
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.change_circle_outlined),
              title: Text(_jsonField(correction, 'reason')),
              subtitle: Text(l10n.ledgerCorrectionRecorded),
            ),
        ],
      ],
    );
  }
}

class _ChainStep extends StatelessWidget {
  const _ChainStep({
    required this.number,
    required this.title,
    required this.body,
    this.child,
  });

  final int number;
  final String title;
  final String body;
  final Widget? child;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          CircleAvatar(
            radius: 16,
            backgroundColor: Theme.of(context).colorScheme.secondaryContainer,
            foregroundColor: Theme.of(context).colorScheme.onSecondaryContainer,
            child: Text('$number'),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: Theme.of(context).textTheme.titleMedium),
                if (body.isNotEmpty) ...[const SizedBox(height: 4), Text(body)],
                ?child,
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _DocumentTile extends ConsumerStatefulWidget {
  const _DocumentTile({required this.document});
  final LedgerDocument document;

  @override
  ConsumerState<_DocumentTile> createState() => _DocumentTileState();
}

class _DocumentTileState extends ConsumerState<_DocumentTile> {
  bool _loading = false;
  Object? _error;

  String _errorMessage(AppLocalizations l10n) {
    final failure = Failure.fromObject(_error!);
    return switch (failure.code) {
      'network_error' => l10n.ledgerDocumentOffline,
      'not_authenticated' ||
      'permission_denied' => l10n.ledgerDocumentUnauthorized,
      _ => l10n.ledgerDocumentFailure,
    };
  }

  Future<void> _open() async {
    if (_loading) return;
    setState(() {
      _loading = true;
      _error = null;
    });
    final Uint8List bytes;
    try {
      bytes = await ref
          .read(transparencyRepositoryProvider)
          .fetchDocument(widget.document.downloadUrl);
    } catch (error) {
      // Fetch failures belong to this row, with a retry. Render failures
      // belong to the viewer, so it is opened outside this try.
      if (mounted) setState(() => _error = error);
      return;
    } finally {
      if (mounted) setState(() => _loading = false);
    }
    if (!mounted) return;
    await showDocumentViewer(
      context,
      bytes: bytes,
      filename: widget.document.filename,
      contentType: widget.document.contentType,
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return ListTile(
      minTileHeight: 56,
      contentPadding: EdgeInsets.zero,
      leading: const Icon(Icons.description_outlined),
      title: Text(ledgerDocumentKindLabel(widget.document.kind, l10n)),
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(widget.document.filename),
          Text(_error == null ? l10n.ledgerDocumentOpen : _errorMessage(l10n)),
          if (_error != null)
            Align(
              alignment: Alignment.centerLeft,
              child: AdaptiveTextButton(
                onPressed: _open,
                child: Text(l10n.commonRetry),
              ),
            ),
        ],
      ),
      trailing: _loading
          ? const SizedBox.square(
              dimension: 24,
              child: CircularProgressIndicator.adaptive(strokeWidth: 2),
            )
          : _error == null
          ? const Icon(Icons.chevron_right)
          : null,
      onTap: _loading ? null : _open,
    );
  }
}
