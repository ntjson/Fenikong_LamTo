import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/failure.dart';
import '../../core/uuid.dart';
import 'report_draft.dart';
import 'reports_repository.dart';

enum PhotoUploadStatus { pending, uploaded, failed }

class PhotoUpload {
  PhotoUpload({
    required this.path,
    required this.filename,
    this.status = PhotoUploadStatus.pending,
    String? clientAttachmentId,
  }) : clientAttachmentId = clientAttachmentId ?? uuidV4();

  final String path;
  final String filename;

  /// Stable in-session identity for this attachment (amendment 10).
  final String clientAttachmentId;

  PhotoUploadStatus status;
}

class SubmitOutcome {
  SubmitOutcome({required this.reportId, required this.photos});

  final int reportId;
  final List<PhotoUpload> photos;

  bool get allPhotosUploaded =>
      photos.every((p) => p.status == PhotoUploadStatus.uploaded);
}

/// Same client_ref was already submitted with different content (spec 3.5).
class ReportConflictException implements Exception {}

/// Spec 3.5 / 6.3 choreography: text commits first under the draft's stable
/// client_ref; the draft clears the moment the report row exists; photos then
/// upload one-by-one so a dropped upload never loses the report.
class ReportSubmitter {
  ReportSubmitter({required this.repository, required this.draftStore});

  final ReportsRepository repository;
  final ReportDraftStore draftStore;

  Future<SubmitOutcome> submit({
    required ReportDraft draft,
    required int occupancyId,
  }) async {
    final int reportId;
    try {
      final summary = await repository.createReport(
        clientRef: draft.clientRef,
        text: draft.text,
        locationId: draft.locationId!,
        isPrivate: draft.isPrivate,
      );
      reportId = summary.id;
    } on DioException catch (e) {
      if (Failure.fromDio(e).code == 'client_ref_conflict') {
        throw ReportConflictException();
      }
      rethrow; // network/validation: draft stays; retry reuses the same ref
    }
    // The report row exists: the text can never be lost now.
    await draftStore.clear(occupancyId);

    final photos = [
      for (final path in draft.photoPaths)
        PhotoUpload(path: path, filename: path.split('/').last),
    ];
    for (final photo in photos) {
      await _upload(reportId, photo);
    }
    return SubmitOutcome(reportId: reportId, photos: photos);
  }

  Future<PhotoUpload> retryPhoto({
    required int reportId,
    required PhotoUpload photo,
  }) async {
    // Amendment 10: already-uploaded attachments must not re-hit the API.
    if (photo.status == PhotoUploadStatus.uploaded) {
      return photo;
    }
    await _upload(reportId, photo);
    return photo;
  }

  Future<void> _upload(int reportId, PhotoUpload photo) async {
    try {
      await repository.uploadPhoto(
        reportId: reportId,
        path: photo.path,
        filename: photo.filename,
      );
      photo.status = PhotoUploadStatus.uploaded;
    } catch (_) {
      // Soft-fail any photo error (Dio or local) so committed-result always
      // lands after text create; draft is already cleared (amendment 11).
      photo.status = PhotoUploadStatus.failed;
    }
  }
}

final reportSubmitterProvider = Provider<ReportSubmitter>(
  (ref) => ReportSubmitter(
    repository: ref.watch(reportsRepositoryProvider),
    draftStore: ref.watch(reportDraftStoreProvider),
  ),
);
