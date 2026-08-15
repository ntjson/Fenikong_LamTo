import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lamto_api/lamto_api.dart';

import '../../core/providers.dart';
import '../../core/failure.dart';
import 'report_draft.dart';
import 'report_photo_files.dart';

/// Paths used by the reporting APIs — must exist in OpenAPI (contract tests).
abstract final class ReportsApiPaths {
  static const reports = '/api/v1/reports';
  static const reportDetail = '/api/v1/reports/{id}';
  static const reportPhotos = '/api/v1/reports/{id}/photos';
  static const locations = '/api/v1/locations';
  static const caseRating = '/api/v1/cases/{id}/rating';
}

abstract class ReportsRepository {
  Future<ReportSummary> createReport({
    required String clientRef,
    required String text,
    required int locationId,
    bool isPrivate = false,
  });
  Future<PaginatedReportSummaryList> listReports({String? cursor});
  Future<ReportDetail> fetchReport(int id);
  Future<ReportPhoto> uploadPhoto({
    required int reportId,
    required String path,
    required String filename,
  });
  Future<CaseRatingResult> rateCase({
    required int caseId,
    required bool satisfied,
    String comment = '',
  });
  Future<void> replyInfo({required int reportId, required String text});
  Future<List<Location>> fetchLocations();
}

/// Thin wrapper over the generated dart-dio APIs on the shared Dio
/// (token + X-LamTo-Occupancy interceptors already installed).
class DioReportsRepository implements ReportsRepository {
  DioReportsRepository(Dio dio)
    : _reports = ReportsApi(dio, standardSerializers),
      _locations = LocationsApi(dio, standardSerializers),
      _cases = CasesApi(dio, standardSerializers);

  final ReportsApi _reports;
  final LocationsApi _locations;
  final CasesApi _cases;

  @override
  Future<ReportSummary> createReport({
    required String clientRef,
    required String text,
    required int locationId,
    bool isPrivate = false,
  }) async {
    final res = await _reports.reportsCreate(
      reportCreateRequest: ReportCreateRequest(
        (b) => b
          ..clientRef = clientRef
          ..text = text
          ..isPrivate = isPrivate
          ..locationId = locationId,
      ),
    );
    return res.data!;
  }

  @override
  Future<PaginatedReportSummaryList> listReports({String? cursor}) async {
    final res = await _reports.reportsList(cursor: cursor);
    return res.data!;
  }

  @override
  Future<ReportDetail> fetchReport(int id) async {
    final res = await _reports.reportsRetrieve(id: id);
    return res.data!;
  }

  @override
  Future<ReportPhoto> uploadPhoto({
    required int reportId,
    required String path,
    required String filename,
  }) async {
    final lower = filename.toLowerCase();
    final subtype = lower.endsWith('.png') ? 'png' : 'jpeg';
    final res = await _reports.reportsPhotosCreate(
      id: reportId,
      photo: await MultipartFile.fromFile(
        path,
        filename: filename,
        contentType: DioMediaType('image', subtype),
      ),
    );
    return res.data!;
  }

  @override
  Future<CaseRatingResult> rateCase({
    required int caseId,
    required bool satisfied,
    String comment = '',
  }) async {
    final res = await _cases.casesRatingCreate(
      id: caseId,
      caseRatingRequest: CaseRatingRequest(
        (b) => b
          ..satisfied = satisfied
          ..comment = comment,
      ),
    );
    return res.data!;
  }

  @override
  Future<void> replyInfo({required int reportId, required String text}) async {
    try {
      await _reports.reportsInfoReplyCreate(
        id: reportId,
        infoReplyRequest: InfoReplyRequest((b) => b..text = text),
      );
    } on DioException catch (e) {
      throw Failure.fromDio(e);
    }
  }

  @override
  Future<List<Location>> fetchLocations() async {
    final res = await _locations.locationsRetrieve();
    return res.data!.toList();
  }
}

/// Extract the `cursor` query param from a DRF cursor-pagination `next` URL.
String? cursorFromNext(String? next) {
  if (next == null || next.isEmpty) return null;
  return Uri.parse(next).queryParameters['cursor'];
}

final reportsRepositoryProvider = Provider<ReportsRepository>(
  (ref) => DioReportsRepository(ref.watch(dioProvider)),
);

final reportDraftStoreProvider = Provider<ReportDraftStore>(
  (ref) => ReportDraftStore(),
);

final reportPhotoFileStoreProvider = Provider<ReportPhotoFileStore>(
  (ref) => ReportPhotoFileStore(),
);

final infoReplyPhotoStoreProvider = Provider<InfoReplyPhotoStore>(
  (ref) => InfoReplyPhotoStore(),
);

/// Info-reply photos not yet uploaded for a report (fail-safe doctrine): the
/// issue detail screen renders per-photo retry from this after restart.
final infoReplyPendingPhotosProvider = FutureProvider.autoDispose
    .family<List<String>, int>(
      (ref, reportId) => ref.watch(infoReplyPhotoStoreProvider).read(reportId),
    );

/// Building-scoped caches rebuild on occupancy change (providers.dart contract).
final locationsProvider = FutureProvider.autoDispose<List<Location>>((ref) {
  ref.watch(occupancyScopedProviders);
  return ref.watch(reportsRepositoryProvider).fetchLocations();
});

final reportDetailProvider = FutureProvider.autoDispose
    .family<ReportDetail, int>((ref, id) {
      ref.watch(occupancyScopedProviders);
      return ref.watch(reportsRepositoryProvider).fetchReport(id);
    });
