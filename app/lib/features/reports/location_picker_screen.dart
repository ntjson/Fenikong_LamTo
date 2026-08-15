import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lamto_api/lamto_api.dart';

import '../../core/error_retry.dart';
import '../../core/adaptive_scaffold.dart';
import '../../core/page_body.dart';
import '../../l10n/app_localizations.dart';
import 'reports_repository.dart';

/// Drill-down location tree (spec 6.3): large rows, explicit selection at
/// every level — no gesture-only affordances.
class LocationPickerScreen extends ConsumerStatefulWidget {
  const LocationPickerScreen({super.key});

  @override
  ConsumerState<LocationPickerScreen> createState() =>
      _LocationPickerScreenState();
}

class _LocationPickerScreenState extends ConsumerState<LocationPickerScreen> {
  /// Drill path: null root -> deeper parents.
  final List<Location> _path = [];

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final locations = ref.watch(locationsProvider);
    final parent = _path.isEmpty ? null : _path.last;

    return PopScope(
      canPop: _path.isEmpty,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop) setState(() => _path.removeLast());
      },
      child: AdaptiveScaffold(
        title: parent?.name ?? l10n.locationPickerTitle,
        body: PageBody(
          child: switch (locations) {
            AsyncData(:final value) => _list(context, l10n, value, parent),
            AsyncError(:final error) => Center(
              child: ErrorRetry(
                error: error,
                onRetry: () => ref.invalidate(locationsProvider),
              ),
            ),
            _ => const Center(child: CircularProgressIndicator.adaptive()),
          },
        ),
      ),
    );
  }

  Widget _list(
    BuildContext context,
    AppLocalizations l10n,
    List<Location> all,
    Location? parent,
  ) {
    final children = all.where((loc) => loc.parentId == parent?.id).toList();
    final hasChildren = {
      for (final loc in all)
        if (loc.parentId != null) loc.parentId!,
    };
    return ListView(
      children: [
        if (parent != null)
          ListTile(
            minTileHeight: 56,
            leading: const Icon(Icons.check_circle_outline),
            title: Text(l10n.locationChooseHere),
            subtitle: Text(parent.name),
            onTap: () => Navigator.pop(context, parent),
          ),
        for (final loc in children)
          ListTile(
            minTileHeight: 56,
            title: Text(loc.name),
            trailing: hasChildren.contains(loc.id)
                ? const Icon(Icons.chevron_right)
                : null,
            onTap: () {
              if (hasChildren.contains(loc.id)) {
                setState(() => _path.add(loc));
              } else {
                Navigator.pop(context, loc);
              }
            },
          ),
      ],
    );
  }
}
