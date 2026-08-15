import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/adaptive_buttons.dart';
import '../../core/adaptive_page_route.dart';
import '../../core/failure.dart';
import '../../core/providers.dart';
import '../../l10n/app_localizations.dart';
import '../auth/session_controller.dart';
import '../reports/reports_repository.dart';
import '../settings/api_base_url_tile.dart';
import '../transparency/transparency_repository.dart';
import '../gate/gate_registration_screen.dart';

/// Resident notification event codes (server defaults absent rows to
/// enabled). One master switch drives every code on both channels.
const residentPreferenceCodes = [
  'report.receipt',
  'triage.status',
  'work.completed',
  'ledger.publication',
  'correction.status',
  'building.announcement',
];

/// Account tab (spec 6.3(7)). Body-only: the shell owns chrome.
class AccountScreen extends ConsumerStatefulWidget {
  const AccountScreen({super.key});

  @override
  ConsumerState<AccountScreen> createState() => _AccountScreenState();
}

class _AccountScreenState extends ConsumerState<AccountScreen> {
  /// Local overlay of the master toggle after the user flipped it.
  bool? _all;

  /// Last preference PATCH failure (resident copy). Inline — not SnackBar —
  /// so the message works under iOS [CupertinoPageScaffold] (no Material
  /// Scaffold / snack-bar host).
  String? _prefError;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final session = ref.watch(sessionControllerProvider);
    final me = switch (session) {
      AsyncData(value: SessionAuthenticated(:final me)) => me,
      _ => null,
    };
    if (me == null) {
      return const Center(child: CircularProgressIndicator.adaptive());
    }
    final holder = ref.watch(occupancyHolderProvider);
    // Absent rows default to enabled server-side, so present rows decide.
    final serverAll = me.notificationPreferences.every(
      (pref) => pref.emailEnabled && pref.pushEnabled,
    );

    return Material(
      color: Colors.transparent,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(me.displayName, style: Theme.of(context).textTheme.titleLarge),
            if (me.email != null && me.email!.isNotEmpty)
              Text(me.email!, style: Theme.of(context).textTheme.bodySmall),
            if (me.phone != null && me.phone!.isNotEmpty)
              Text(me.phone!, style: Theme.of(context).textTheme.bodySmall),
            const SizedBox(height: 24),
            Text(
              l10n.accountOccupancies,
              style: Theme.of(context).textTheme.titleMedium,
            ),
            RadioGroup<int>(
              groupValue: holder.occupancyId,
              onChanged: (id) {
                if (id != null) {
                  ref
                      .read(sessionControllerProvider.notifier)
                      .selectOccupancy(me, id);
                }
              },
              child: Column(
                children: [
                  for (final occupancy in me.occupancies)
                    RadioListTile<int>(
                      contentPadding: EdgeInsets.zero,
                      value: occupancy.id,
                      title: Text(
                        '${occupancy.buildingName} · ${occupancy.unitLabel}',
                      ),
                    ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            Text(
              l10n.accountPreferences,
              style: Theme.of(context).textTheme.titleMedium,
            ),
            if (_prefError != null) ...[
              const SizedBox(height: 8),
              Text(
                _prefError!,
                key: const Key('account_pref_error'),
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.error,
                ),
              ),
            ],
            SwitchListTile.adaptive(
              key: const Key('notifications_all'),
              contentPadding: EdgeInsets.zero,
              title: Text(l10n.accountPrefAll),
              value: _all ?? serverAll,
              onChanged: _setAll,
            ),
            const SizedBox(height: 24),
            AdaptiveOutlinedButton(
              onPressed: () => Navigator.of(context).push(
                adaptivePageRoute<void>(
                  builder: (_) => GateRegistrationScreen(
                    repository: ref.read(gateRepositoryProvider),
                  ),
                ),
              ),
              icon: const Icon(Icons.door_front_door_outlined),
              child: Text(l10n.gateAccountAction),
            ),
            const SizedBox(height: 24),
            const ApiBaseUrlTile(),
            const SizedBox(height: 24),
            // Session actions, not the tab's primary CTA: outlined/text, never
            // the filled Accountability Indigo reserved for primary actions.
            AdaptiveOutlinedButton(
              fullWidth: true,
              onPressed: () => _confirmSignOut(),
              child: Text(l10n.signOut),
            ),
            const SizedBox(height: 8),
            AdaptiveTextButton(
              fullWidth: true,
              onPressed: () => _confirmSignOut(allDevices: true),
              child: Text(l10n.accountSignOutAll),
            ),
          ],
        ),
      ),
    );
  }

  /// Sign-out destroys unsent work on this device ([ReportDraftStore.clearAll]
  /// wipes report drafts and pending reply photos), so it confirms first.
  /// The consequence line appears only when such work actually exists.
  Future<void> _confirmSignOut({bool allDevices = false}) async {
    final l10n = AppLocalizations.of(context)!;
    final hasUnsentWork = await ref
        .read(reportDraftStoreProvider)
        .hasUnsentWork();
    if (!mounted) return;
    final title = allDevices ? l10n.accountSignOutAll : l10n.signOut;
    final warning = hasUnsentWork ? l10n.signOutUnsentWorkWarning : null;
    final confirmed = defaultTargetPlatform == TargetPlatform.iOS
        ? await showCupertinoDialog<bool>(
            context: context,
            builder: (context) => CupertinoAlertDialog(
              title: Text(title),
              content: warning == null ? null : Text(warning),
              actions: [
                CupertinoDialogAction(
                  isDefaultAction: true,
                  onPressed: () => Navigator.pop(context, false),
                  child: Text(l10n.commonCancel),
                ),
                CupertinoDialogAction(
                  isDestructiveAction: true,
                  onPressed: () => Navigator.pop(context, true),
                  child: Text(l10n.signOut),
                ),
              ],
            ),
          )
        : await showDialog<bool>(
            context: context,
            builder: (context) => AlertDialog(
              title: Text(title),
              content: warning == null ? null : Text(warning),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context, false),
                  child: Text(l10n.commonCancel),
                ),
                TextButton(
                  style: TextButton.styleFrom(
                    foregroundColor: Theme.of(context).colorScheme.error,
                  ),
                  onPressed: () => Navigator.pop(context, true),
                  child: Text(l10n.signOut),
                ),
              ],
            ),
          );
    if (confirmed == true && mounted) {
      await ref
          .read(sessionControllerProvider.notifier)
          .signOut(allDevices: allDevices);
    }
  }

  Future<void> _setAll(bool value) async {
    setState(() {
      _all = value;
      _prefError = null;
    });
    try {
      // ponytail: sequential per-code PATCH (no bulk endpoint); a mid-loop
      // failure leaves earlier codes applied — the revert + retry covers it.
      for (final code in residentPreferenceCodes) {
        await ref
            .read(transparencyRepositoryProvider)
            .updatePreference(
              eventCode: code,
              emailEnabled: value,
              pushEnabled: value,
            );
      }
    } catch (error) {
      // Revert the optimistic flip on failure and surface resident copy.
      // Inline error only — SnackBar needs a Material Scaffold host that
      // iOS CupertinoPageScaffold (HomeShell) does not provide.
      if (!mounted) return;
      final l10n = AppLocalizations.of(context)!;
      setState(() {
        _all = !value;
        _prefError = failureMessage(Failure.fromObject(error), l10n);
      });
    }
  }
}
