import 'package:flutter/material.dart';

import '../l10n/app_localizations.dart';
import 'adaptive_buttons.dart';
import 'failure.dart';

/// Load-more control shared by the cursor-paginated lists. Disables itself
/// while the page is in flight (no double-tap duplicate pages) and surfaces a
/// failed page inline, keeping the button available as the retry action.
class LoadMoreButton extends StatefulWidget {
  const LoadMoreButton({
    required this.label,
    required this.onLoadMore,
    super.key,
  });

  final String label;
  final Future<void> Function() onLoadMore;

  @override
  State<LoadMoreButton> createState() => _LoadMoreButtonState();
}

class _LoadMoreButtonState extends State<LoadMoreButton> {
  bool _busy = false;
  Failure? _failure;

  Future<void> _load() async {
    setState(() {
      _busy = true;
      _failure = null;
    });
    try {
      await widget.onLoadMore();
    } catch (e) {
      if (mounted) setState(() => _failure = Failure.fromObject(e));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 88),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (_failure != null) ...[
            Text(
              failureMessage(_failure!, l10n),
              textAlign: TextAlign.center,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
            const SizedBox(height: 8),
          ],
          AdaptiveOutlinedButton(
            busy: _busy,
            onPressed: _busy ? null : _load,
            child: Text(widget.label),
          ),
        ],
      ),
    );
  }
}
