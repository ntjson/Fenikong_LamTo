import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:lamto_api/lamto_api.dart';

import '../../core/authenticated_image.dart';
import '../../core/adaptive_buttons.dart';
import '../../core/adaptive_page_route.dart';
import '../../core/adaptive_scaffold.dart';
import '../../core/error_retry.dart';
import '../../core/failure.dart';
import '../../core/page_body.dart';
import '../../l10n/app_localizations.dart';
import '../../theme.dart';
import '../ledger/ledger_detail_screen.dart';
import 'category_labels.dart';
import 'photo_thumbnail.dart';
import 'report_draft.dart';
import 'report_photo_files.dart';
import 'report_submitter.dart';
import 'reports_repository.dart';
import 'report_form_screen.dart';

String _date(DateTime value) =>
    DateFormat('dd/MM/yyyy').format(value.toLocal());

class IssueDetailScreen extends ConsumerStatefulWidget {
  const IssueDetailScreen({required this.reportId, super.key});
  final int reportId;

  @override
  ConsumerState<IssueDetailScreen> createState() => _IssueDetailScreenState();
}

class _IssueDetailScreenState extends ConsumerState<IssueDetailScreen> {
  /// Shows the inline thanks notice after a rating — SnackBars never render
  /// under the iOS Cupertino shell.
  bool _rated = false;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final detail = ref.watch(reportDetailProvider(widget.reportId));
    return AdaptiveScaffold(
      title: l10n.issueDetailTitle(widget.reportId),
      body: PageBody(
        child: switch (detail) {
          AsyncData(:final value) => _body(context, ref, l10n, value),
          AsyncError(:final error) => Center(
            child: ErrorRetry(
              error: error,
              onRetry: () =>
                  ref.invalidate(reportDetailProvider(widget.reportId)),
            ),
          ),
          _ => const Center(child: CircularProgressIndicator.adaptive()),
        },
      ),
    );
  }

  Widget _body(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    ReportDetail report,
  ) {
    // Tone only where states differ (pending vs done); default ink elsewhere
    // so color keeps carrying meaning (DESIGN.md Separate States Rule).
    String caseLine(ReportCase caseItem) {
      final category = categoryLabel(caseItem.category, l10n);
      return category == null
          ? l10n.timelineCaseNoCategory
          : l10n.timelineCase(category);
    }

    final steps = <(IconData, String, StatusTone?)>[
      (
        Icons.send_outlined,
        '${l10n.timelineSubmitted} · ${_date(report.createdAt)}',
        null,
      ),
      if (report.triageStatus == 'SUCCEEDED' ||
          report.triageStatus == 'NEEDS_MANUAL' ||
          report.cases.isNotEmpty)
        (Icons.fact_check_outlined, l10n.timelineTriageDone, null)
      else
        (Icons.hourglass_empty, l10n.timelineTriagePending, StatusTone.warning),
      for (final caseItem in report.cases) ...[
        (
          Icons.folder_open_outlined,
          '${caseLine(caseItem)}\n'
              '${caseItem.completedAt != null ? l10n.timelineCompleted : l10n.timelineWork(caseItem.updates.isNotEmpty ? l10n.workStatusInProgress : l10n.workStatusAssigned, _date(caseItem.deadlineAt))}',
          null,
        ),
      ],
    ];
    final rateable = report.cases.where((caseItem) => caseItem.canRate);
    final infoRequestMessage = report.openInfoRequest?['message']?.value;
    // Reply photos whose upload has not landed yet (fail-safe doctrine):
    // restored from the persisted record so retry survives process death.
    final pendingReplyPhotos =
        ref.watch(infoReplyPendingPhotosProvider(report.id)).value ??
        const <String>[];

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(report.text, style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 4),
        Text(
          '${report.locationPathSnapshot} · ${report.unitLabel}',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        if (report.status == StatusEnum.NEEDS_INFO &&
            infoRequestMessage is String) ...[
          const SizedBox(height: 16),
          _InfoRequestBanner(
            message: infoRequestMessage,
            onReply: () => _showReplySheet(context, ref, report.id),
          ),
        ],
        if (report.photos.isNotEmpty) ...[
          const SizedBox(height: 12),
          SizedBox(
            height: 96,
            child: ListView(
              scrollDirection: Axis.horizontal,
              children: [
                for (final (index, photo) in report.photos.indexed)
                  Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(10),
                      child: AuthenticatedImage(
                        photo.downloadUrl,
                        width: 96,
                        height: 96,
                        semanticLabel: l10n.photoNofM(
                          index + 1,
                          report.photos.length,
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ],
        if (pendingReplyPhotos.isNotEmpty) ...[
          const SizedBox(height: 12),
          Builder(
            builder: (context) {
              final colors = statusToneColors(context, StatusTone.warning);
              return Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: colors.bg,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Row(
                  children: [
                    Icon(Icons.info_outline, color: colors.fg),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        l10n.infoReplyPendingPhotosTitle,
                        style: Theme.of(
                          context,
                        ).textTheme.bodyMedium?.copyWith(color: colors.fg),
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              for (final (index, path) in pendingReplyPhotos.indexed)
                PhotoThumbnail(
                  path: path,
                  index: index + 1,
                  count: pendingReplyPhotos.length,
                  onRetry: () => _retryPendingReplyPhoto(ref, report.id, path),
                ),
            ],
          ),
        ],
        if (report.declinedReason != null) ...[
          const SizedBox(height: 16),
          Card(
            child: ListTile(
              title: Text(l10n.declinedTitle),
              subtitle: Text(report.declinedReason!),
            ),
          ),
          const SizedBox(height: 12),
          AdaptiveFilledButton(
            onPressed: () => openReportForm(context),
            icon: const Icon(Icons.edit_note_outlined),
            child: Text(l10n.declinedCorrectedReportCta),
          ),
        ],
        const SizedBox(height: 16),
        for (final (icon, label, tone) in steps)
          ListTile(
            minTileHeight: 48,
            contentPadding: EdgeInsets.zero,
            leading: Icon(
              icon,
              color: tone == null ? null : statusToneColors(context, tone).fg,
            ),
            title: Text(label),
          ),
        const SizedBox(height: 16),
        Text(
          l10n.progressTitle,
          style: Theme.of(context).textTheme.titleMedium,
        ),
        if (report.cases.every((caseItem) => caseItem.updates.isEmpty))
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text(
              l10n.progressEmpty,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
        for (final caseItem in report.cases) ...[
          for (final update in caseItem.updates)
            _ProgressTile(
              createdAt: update.createdAt,
              cause: update.cause,
              result: update.result,
            ),
          if (caseItem.completedAt != null)
            _CompletedMarker(at: caseItem.completedAt!),
        ],
        // Inline where the rate CTA sat (the refreshed detail drops the CTA).
        if (_rated)
          Padding(
            padding: const EdgeInsets.only(top: 16),
            child: StatusNotice(
              tone: StatusTone.success,
              message: l10n.rateThanks,
            ),
          ),
        for (final caseItem in rateable)
          if (report.status != StatusEnum.DECLINED)
            Padding(
              padding: const EdgeInsets.only(top: 16),
              child: AdaptiveFilledButton(
                icon: const Icon(Icons.star_outline),
                child: Text(l10n.rateWorkCta),
                onPressed: () => _openRateSheet(context, caseItem.id),
              ),
            ),
        for (final entryId in report.ledgerEntryIds)
          Padding(
            padding: const EdgeInsets.only(top: 16),
            child: AdaptiveOutlinedButton(
              icon: const Icon(Icons.account_balance_outlined),
              child: Text(l10n.ledgerDetailTitle),
              onPressed: () => Navigator.push(
                context,
                adaptivePageRoute(
                  builder: (_) => LedgerDetailScreen(entryId: entryId),
                ),
              ),
            ),
          ),
      ],
    );
  }

  Future<void> _openRateSheet(BuildContext context, int caseId) async {
    final rated = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      builder: (_) => _RateCaseSheet(caseId: caseId),
    );
    if (rated == true && mounted) {
      ref.invalidate(reportDetailProvider(widget.reportId));
      setState(() => _rated = true);
    }
  }

  Future<void> _showReplySheet(
    BuildContext context,
    WidgetRef ref,
    int reportId,
  ) async {
    await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      builder: (_) => _InfoReplySheet(reportId: reportId),
    );
    // The reply (and pending-photo record) may have committed even when the
    // sheet was barrier-dismissed, so refresh unconditionally.
    if (context.mounted) {
      ref.invalidate(reportDetailProvider(reportId));
      ref.invalidate(infoReplyPendingPhotosProvider(reportId));
    }
  }

  Future<void> _retryPendingReplyPhoto(
    WidgetRef ref,
    int reportId,
    String path,
  ) async {
    final uploaded = await _uploadPendingReplyPhoto(
      repository: ref.read(reportsRepositoryProvider),
      files: ref.read(reportPhotoFileStoreProvider),
      records: ref.read(infoReplyPhotoStoreProvider),
      reportId: reportId,
      path: path,
    );
    ref.invalidate(infoReplyPendingPhotosProvider(reportId));
    if (uploaded) ref.invalidate(reportDetailProvider(reportId));
  }
}

/// One step of the info-reply photo choreography: upload a pending photo; on
/// success delete the app-owned copy and shrink the persisted record. Returns
/// whether the server now has the photo. Retrying is always safe — the server
/// is idempotent by content SHA-256.
Future<bool> _uploadPendingReplyPhoto({
  required ReportsRepository repository,
  required ReportPhotoFileStore files,
  required InfoReplyPhotoStore records,
  required int reportId,
  required String path,
}) async {
  try {
    await repository.uploadPhoto(
      reportId: reportId,
      path: path,
      filename: path.split('/').last,
    );
  } catch (_) {
    return false; // soft-fail: the reply text is committed; retry stays offered
  }
  await files.deletePaths([path]);
  final remaining = List<String>.from(await records.read(reportId))
    ..remove(path);
  await records.write(reportId, remaining);
  return true;
}

class _ProgressTile extends StatelessWidget {
  const _ProgressTile({
    required this.createdAt,
    required this.cause,
    required this.result,
  });

  final DateTime createdAt;
  final String cause;
  final String result;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 8),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.only(top: 2),
          child: Icon(Icons.build_outlined),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(cause, style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 4),
              Text(result),
              Text(_date(createdAt)),
            ],
          ),
        ),
      ],
    ),
  );
}

