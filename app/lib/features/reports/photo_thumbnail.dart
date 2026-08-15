import 'dart:io';

import 'package:flutter/material.dart';

import '../../core/adaptive_buttons.dart';
import '../../l10n/app_localizations.dart';
import '../../theme.dart';

/// 64px preview of a local (app-owned) photo, replacing the minted-UUID
/// chips: residents confirm the picture itself, never a filename.
///
/// [onDelete] shows a remove affordance (pre-submit / pre-send lists).
/// [onRetry] marks the photo as failed-to-upload: error border + badge icon
/// + a labeled retry action, so the state never rides on color alone.
class PhotoThumbnail extends StatelessWidget {
  const PhotoThumbnail({
    required this.path,
    required this.index,
    required this.count,
    this.onDelete,
    this.onRetry,
    super.key,
  });

  static const double size = 64;

  final String path;

  /// 1-based position among [count] photos ("Ảnh {n}/{m}").
  final int index;
  final int count;
  final VoidCallback? onDelete;
  final VoidCallback? onRetry;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final failed = onRetry != null;
    final errorColors = statusToneColors(context, StatusTone.error);
    final label = failed
        ? '${l10n.photoNofM(index, count)} — ${l10n.photoUploadFailed}'
        : l10n.photoNofM(index, count);
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Stack(
          children: [
            Semantics(
              label: label,
              image: true,
              child: Container(
                width: size,
                height: size,
                clipBehavior: Clip.antiAlias,
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(10),
                  border: failed
                      ? Border.all(color: errorColors.fg, width: 2)
                      : null,
                ),
                child: Image.file(
                  File(path),
                  fit: BoxFit.cover,
                  // Local files decoded at display density, never full-res.
                  cacheWidth: (size * MediaQuery.devicePixelRatioOf(context))
                      .round(),
                  errorBuilder: (_, _, _) =>
                      const Icon(Icons.broken_image_outlined),
                ),
              ),
            ),
            if (failed)
              Positioned(
                top: 2,
                right: 2,
                child: ExcludeSemantics(
                  child: Container(
                    padding: const EdgeInsets.all(2),
                    decoration: BoxDecoration(
                      color: errorColors.bg,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      Icons.error_outline,
                      size: 16,
                      color: errorColors.fg,
                    ),
                  ),
                ),
              ),
            if (onDelete != null)
              Positioned(
                top: 2,
                right: 2,
                child: IconButton.filledTonal(
                  onPressed: onDelete,
                  tooltip: MaterialLocalizations.of(
                    context,
                  ).deleteButtonTooltip,
                  iconSize: 16,
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints.tightFor(
                    width: 28,
                    height: 28,
                  ),
                  icon: const Icon(Icons.close),
                ),
              ),
          ],
        ),
        if (failed)
          AdaptiveTextButton(
            onPressed: onRetry,
            child: Text(l10n.reportPhotoRetry),
          ),
      ],
    );
  }
}
