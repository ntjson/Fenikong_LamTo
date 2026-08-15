import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/features/reports/report_draft.dart';
import 'package:lamto/features/reports/report_submitter.dart';
import 'package:lamto/features/reports/reports_repository.dart';
import 'package:lamto_api/lamto_api.dart';
import 'package:shared_preferences/shared_preferences.dart';

ReportSummary _summary(int id) => ReportSummary(
  (b) => b
    ..id = id
    ..text = 'Leak'
    ..status = StatusEnum.SUBMITTED
    ..isPrivate = false
    ..locationPathSnapshot = 'B / Hall'
    ..createdAt = DateTime.utc(2026, 7, 17),
);

DioException _problem(int status, String code) {
  final req = RequestOptions(path: '/api/v1/reports');
  return DioException(
    requestOptions: req,
    response: Response(
      requestOptions: req,
      statusCode: status,
      data: {
        'code': code,
        'status': status,
        'title': 'x',
        'type': 'about:blank',
      },
    ),
    type: DioExceptionType.badResponse,
  );
}

class _FakeRepo implements ReportsRepository {
  final createdRefs = <String>[];
  final privateValues = <bool>[];
  final uploaded = <String>[];
  Object? createError;
  Set<String> failPhotoPaths = {};

  /// Paths that throw a non-Dio error (e.g. missing local file).
  Set<String> throwLocalPaths = {};

  @override
  Future<ReportSummary> createReport({
    required String clientRef,
    required String text,
    required int locationId,
    bool isPrivate = false,
  }) async {
    createdRefs.add(clientRef);
    privateValues.add(isPrivate);
    final error = createError;
    if (error != null) throw error;
    return _summary(42);
  }

  @override
  Future<ReportPhoto> uploadPhoto({
    required int reportId,
    required String path,
    required String filename,
  }) async {
    if (throwLocalPaths.contains(path)) {
      throw StateError('missing local file');
    }
    if (failPhotoPaths.contains(path)) {
      throw _problem(500, 'server_error');
    }
    uploaded.add(path);
    return ReportPhoto(
      (b) => b
        ..id = uploaded.length
        ..filename = filename
        ..sha256 = 'aa'
        ..downloadUrl = '/api/v1/documents/tok',
    );
  }

  @override
  Future<PaginatedReportSummaryList> listReports({String? cursor}) =>
      throw UnimplementedError();
  @override
  Future<ReportDetail> fetchReport(int id) => throw UnimplementedError();
  @override
  Future<CaseRatingResult> rateCase({
    required int caseId,
    required bool satisfied,
    String comment = '',
  }) => throw UnimplementedError();
  @override
  Future<void> replyInfo({required int reportId, required String text}) =>
      throw UnimplementedError();
  @override
  Future<List<Location>> fetchLocations() => throw UnimplementedError();
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late _FakeRepo repo;
  late ReportDraftStore drafts;
  late ReportSubmitter submitter;

  setUp(() {
    SharedPreferences.setMockInitialValues({});
    repo = _FakeRepo();
    drafts = ReportDraftStore();
    submitter = ReportSubmitter(repository: repo, draftStore: drafts);
  });

  ReportDraft draftOf({List<String> photos = const []}) => ReportDraft.fresh()
      .copyWith(text: 'Leak', locationId: 3, photoPaths: photos);

  test('submit commits text, clears draft, uploads photos in order', () async {
    final draft = draftOf(photos: ['/tmp/a.jpg', '/tmp/b.jpg']);
    await drafts.write(7, draft);
    final outcome = await submitter.submit(draft: draft, occupancyId: 7);
    expect(outcome.reportId, 42);
    expect(outcome.allPhotosUploaded, isTrue);
    expect(repo.uploaded, ['/tmp/a.jpg', '/tmp/b.jpg']);
    expect(await drafts.read(7), isNull); // text committed -> draft gone
  });

  test('submit forwards draft privacy', () async {
    final draft = draftOf().copyWith(isPrivate: true);
    await submitter.submit(draft: draft, occupancyId: 7);
    expect(repo.privateValues.single, isTrue);
  });

  test(
    'retry after network failure reuses the SAME client_ref (spec 3.5)',
    () async {
      final draft = draftOf();
      repo.createError = DioException(
        requestOptions: RequestOptions(path: '/api/v1/reports'),
        type: DioExceptionType.connectionTimeout,
      );
      await expectLater(
        submitter.submit(draft: draft, occupancyId: 7),
        throwsA(anything),
      );
      repo.createError = null;
      await submitter.submit(
        draft: draft,
        occupancyId: 7,
      ); // server replays 200
      expect(repo.createdRefs, hasLength(2));
      expect(repo.createdRefs[0], repo.createdRefs[1]);
    },
  );

  test('409 client_ref_conflict surfaces ReportConflictException', () async {
    repo.createError = _problem(409, 'client_ref_conflict');
    await expectLater(
      submitter.submit(draft: draftOf(), occupancyId: 7),
      throwsA(isA<ReportConflictException>()),
    );
  });

  test('failed photo never loses the report; retryPhoto recovers it', () async {
    repo.failPhotoPaths = {'/tmp/b.jpg'};
    final draft = draftOf(photos: ['/tmp/a.jpg', '/tmp/b.jpg']);
    await drafts.write(7, draft);
    final outcome = await submitter.submit(draft: draft, occupancyId: 7);
    expect(outcome.reportId, 42);
    expect(outcome.allPhotosUploaded, isFalse);
    expect(await drafts.read(7), isNull); // report text is safe regardless
    final failed = outcome.photos.singleWhere(
      (p) => p.status == PhotoUploadStatus.failed,
    );

    repo.failPhotoPaths = {};
    final retried = await submitter.retryPhoto(reportId: 42, photo: failed);
    expect(retried.status, PhotoUploadStatus.uploaded);
  });

  // Amendment 10: photo retry must not re-upload when already uploaded (client
  // attachment id / status). Backend sha256 dedup covers lost-response; client
  // must not double-call when status is already uploaded.
  test('retryPhoto is idempotent when photo already uploaded', () async {
    final draft = draftOf(photos: ['/tmp/a.jpg']);
    final outcome = await submitter.submit(draft: draft, occupancyId: 7);
    final photo = outcome.photos.single;
    expect(photo.status, PhotoUploadStatus.uploaded);
    final before = repo.uploaded.length;
    final again = await submitter.retryPhoto(reportId: 42, photo: photo);
    expect(again.status, PhotoUploadStatus.uploaded);
    expect(repo.uploaded.length, before); // no second upload
  });

  // Soft-fail non-Dio photo errors so form always reaches committed-result.
  test('non-Dio photo error marks failed and still returns reportId', () async {
    repo.throwLocalPaths = {'/tmp/a.jpg'};
    final draft = draftOf(photos: ['/tmp/a.jpg']);
    await drafts.write(7, draft);
    final outcome = await submitter.submit(draft: draft, occupancyId: 7);
    expect(outcome.reportId, 42);
    expect(outcome.photos.single.status, PhotoUploadStatus.failed);
    expect(await drafts.read(7), isNull);
  });
}