class _CompletedMarker extends StatelessWidget {
  const _CompletedMarker({required this.at});

  final DateTime at;

  @override
  Widget build(BuildContext context) {
    final colors = statusToneColors(context, StatusTone.success);
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: Icon(Icons.check_circle_outline, color: colors.fg),
      title: Text(
        '${AppLocalizations.of(context)!.progressCompleted} · ${_date(at)}',
      ),
    );
  }
}

class _InfoRequestBanner extends StatelessWidget {
  const _InfoRequestBanner({required this.message, required this.onReply});

  final String message;
  final VoidCallback onReply;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final colors = statusToneColors(context, StatusTone.warning);
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: colors.bg,
        border: Border.all(color: colors.fg),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.info_outline, color: colors.fg),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  l10n.infoRequestTitle,
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                const SizedBox(height: 4),
                Text(message),
                const SizedBox(height: 8),
                AdaptiveFilledButton(
                  onPressed: onReply,
                  child: Text(l10n.infoReplySubmit),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _InfoReplySheet extends ConsumerStatefulWidget {
  const _InfoReplySheet({required this.reportId});

  final int reportId;

  @override
  ConsumerState<_InfoReplySheet> createState() => _InfoReplySheetState();
}

/// Fail-safe reply choreography (mirrors [ReportSubmitter]): the text commits
/// first in its own request; only then do photos upload one by one, each with
/// its own retry, so a dead connection can never lose the words.
class _InfoReplySheetState extends ConsumerState<_InfoReplySheet> {
  final _text = TextEditingController();
  final _photos = <PhotoUpload>[];
  bool _busy = false;
  bool _committed = false;
  String? _error;

  // Cached in initState — [ref] is unsafe after unmount, and the upload loop
  // keeps running (and must keep the record accurate) if the sheet closes.
  late ReportsRepository _repo;
  late ReportPhotoFileStore _fileStore;
  late InfoReplyPhotoStore _replyStore;

  @override
  void initState() {
    super.initState();
    _repo = ref.read(reportsRepositoryProvider);
    _fileStore = ref.read(reportPhotoFileStoreProvider);
    _replyStore = ref.read(infoReplyPhotoStoreProvider);
  }

  @override
  void dispose() {
    // Cancelled before commit: nothing was sent, drop the imported copies.
    // After commit the not-yet-uploaded paths belong to the persisted record.
    if (!_committed && _photos.isNotEmpty) {
      unawaited(
        _fileStore
            .deletePaths([for (final p in _photos) p.path])
            .catchError((Object _) {}),
      );
    }
    _text.dispose();
    super.dispose();
  }

  Future<void> _addPhoto(AppLocalizations l10n) async {
    if (_busy || _committed) return;
    final remaining = maxReportPhotos - _photos.length;
    if (remaining <= 0) return;
    final picked = await pickReportPhotos(
      context,
      l10n,
      ref.read(imagePickerProvider),
      limit: remaining,
    );
    if (picked.isEmpty) return;
    // Durable app-owned copies before anything else (picker cache paths do
    // not survive process death) — same rule as the report draft.
    final owned = <PhotoUpload>[];
    for (final xfile in picked) {
      final path = await _fileStore.importReplyPickerPath(
        reportId: widget.reportId,
        sourcePath: xfile.path,
      );
      owned.add(PhotoUpload(path: path, filename: path.split('/').last));
    }
    if (!mounted) {
      // Dispose already ran without these paths; do not leak the copies.
      unawaited(_fileStore.deletePaths([for (final p in owned) p.path]));
      return;
    }
    setState(() => _photos.addAll(owned));
  }

  Future<void> _removePhoto(PhotoUpload photo) async {
    if (_busy || _committed) return;
    setState(() => _photos.remove(photo));
    await _fileStore.deletePaths([photo.path]);
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final failed = [
      for (final p in _photos)
        if (p.status == PhotoUploadStatus.failed) p,
    ];
    final uploaded = _photos
        .where((p) => p.status == PhotoUploadStatus.uploaded)
        .length;
    final editingLocked = _busy || _committed;
    return Padding(
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: 16,
        bottom: 16 + MediaQuery.viewInsetsOf(context).bottom,
      ),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              l10n.infoRequestTitle,
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _text,
              minLines: 3,
              maxLines: 5,
              enabled: !editingLocked,
              onChanged: (_) => setState(() {}),
              decoration: InputDecoration(hintText: l10n.infoReplyHint),
            ),
            const SizedBox(height: 8),
            Text(l10n.infoReplyPhotosHint),
            const SizedBox(height: 8),
            // Photos below the text field so infoReplyPhotosHint stays
            // geometrically true.
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final (index, photo) in _photos.indexed)
                  PhotoThumbnail(
                    path: photo.path,
                    index: index + 1,
                    count: _photos.length,
                    onDelete: editingLocked ? null : () => _removePhoto(photo),
                  ),
                if (!_committed && _photos.length < maxReportPhotos)
                  ActionChip(
                    avatar: const Icon(Icons.add_a_photo_outlined, size: 20),
                    label: Text(l10n.reportAddPhoto),
                    // ≥48dp touch target (spec §6.2/§6.4).
                    materialTapTargetSize: MaterialTapTargetSize.padded,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 12,
                    ),
                    onPressed: _busy ? null : () => _addPhoto(l10n),
                  ),
              ],
            ),
            if (_error != null) ...[
              const SizedBox(height: 8),
              Semantics(
                liveRegion: true,
                child: Text(
                  _error!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ),
              const SizedBox(height: 4),
              Text(
                l10n.infoReplyNotSent,
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
            if (_committed && !_busy) ...[
              const SizedBox(height: 8),
              Builder(
                builder: (context) {
                  final ok = failed.isEmpty;
                  final colors = statusToneColors(
                    context,
                    ok ? StatusTone.success : StatusTone.warning,
                  );
                  return Semantics(
                    liveRegion: true,
                    child: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: colors.bg,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            ok
                                ? Icons.check_circle_outline
                                : Icons.info_outline,
                            color: colors.fg,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              ok
                                  ? l10n.infoReplySavedPhotos(
                                      uploaded,
                                      _photos.length,
                                    )
                                  : l10n.infoReplyPhotosPending,
                              style: Theme.of(context).textTheme.bodyMedium
                                  ?.copyWith(color: colors.fg),
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ],
            if (failed.isNotEmpty) ...[
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  for (final photo in failed)
                    PhotoThumbnail(
                      path: photo.path,
                      index: _photos.indexOf(photo) + 1,
                      count: _photos.length,
                      // _retryPhoto no-ops while busy, so the failed state
                      // (and its treatment) never flickers off.
                      onRetry: () => _retryPhoto(photo),
                    ),
                ],
              ),
            ],
            const SizedBox(height: 8),
            AdaptiveFilledButton(
              busy: _busy,
              onPressed: _busy
                  ? null
                  : _committed
                  ? () => Navigator.pop(context, true)
                  : _text.text.trim().isEmpty
                  ? null
                  : _submit,
              child: Text(
                _committed ? l10n.infoReplyClose : l10n.infoReplySubmit,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _submit() async {
    final l10n = AppLocalizations.of(context)!;
    setState(() {
      _busy = true;
      _error = null;
    });
    // Step 1: the words. Their own request — a failed photo can't touch them.
    try {
      await _repo.replyInfo(reportId: widget.reportId, text: _text.text.trim());
    } catch (e) {
      if (mounted) {
        setState(() {
          _busy = false;
          _error = failureMessage(Failure.fromObject(e), l10n);
        });
      }
      return;
    }
    // The reply row exists: the text can never be lost now.
    _committed = true;
    if (_photos.isEmpty) {
      if (mounted) Navigator.pop(context, true);
      return;
    }
    // Step 2: persist the pending record first (process death mid-upload
    // restores per-photo retry on the issue detail screen), then upload
    // photos one by one.
    await _replyStore.write(widget.reportId, [for (final p in _photos) p.path]);
    if (mounted) setState(() {});
    for (final photo in _photos) {
      final ok = await _uploadPendingReplyPhoto(
        repository: _repo,
        files: _fileStore,
        records: _replyStore,
        reportId: widget.reportId,
        path: photo.path,
      );
      photo.status = ok ? PhotoUploadStatus.uploaded : PhotoUploadStatus.failed;
      if (mounted) setState(() {});
    }
    if (mounted) setState(() => _busy = false);
  }

  Future<void> _retryPhoto(PhotoUpload photo) async {
    if (_busy || photo.status == PhotoUploadStatus.uploaded) return;
    setState(() => _busy = true);
    final ok = await _uploadPendingReplyPhoto(
      repository: _repo,
      files: _fileStore,
      records: _replyStore,
      reportId: widget.reportId,
      path: photo.path,
    );
    photo.status = ok ? PhotoUploadStatus.uploaded : PhotoUploadStatus.failed;
    if (mounted) setState(() => _busy = false);
  }
}

class _RateCaseSheet extends ConsumerStatefulWidget {
  const _RateCaseSheet({required this.caseId});
  final int caseId;

  @override
  ConsumerState<_RateCaseSheet> createState() => _RateCaseSheetState();
}

class _RateCaseSheetState extends ConsumerState<_RateCaseSheet> {
  bool _satisfied = true;
  final _comment = TextEditingController();
  bool _busy = false;
  String? _error;

  @override
  void dispose() {
    _comment.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Padding(
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: 16,
        bottom: 16 + MediaQuery.viewInsetsOf(context).bottom,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            l10n.rateWorkTitle,
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          SegmentedButton<bool>(
            segments: [
              ButtonSegment(value: true, label: Text(l10n.rateSatisfied)),
              ButtonSegment(value: false, label: Text(l10n.rateNotSatisfied)),
            ],
            selected: {_satisfied},
            onSelectionChanged: _busy
                ? null
                : (selection) => setState(() => _satisfied = selection.first),
          ),
          TextField(
            controller: _comment,
            maxLength: 500,
            decoration: InputDecoration(labelText: l10n.rateCommentLabel),
          ),
          if (_error != null) ...[
            const SizedBox(height: 8),
            Text(
              _error!,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
          ],
          const SizedBox(height: 8),
          AdaptiveFilledButton(
            onPressed: _busy ? null : _submit,
            child: Text(l10n.rateSubmit),
          ),
        ],
      ),
    );
  }

  Future<void> _submit() async {
    final l10n = AppLocalizations.of(context)!;
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await ref
          .read(reportsRepositoryProvider)
          .rateCase(
            caseId: widget.caseId,
            satisfied: _satisfied,
            comment: _comment.text.trim(),
          );
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) {
        setState(() => _error = failureMessage(Failure.fromObject(e), l10n));
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }
}
