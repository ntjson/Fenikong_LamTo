import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

/// Platform button vocabulary (DESIGN.md §5: native roles at 44pt / 48dp).
/// Material's filled / outlined / text roles map onto Cupertino's filled and
/// plain roles — iOS has no outlined button; secondary and tertiary actions
/// are both plain, weight comes from filled vs not (the pattern the
/// registration screens established). Colors flow from the app theme via
/// [CupertinoTheme], so dark mode keeps working on both platforms.

bool get _isCupertino => defaultTargetPlatform == TargetPlatform.iOS;

Widget _withIcon(Widget? icon, Widget child) => icon == null
    ? child
    : Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          icon,
          const SizedBox(width: 8),
          Flexible(child: child),
        ],
      );

/// Overlays a small activity indicator on an invisible copy of the label, so
/// a busy button keeps its laid-out size (no width/height jump) and screen
/// readers keep the action name.
Widget _busyOverlay(Widget child) => Stack(
  clipBehavior: Clip.none,
  children: [
    Opacity(opacity: 0, alwaysIncludeSemantics: true, child: child),
    // Positioned: contributes nothing to the Stack's size, so the button's
    // geometry is exactly the label's.
    const Positioned.fill(
      child: Center(
        child: SizedBox.square(
          dimension: 18,
          child: CircularProgressIndicator.adaptive(strokeWidth: 2),
        ),
      ),
    ),
  ],
);

/// Primary action: [CupertinoButton.filled] on iOS, [FilledButton] elsewhere.
/// [tonal] lowers emphasis (Material tonal / Cupertino tinted).
/// [busy] disables the button and overlays a spinner on the label without
/// changing the button's laid-out size.
class AdaptiveFilledButton extends StatelessWidget {
  const AdaptiveFilledButton({
    required this.onPressed,
    required this.child,
    this.icon,
    this.tonal = false,
    this.busy = false,
    super.key,
  });

  final VoidCallback? onPressed;
  final Widget child;
  final Widget? icon;
  final bool tonal;
  final bool busy;

  @override
  Widget build(BuildContext context) {
    final pressed = busy ? null : onPressed;
    final content = busy ? _busyOverlay(child) : child;
    if (_isCupertino) {
      final label = _withIcon(icon, content);
      return tonal
          ? CupertinoButton.tinted(onPressed: pressed, child: label)
          : CupertinoButton.filled(onPressed: pressed, child: label);
    }
    if (icon != null) {
      return tonal
          ? FilledButton.tonalIcon(
              onPressed: pressed,
              icon: icon,
              label: content,
            )
          : FilledButton.icon(onPressed: pressed, icon: icon, label: content);
    }
    return tonal
        ? FilledButton.tonal(onPressed: pressed, child: content)
        : FilledButton(onPressed: pressed, child: content);
  }
}

/// Secondary action: plain [CupertinoButton] on iOS, [OutlinedButton]
/// elsewhere. [fullWidth] keeps the stretched 48dp Material minimum where a
/// screen lays session-level actions out edge to edge. [busy] mirrors
/// [AdaptiveFilledButton.busy]: disabled, spinner over the label, stable
/// geometry.
class AdaptiveOutlinedButton extends StatelessWidget {
  const AdaptiveOutlinedButton({
    required this.onPressed,
    required this.child,
    this.icon,
    this.fullWidth = false,
    this.busy = false,
    super.key,
  });

  final VoidCallback? onPressed;
  final Widget child;
  final Widget? icon;
  final bool fullWidth;
  final bool busy;

  @override
  Widget build(BuildContext context) {
    final pressed = busy ? null : onPressed;
    final content = busy ? _busyOverlay(child) : child;
    if (_isCupertino) {
      return CupertinoButton(
        onPressed: pressed,
        child: _withIcon(icon, content),
      );
    }
    final style = fullWidth
        ? OutlinedButton.styleFrom(minimumSize: const Size.fromHeight(48))
        : null;
    return icon != null
        ? OutlinedButton.icon(
            onPressed: pressed,
            style: style,
            icon: icon,
            label: content,
          )
        : OutlinedButton(onPressed: pressed, style: style, child: content);
  }
}

/// Tertiary / inline action: plain [CupertinoButton] on iOS, [TextButton]
/// elsewhere.
class AdaptiveTextButton extends StatelessWidget {
  const AdaptiveTextButton({
    required this.onPressed,
    required this.child,
    this.fullWidth = false,
    super.key,
  });

  final VoidCallback? onPressed;
  final Widget child;
  final bool fullWidth;

  @override
  Widget build(BuildContext context) {
    if (_isCupertino) {
      return CupertinoButton(onPressed: onPressed, child: child);
    }
    return TextButton(
      onPressed: onPressed,
      style: fullWidth
          ? TextButton.styleFrom(minimumSize: const Size.fromHeight(48))
          : null,
      child: child,
    );
  }
}
