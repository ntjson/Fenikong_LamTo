import 'dart:typed_data';

import 'package:flutter/cupertino.dart' show CupertinoIcons;
import 'package:flutter/material.dart';
import 'package:pdfrx/pdfrx.dart';
import 'package:share_plus/share_plus.dart';

import '../../core/adaptive_buttons.dart';
import '../../core/adaptive_page_route.dart';
import '../../core/adaptive_scaffold.dart';
import '../../l10n/app_localizations.dart';
import '../../theme.dart';
import 'document_kind.dart';

/// Opens a downloaded document on top of the current screen.
///
/// The resident reads the document here, inside the app; handing it to another
/// app is a deliberate action they take from the viewer, not the way documents
/// open.
Future<void> showDocumentViewer(
  BuildContext context, {
  required Uint8List bytes,
  required String filename,
  String? contentType,
}) => Navigator.of(context).push(
  adaptivePageRoute<void>(
    builder: (_) => DocumentViewerScreen(
      bytes: bytes,
      filename: filename,
      contentType: contentType,
    ),
  ),
);

/// Reads one downloaded document — PDF or image — without leaving the app.
///
/// The bytes are held in memory: they are evidence fetched for this reading,
/// not a file the app keeps.
class DocumentViewerScreen extends StatefulWidget {
  const DocumentViewerScreen({
    required this.bytes,
    required this.filename,
    this.contentType,
    this.controller,
    super.key,
  });

  final Uint8List bytes;
  final String filename;
  final String? contentType;

  /// Optional handle on the PDF view — page count, current page, navigation.
  /// Reading needs none; a caller that wants to observe or drive the view
  /// passes one.
  final PdfViewerController? controller;

  @override
  State<DocumentViewerScreen> createState() => _DocumentViewerScreenState();
}

class _DocumentViewerScreenState extends State<DocumentViewerScreen> {
  bool _sharing = false;
  bool _shareFailed = false;

  /// Hands the document to the OS — share targets, and the save-to-files and
  /// print entries the sheet carries — on the resident's request.
  ///
  /// The bytes go across as data with a name: share_plus stages them itself,
  /// in a temporary directory the system reclaims, so LamTo never writes a
  /// resident's evidence to disk on its own account.
  Future<void> _share() async {
    if (_sharing) return;
    setState(() {
      _sharing = true;
      _shareFailed = false;
    });
    try {
      final safeName = widget.filename.replaceAll(RegExp(r'[/\\]|\.\.'), '_');
      final box = context.findRenderObject() as RenderBox?;
      await SharePlus.instance.share(
        ShareParams(
          files: [
            XFile.fromData(
              widget.bytes,
              name: safeName.isEmpty ? 'document' : safeName,
              mimeType: widget.contentType,
            ),
          ],
          fileNameOverrides: [safeName.isEmpty ? 'document' : safeName],
          sharePositionOrigin: box != null && box.hasSize
              ? box.localToGlobal(Offset.zero) & box.size
              : null,
        ),
      );
    } catch (_) {
      // Reading is unaffected — the document is still on screen — but a
      // silent failure would leave the resident with nothing at all.
      if (mounted) setState(() => _shareFailed = true);
    } finally {
      if (mounted) setState(() => _sharing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return AdaptiveScaffold(
      title: widget.filename,
      actions: [
        AdaptiveIconButton(
          onPressed: _sharing ? null : _share,
          icon: Icons.share,
          cupertinoIcon: CupertinoIcons.share,
          label: l10n.documentShare,
        ),
      ],
      body: _shareFailed
          ? Column(
              children: [
                Expanded(child: _content(l10n)),
                // The document stays on screen: a failed hand-off is not a
                // failure to read, and the action can simply be taken again.
                StatusNotice(
                  tone: StatusTone.warning,
                  message: l10n.documentShareFailed,
                ),
              ],
            )
          : _content(l10n),
    );
  }

  Widget _content(AppLocalizations l10n) {
    switch (detectDocumentKind(widget.bytes, widget.contentType)) {
      case DocumentKind.pdf:
        return PdfViewer.data(
          widget.bytes,
          sourceName: widget.filename,
          controller: widget.controller,
          // pdfrx's own banner is a developer diagnostic; a resident who opens
          // an unreadable file gets the app's plain sentence instead.
          params: PdfViewerParams(
            errorBannerBuilder: (context, error, stackTrace, documentRef) =>
                _unreadable(l10n),
          ),
        );
      case DocumentKind.image:
        return InteractiveViewer(
          maxScale: 8,
          child: Center(
            child: Image.memory(
              widget.bytes,
              errorBuilder: (context, error, stackTrace) => _unreadable(l10n),
            ),
          ),
        );
      case DocumentKind.unsupported:
        return _unreadable(l10n);
    }
  }

  /// Shown for a file this app cannot render — an unsupported type, or a PDF
  /// the engine refuses. Sharing stays available, so the document is never a
  /// dead end.
  Widget _unreadable(AppLocalizations l10n) => Center(
    child: Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.description_outlined, size: 48),
          const SizedBox(height: 12),
          Text(l10n.documentNoPreview, textAlign: TextAlign.center),
        ],
      ),
    ),
  );
}
