import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/adaptive_buttons.dart';
import '../../core/api_base_url.dart';
import '../../core/providers.dart';
import '../../l10n/app_localizations.dart';
import '../../theme.dart';
import '../auth/session_controller.dart';

/// Collapsible API server URL editor (login + account).
///
/// Lets a installed APK retarget a new Cloudflare quick-tunnel URL without
/// rebuilding. Saving signs the user out so the next login hits the new host.
class ApiBaseUrlTile extends ConsumerStatefulWidget {
  const ApiBaseUrlTile({super.key, this.initiallyExpanded = false});

  final bool initiallyExpanded;

  @override
  ConsumerState<ApiBaseUrlTile> createState() => _ApiBaseUrlTileState();
}

class _ApiBaseUrlTileState extends ConsumerState<ApiBaseUrlTile> {
  late final TextEditingController _controller;
  String? _error;
  bool _busy = false;

  /// Inline saved confirmation — a SnackBar has no Material Scaffold host
  /// under the iOS Cupertino shell, so it would never render there.
  bool _saved = false;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: ref.read(apiBaseUrlProvider));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _save(AppLocalizations l10n) async {
    setState(() {
      _busy = true;
      _error = null;
      _saved = false;
    });
    try {
      await ref.read(apiBaseUrlProvider.notifier).setUrl(_controller.text);
      // Old knox tokens belong to the previous host.
      await ref.read(sessionControllerProvider.notifier).signOut();
      if (mounted) setState(() => _saved = true);
    } on FormatException {
      if (mounted) setState(() => _error = l10n.apiBaseUrlInvalid);
    } catch (_) {
      if (mounted) setState(() => _error = l10n.errGeneric);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _reset(AppLocalizations l10n) async {
    setState(() {
      _busy = true;
      _error = null;
      _saved = false;
    });
    try {
      await ref.read(apiBaseUrlProvider.notifier).clearOverride();
      _controller.text = ref.read(apiBaseUrlProvider);
      await ref.read(sessionControllerProvider.notifier).signOut();
      if (mounted) setState(() => _saved = true);
    } catch (_) {
      if (mounted) setState(() => _error = l10n.errGeneric);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final current = ref.watch(apiBaseUrlProvider);
    ref.listen<String>(apiBaseUrlProvider, (prev, next) {
      if (_busy) return;
      if (_controller.text.trim().isEmpty ||
          normalizeApiBaseUrl(_controller.text) == prev) {
        _controller.text = next;
      }
    });

    return ExpansionTile(
      key: const Key('api_base_url_tile'),
      initiallyExpanded: widget.initiallyExpanded,
      title: Text(l10n.apiBaseUrlTitle),
      subtitle: Text(
        current,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
        style: Theme.of(context).textTheme.bodySmall,
      ),
      childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
      children: [
        Text(l10n.apiBaseUrlHelp, style: Theme.of(context).textTheme.bodySmall),
        const SizedBox(height: 12),
        TextField(
          key: const Key('api_base_url_field'),
          controller: _controller,
          decoration: InputDecoration(
            labelText: l10n.apiBaseUrlLabel,
            hintText: 'https://….trycloudflare.com',
          ),
          keyboardType: TextInputType.url,
          autocorrect: false,
          enableSuggestions: false,
          textInputAction: TextInputAction.done,
          onSubmitted: (_) => _busy ? null : _save(l10n),
        ),
        if (_error != null) ...[
          const SizedBox(height: 8),
          Text(
            _error!,
            style: TextStyle(color: Theme.of(context).colorScheme.error),
          ),
        ],
        if (_saved) ...[
          const SizedBox(height: 8),
          StatusNotice(tone: StatusTone.success, message: l10n.apiBaseUrlSaved),
        ],
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: AdaptiveFilledButton(
                key: const Key('api_base_url_save'),
                onPressed: _busy ? null : () => _save(l10n),
                child: Text(l10n.apiBaseUrlSave),
              ),
            ),
            const SizedBox(width: 8),
            AdaptiveTextButton(
              key: const Key('api_base_url_reset'),
              onPressed: _busy ? null : () => _reset(l10n),
              child: Text(l10n.apiBaseUrlReset),
            ),
          ],
        ),
      ],
    );
  }
}
