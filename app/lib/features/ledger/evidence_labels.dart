import 'package:flutter/material.dart';

import '../../l10n/app_localizations.dart';
import '../../theme.dart';

/// Distinct presentation per evidence level (spec 5.1/5.2): LOCAL_SIGNED never
/// borrows chain wording; MISMATCH renders prominently; color never alone.
String evidenceLevelLabel(String level, AppLocalizations l10n) =>
    switch (level) {
      'CHAIN_CONFIRMED' => l10n.evidenceChain,
      'LOCAL_SIGNED' => l10n.evidenceLocal,
      'MISMATCH' => l10n.evidenceMismatch,
      _ => l10n.evidencePending,
    };

String integrityStatusLabel(String status, AppLocalizations l10n) =>
    switch (status) {
      'VERIFIED' => l10n.integrityVerified,
      'MISMATCH' => l10n.integrityMismatch,
      'UNAVAILABLE' => l10n.integrityUnavailable,
      _ => l10n.integrityUnchecked,
    };

/// Role-aware approver line for the plain-language story (A1).
String approverLine(String role, String name, AppLocalizations l10n) =>
    switch (role) {
      'board' => l10n.ledgerApproverBoard(name),
      'resident_rep' => l10n.ledgerApproverRep(name),
      'emergency' => l10n.ledgerApproverEmergency(name),
      _ => l10n.ledgerApproverGeneric(name),
    };

(StatusTone, IconData) _styleFor(String level) => switch (level) {
  'CHAIN_CONFIRMED' => (StatusTone.success, Icons.verified_outlined),
  'MISMATCH' => (StatusTone.error, Icons.error_outline),
  'LOCAL_SIGNED' => (StatusTone.info, Icons.lock_outline),
  _ => (StatusTone.warning, Icons.hourglass_empty),
};

class EvidenceBadge extends StatelessWidget {
  const EvidenceBadge({required this.level, super.key});
  final String level;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final (tone, icon) = _styleFor(level);
    return StatusChip(
      tone: tone,
      icon: icon,
      label: evidenceLevelLabel(level, l10n),
    );
  }
}
