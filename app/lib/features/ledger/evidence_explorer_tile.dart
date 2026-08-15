import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../l10n/app_localizations.dart';

/// Reusable Evidence explorer link row (spec 6.3(11) / issue 07 & 08).
///
/// Tapping opens the public Evidence explorer page in the device's external
/// browser so the full URL is visible and shareable.
class EvidenceExplorerTile extends StatelessWidget {
  const EvidenceExplorerTile({required this.url, super.key});

  final String url;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final titleStyle = Theme.of(context).textTheme.titleMedium;
    return ListTile(
      minTileHeight: 48,
      contentPadding: EdgeInsets.zero,
      title: Text(l10n.evidenceExplorer, style: titleStyle),
      trailing: const Icon(Icons.open_in_new),
      onTap: () async {
        final uri = Uri.tryParse(url);
        if (uri != null) {
          await launchUrl(uri, mode: LaunchMode.externalApplication);
        }
      },
    );
  }
}
