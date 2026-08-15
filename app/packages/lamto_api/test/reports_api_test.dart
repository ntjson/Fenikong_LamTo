import 'package:test/test.dart';
import 'package:lamto_api/lamto_api.dart';


/// tests for ReportsApi
void main() {
  final instance = LamtoApi().getReportsApi();

  group(ReportsApi, () {
    //Future<ReportSummary> reportsCreate(ReportCreateRequest reportCreateRequest, { int xLamToOccupancy }) async
    test('test reportsCreate', () async {
      // TODO
    });

    // Step 1 of the resident's needs-info reply: commit the text. Text-only by design so a dropped connection can never lose the words; the client then attaches any photos one by one via POST /api/v1/reports/{id}/photos. A successful reply resolves the open information request and moves the report from NEEDS_INFO back to IN_REVIEW (photo uploads are not status-gated, so step 2 still works after the flip).
    //
    //Future<InfoReplyResult> reportsInfoReplyCreate(int id, InfoReplyRequest infoReplyRequest) async
    test('test reportsInfoReplyCreate', () async {
      // TODO
    });

    //Future<PaginatedReportSummaryList> reportsList({ String cursor }) async
    test('test reportsList', () async {
      // TODO
    });

    // Attach one photo to a report the caller submitted (active occupancy in the report's building required). There is no report-status gate, so this also serves as step 2 of the needs-info reply choreography, after POST /api/v1/reports/{id}/info-reply commits the text. Uploads are virus-scanned before storage and idempotent per report by content SHA-256: replaying the same file returns 200 with the existing photo instead of creating a duplicate (201), so per-photo retries are safe.
    //
    //Future<ReportPhoto> reportsPhotosCreate(int id, MultipartFile photo) async
    test('test reportsPhotosCreate', () async {
      // TODO
    });

    //Future<ReportDetail> reportsRetrieve(int id) async
    test('test reportsRetrieve', () async {
      // TODO
    });

  });
}
