import 'dart:typed_data';

import 'package:built_collection/built_collection.dart';
import 'package:built_value/json_object.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:lamto/core/occupancy.dart';
import 'package:lamto/core/providers.dart';
import 'package:lamto/features/reports/issue_detail_screen.dart';
import 'package:lamto/features/reports/photo_thumbnail.dart';
import 'package:lamto/features/reports/report_draft.dart';
import 'package:lamto/features/reports/report_form_screen.dart';
import 'package:lamto/features/reports/report_photo_files.dart';
import 'package:lamto/features/reports/reports_repository.dart';
import 'package:lamto/l10n/app_localizations.dart';
import 'package:lamto_api/lamto_api.dart';
import 'package:shared_preferences/shared_preferences.dart';

ReportDetail _detail({
  required bool canRate,
  StatusEnum status = StatusEnum.SUBMITTED,
  String? declinedReason,
  MapBuilder<String, JsonObject?>? openInfoRequest,
  List<ReportWorkUpdate>? updates,
  bool completed = true,
  List<int> ledgerEntryIds = const [],
}) => ReportDetail(
  (b) => b
    ..id = 42
    ..text = 'Thang máy kêu to'
    ..status = status
    ..declinedReason = declinedReason
    ..isPrivate = false
    ..locationPathSnapshot = 'Tòa A / Thang máy 2'
    ..unitLabel = 'B-1204'
    ..createdAt = DateTime.utc(2026, 7, 10)
    ..triageStatus = 'SUCCEEDED'
    ..category = 'ELEVATOR'
    ..openInfoRequest = openInfoRequest
    ..photos = ListBuilder<ReportPhoto>()
    ..ledgerEntryIds = ListBuilder<int>(ledgerEntryIds)
    ..cases = ListBuilder<ReportCase>([
      ReportCase(
        (c) => c
          ..id = 1
          ..category = 'ELEVATOR'
          ..urgency = 'HIGH'
          ..deadlineAt = DateTime.utc(2026, 7, 12)
          ..active = true
          ..completedAt = completed ? DateTime.utc(2026, 7, 11) : null
          ..updates = ListBuilder<ReportWorkUpdate>(updates ?? [_update(9)])
          ..canRate = canRate,
      ),
    ]),
);

ReportWorkUpdate _update(int id, {String? cause, String? result}) =>
    ReportWorkUpdate(
      (u) => u
        ..id = id
        ..cause = cause ?? 'Cáp mòn $id'
        ..result = result ?? 'Đã cố định cáp $id'
        ..createdAt = DateTime.utc(2026, 7, 10 + id),
    );

MapBuilder<String, JsonObject?> _infoRequest([JsonObject? message]) =>
    MapBuilder<String, JsonObject?>({
      'id': JsonObject(7),
      'message': ?message,
      'created_at': JsonObject('2026-07-11T00:00:00Z'),
    });

class _FakeRepo implements ReportsRepository {
  _FakeRepo(this.detail);
  ReportDetail detail;
  final ratings = <(int, bool, String)>[];
  final replies = <(int, String)>[];
  final uploads = <(int, String)>[];

  /// Filenames whose upload throws (per-photo failure choreography).
  final failUploads = <String>{};
  int fetches = 0;

  @override
  Future<ReportDetail> fetchReport(int id) async {
    fetches++;
    return detail;
  }

  bool failReply = false;

  @override
  Future<void> replyInfo({required int reportId, required String text}) async {
    if (failReply) {
      failReply = false;
      throw Exception('offline');
    }
    replies.add((reportId, text));
    detail = _detail(canRate: false, status: StatusEnum.IN_REVIEW);
  }

  @override
  Future<CaseRatingResult> rateCase({
    required int caseId,
    required bool satisfied,
    String comment = '',
  }) async {
    ratings.add((caseId, satisfied, comment));
    detail = _detail(canRate: false);
    return CaseRatingResult(
      (b) => b
        ..id = 1
        ..caseId = caseId
        ..satisfied = satisfied,
    );
  }

  @override
  Future<ReportSummary> createReport({
    required String clientRef,
    required String text,
    required int locationId,
    bool isPrivate = false,
  }) => throw UnimplementedError();
  @override
  Future<List<Location>> fetchLocations() => throw UnimplementedError();
  @override
  Future<PaginatedReportSummaryList> listReports({String? cursor}) =>
      throw UnimplementedError();
  @override
  Future<ReportPhoto> uploadPhoto({
    required int reportId,
    required String path,
    required String filename,
  }) async {
    if (failUploads.contains(filename)) {
      throw Exception('upload failed');
    }
    uploads.add((reportId, filename));
    return ReportPhoto(
      (b) => b
        ..id = uploads.length
        ..filename = filename
        ..sha256 = 'sha-$filename'
        ..downloadUrl = '/photos/$filename',
    );
  }
}

/// In-memory picker: the sheet only forwards `xfile.path` to the file store,
/// which is also faked, so no real files are needed.
class _FakePicker extends ImagePicker {
  _FakePicker(this.files);
  final List<XFile> files;

  @override
  Future<List<XFile>> pickMultiImage({
    double? maxWidth,
    double? maxHeight,
    int? imageQuality,
    int? limit,
    bool requestFullMetadata = true,
  }) async => files;

  @override
  Future<XFile?> pickImage({
    required ImageSource source,
    double? maxWidth,
    double? maxHeight,
    int? imageQuality,
    CameraDevice preferredCameraDevice = CameraDevice.rear,
    bool requestFullMetadata = true,
  }) async => files.isEmpty ? null : files.first;
}

/// No real file IO in widget tests (fake-async cannot drive dart:io futures).
class _FakeFileStore extends ReportPhotoFileStore {
  final deleted = <String>[];
  int _n = 0;

  @override
  Future<String> importReplyPickerPath({
    required int reportId,
    required String sourcePath,
  }) async => '/owned/reply_$reportId/photo${++_n}.jpg';

  @override
  Future<void> deletePaths(Iterable<String> paths) async {
    deleted.addAll(paths);
  }
}

class _MissingImageAdapter implements HttpClientAdapter {
  @override
  void close({bool force = false}) {}

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<void>? cancelFuture,
  ) async => ResponseBody.fromString('', 404);
}

Future<void> _pump(
  WidgetTester tester,
  _FakeRepo repo, {
  _FakePicker? picker,
  _FakeFileStore? fileStore,
  Map<String, Object> prefs = const {},
}) async {
  SharedPreferences.setMockInitialValues(prefs);
  final dio = Dio(BaseOptions(baseUrl: 'http://test'))
    ..httpClientAdapter = _MissingImageAdapter();
  final holder = OccupancyHolder()..occupancyId = 7;
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        reportsRepositoryProvider.overrideWithValue(repo),
        dioProvider.overrideWith((ref) => dio),
        occupancyHolderProvider.overrideWithValue(holder),
        reportDraftStoreProvider.overrideWithValue(ReportDraftStore()),
        reportPhotoFileStoreProvider.overrideWithValue(
          fileStore ?? _FakeFileStore(),
        ),
        imagePickerProvider.overrideWithValue(picker ?? _FakePicker(const [])),
      ],
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: const Locale('vi'),
        home: const IssueDetailScreen(reportId: 42),
      ),
    ),
  );
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('renders progress updates in order with causes', (
    tester,
  ) async {
    await _pump(
      tester,
      _FakeRepo(_detail(canRate: false, updates: [_update(1), _update(2)])),
    );

    expect(find.text('Tiến độ xử lý'), findsOneWidget);
    expect(find.text('Cáp mòn 1'), findsOneWidget);
    expect(find.text('Đã cố định cáp 1'), findsOneWidget);
    expect(find.text('Cáp mòn 2'), findsOneWidget);
    expect(find.text('Đã cố định cáp 2'), findsOneWidget);
    expect(
      tester.getTopLeft(find.text('Cáp mòn 1')).dy,
      lessThan(tester.getTopLeft(find.text('Cáp mòn 2')).dy),
    );
  });

  testWidgets('renders the case category from its code in Vietnamese', (
    tester,
  ) async {
    await _pump(tester, _FakeRepo(_detail(canRate: false)));

    expect(
      find.textContaining('Đã ghép vào yêu cầu xử lý: Thang máy'),
      findsOneWidget,
    );
  });

  testWidgets('drops the category when the code is unknown', (tester) async {
    final detail = _detail(canRate: false).rebuild(
      (b) => b.cases[0] = b.cases[0].rebuild((c) => c.category = 'Water leak'),
    );
    await _pump(tester, _FakeRepo(detail));

    expect(find.textContaining('Water leak'), findsNothing);
    expect(find.textContaining('Đã ghép vào yêu cầu xử lý'), findsOneWidget);
    expect(find.textContaining('Đã ghép vào yêu cầu xử lý:'), findsNothing);
  });

  testWidgets('shows completion before the rating action', (tester) async {
    await _pump(tester, _FakeRepo(_detail(canRate: true)));

    expect(find.textContaining('Đã hoàn thành công việc'), findsOneWidget);
    expect(find.text('Đánh giá công việc'), findsOneWidget);
  });

  testWidgets('shows a quiet line when there are no progress updates', (
    tester,
  ) async {
    await _pump(
      tester,
      _FakeRepo(_detail(canRate: false, updates: [], completed: false)),
    );

    expect(find.text('Chưa có cập nhật tiến độ.'), findsOneWidget);
    expect(find.byType(Card), findsNothing);
  });

  testWidgets('shows a declined reason and hides rating', (tester) async {
    await _pump(
      tester,
      _FakeRepo(
        _detail(
          canRate: true,
          status: StatusEnum.DECLINED,
          declinedReason: 'Outside management responsibility',
        ),
      ),
    );

    expect(find.text('Ban quản lý quyết định không tiếp nhận'), findsOneWidget);
    expect(find.text('Outside management responsibility'), findsOneWidget);
    expect(find.text('Đánh giá công việc'), findsNothing);
    expect(find.text('Gửi phản ánh đã chỉnh sửa'), findsOneWidget);

    await tester.tap(find.text('Gửi phản ánh đã chỉnh sửa'));
    await tester.pumpAndSettle();
    expect(find.byType(ReportFormScreen), findsOneWidget);
  });

  testWidgets('rates eligible case as satisfied and refreshes', (tester) async {
    final repo = _FakeRepo(_detail(canRate: true));
    await _pump(tester, repo);
    await tester.tap(find.text('Đánh giá công việc'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Hài lòng'));
    await tester.pump();
    await tester.tap(find.text('Gửi đánh giá'));
    await tester.pumpAndSettle();

    expect(repo.ratings.single, (1, true, ''));
    expect(find.text('Cảm ơn bạn đã đánh giá.'), findsOneWidget);
    expect(find.text('Đánh giá công việc'), findsNothing); // refreshed
  });

  testWidgets('rates eligible case as not satisfied', (tester) async {
    final repo = _FakeRepo(_detail(canRate: true));
    await _pump(tester, repo);
    await tester.tap(find.text('Đánh giá công việc'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Không hài lòng'));
    await tester.pump();
    await tester.tap(find.text('Gửi đánh giá'));
    await tester.pumpAndSettle();

    expect(repo.ratings.single, (1, false, ''));
  });

  testWidgets('retapping the selected rating keeps a valid selection', (
    tester,
  ) async {
    final repo = _FakeRepo(_detail(canRate: true));
    await _pump(tester, repo);
    await tester.tap(find.text('Đánh giá công việc'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Hài lòng'));
    await tester.pump();
    await tester.tap(find.text('Hài lòng'));
    await tester.pump();
    await tester.tap(find.text('Gửi đánh giá'));
    await tester.pumpAndSettle();

    expect(repo.ratings.single, (1, true, ''));
  });

  testWidgets('shows an open management information request', (tester) async {
    await _pump(
      tester,
      _FakeRepo(
        _detail(
          canRate: false,
          status: StatusEnum.NEEDS_INFO,
          openInfoRequest: _infoRequest(
            JsonObject('Please describe the kitchen issue'),
          ),
        ),
      ),
    );

    expect(find.text('Ban quản lý cần thêm thông tin'), findsOneWidget);
    expect(find.text('Please describe the kitchen issue'), findsOneWidget);
    expect(find.text('Gửi trả lời'), findsOneWidget);
  });

  testWidgets('submits an information reply and refreshes the detail', (
    tester,
  ) async {
    final repo = _FakeRepo(
      _detail(
        canRate: false,
        status: StatusEnum.NEEDS_INFO,
        openInfoRequest: _infoRequest(
          JsonObject('Please describe the kitchen issue'),
        ),
      ),
    );
    await _pump(tester, repo);
    await tester.tap(find.text('Gửi trả lời'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField), 'Kitchen tap');
    await tester.pump();
    await tester.tap(find.text('Gửi trả lời').last);
    await tester.pumpAndSettle();

    expect(repo.replies.single, (42, 'Kitchen tap'));
    expect(repo.fetches, 2);
    expect(find.text('Ban quản lý cần thêm thông tin'), findsNothing);
  });

  testWidgets('keeps information reply submit disabled for empty text', (
    tester,
  ) async {
    await _pump(
      tester,
      _FakeRepo(
        _detail(
          canRate: false,
          status: StatusEnum.NEEDS_INFO,
          openInfoRequest: _infoRequest(
            JsonObject('Please describe the kitchen issue'),
          ),
        ),
      ),
    );
    await tester.tap(find.text('Gửi trả lời'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField), '   ');
    await tester.pump();

    final submit = tester.widget<FilledButton>(
      find.widgetWithText(FilledButton, 'Gửi trả lời').last,
    );
    expect(submit.onPressed, isNull);
  });

  testWidgets('sends the reply text first, then attaches every photo', (
    tester,
  ) async {
    final repo = _FakeRepo(
      _detail(
        canRate: false,
        status: StatusEnum.NEEDS_INFO,
        openInfoRequest: _infoRequest(JsonObject('Send a photo of the leak')),
      ),
    );
    final fileStore = _FakeFileStore();
    await _pump(
      tester,
      repo,
      picker: _FakePicker([XFile('/picked/a.jpg'), XFile('/picked/b.jpg')]),
      fileStore: fileStore,
    );
    final semantics = tester.ensureSemantics();

    await tester.tap(find.text('Gửi trả lời'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField), 'Ảnh rò nước đây');
    await tester.pump();

    await tester.tap(find.text('Thêm ảnh'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Chọn từ thư viện'));
    await tester.pumpAndSettle();
    expect(find.byType(PhotoThumbnail), findsNWidgets(2));
    expect(find.bySemanticsLabel(RegExp('Ảnh 1/2')), findsOneWidget);

    await tester.tap(find.text('Gửi trả lời').last);
    await tester.pumpAndSettle();

    expect(repo.replies.single, (42, 'Ảnh rò nước đây'));
    expect(repo.uploads, [(42, 'photo1.jpg'), (42, 'photo2.jpg')]);
    expect(
      find.text('Trả lời của bạn đã được ghi nhận. Đã đính kèm 2/2 ảnh.'),
      findsOneWidget,
    );
    // Uploaded copies cleaned up; no pending record left behind.
    expect(
      fileStore.deleted,
      containsAll(['/owned/reply_42/photo1.jpg', '/owned/reply_42/photo2.jpg']),
    );
    expect(await InfoReplyPhotoStore().read(42), isEmpty);

    await tester.tap(find.text('Đóng'));
    await tester.pumpAndSettle();
    expect(find.text('Ban quản lý cần thêm thông tin'), findsNothing);
    semantics.dispose();
  });

  testWidgets('reply sheet delete removes a picked photo before send', (
    tester,
  ) async {
    final repo = _FakeRepo(
      _detail(
        canRate: false,
        status: StatusEnum.NEEDS_INFO,
        openInfoRequest: _infoRequest(JsonObject('Send a photo')),
      ),
    );
    final fileStore = _FakeFileStore();
    await _pump(
      tester,
      repo,
      picker: _FakePicker([XFile('/picked/a.jpg'), XFile('/picked/b.jpg')]),
      fileStore: fileStore,
    );

    await tester.tap(find.text('Gửi trả lời'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Thêm ảnh'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Chọn từ thư viện'));
    await tester.pumpAndSettle();
    expect(find.byType(PhotoThumbnail), findsNWidgets(2));

    await tester.tap(find.byIcon(Icons.close).first);
    await tester.pumpAndSettle();

    expect(find.byType(PhotoThumbnail), findsOneWidget);
    expect(fileStore.deleted, ['/owned/reply_42/photo1.jpg']);
  });

  testWidgets(
    'keeps the reply and offers per-photo retry when a photo upload fails',
    (tester) async {
      final repo = _FakeRepo(
        _detail(
          canRate: false,
          status: StatusEnum.NEEDS_INFO,
          openInfoRequest: _infoRequest(JsonObject('Send a photo')),
        ),
      );
      repo.failUploads.add('photo1.jpg');
      final fileStore = _FakeFileStore();
      await _pump(
        tester,
        repo,
        picker: _FakePicker([XFile('/picked/a.jpg')]),
        fileStore: fileStore,
      );

      await tester.tap(find.text('Gửi trả lời'));
      await tester.pumpAndSettle();
      await tester.enterText(find.byType(TextField), 'Vòi bếp');
      await tester.tap(find.text('Thêm ảnh'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Chọn từ thư viện'));
      await tester.pumpAndSettle();

      await tester.tap(find.text('Gửi trả lời').last);
      await tester.pumpAndSettle();

      // The words are committed; the photo is not — and the sheet says so.
      expect(repo.replies.single, (42, 'Vòi bếp'));
      expect(repo.uploads, isEmpty);
      expect(
        find.text(
          'Trả lời của bạn đã được ghi nhận. '
          'Một số ảnh chưa tải lên được — thử lại từng ảnh bên dưới.',
        ),
        findsOneWidget,
      );
      expect(await InfoReplyPhotoStore().read(42), [
        '/owned/reply_42/photo1.jpg',
      ]);
      expect(fileStore.deleted, isEmpty);
      // The committed reply is locked: no edit, no resend — only Close.
      expect(tester.widget<TextField>(find.byType(TextField)).enabled, isFalse);
      expect(find.text('Đóng'), findsOneWidget);

      repo.failUploads.clear();
      await tester.tap(find.text('Thử lại'));
      await tester.pumpAndSettle();

      expect(repo.uploads.single, (42, 'photo1.jpg'));
      expect(
        find.text('Trả lời của bạn đã được ghi nhận. Đã đính kèm 1/1 ảnh.'),
        findsOneWidget,
      );
      expect(find.text('Thử lại'), findsNothing);
      expect(await InfoReplyPhotoStore().read(42), isEmpty);
      expect(fileStore.deleted, ['/owned/reply_42/photo1.jpg']);
    },
  );

  testWidgets('a failed reply states nothing was sent and keeps everything', (
    tester,
  ) async {
    final repo = _FakeRepo(
      _detail(
        canRate: false,
        status: StatusEnum.NEEDS_INFO,
        openInfoRequest: _infoRequest(JsonObject('Send a photo')),
      ),
    );
    repo.failReply = true;
    await _pump(tester, repo, picker: _FakePicker([XFile('/picked/a.jpg')]));

    await tester.tap(find.text('Gửi trả lời'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField), 'Vòi bếp');
    await tester.tap(find.text('Thêm ảnh'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Chọn từ thư viện'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Gửi trả lời').last);
    await tester.pumpAndSettle();

    expect(repo.replies, isEmpty);
    expect(find.textContaining('Chưa có gì được gửi đi.'), findsOneWidget);
    expect(find.byType(PhotoThumbnail), findsOneWidget); // photo kept
    expect(tester.widget<TextField>(find.byType(TextField)).enabled, isTrue);
    expect(await InfoReplyPhotoStore().read(42), isEmpty); // not committed

    // The same tap sends the full reply once the network is back.
    await tester.tap(find.text('Gửi trả lời').last);
    await tester.pumpAndSettle();
    expect(repo.replies.single, (42, 'Vòi bếp'));
    expect(
      find.text('Trả lời của bạn đã được ghi nhận. Đã đính kèm 1/1 ảnh.'),
      findsOneWidget,
    );
  });

  testWidgets(
    'restores pending reply photos after restart with working retry',
    (tester) async {
      final repo = _FakeRepo(
        _detail(canRate: false, status: StatusEnum.IN_REVIEW),
      );
      final fileStore = _FakeFileStore();
      await _pump(
        tester,
        repo,
        fileStore: fileStore,
        prefs: {
          'lamto_report_draft_reply_photos_42': '["/owned/reply_42/leak.jpg"]',
        },
      );

      expect(
        find.text('Ảnh trả lời chưa tải lên được — thử lại từng ảnh.'),
        findsOneWidget,
      );
      // Thumbnail with retry, never a minted filename.
      expect(find.byType(PhotoThumbnail), findsOneWidget);
      expect(find.text('leak.jpg'), findsNothing);

      await tester.tap(find.text('Thử lại'));
      await tester.pumpAndSettle();

      expect(repo.uploads.single, (42, 'leak.jpg'));
      expect(fileStore.deleted, ['/owned/reply_42/leak.jpg']);
      expect(find.byType(PhotoThumbnail), findsNothing);
      expect(await InfoReplyPhotoStore().read(42), isEmpty);
      expect(repo.fetches, 2); // photo strip refreshed after the upload landed
    },
  );

  testWidgets('ignores malformed open information request messages', (
    tester,
  ) async {
    for (final request in [
      _infoRequest(),
      MapBuilder<String, JsonObject?>({'message': null}),
      _infoRequest(JsonObject(7)),
    ]) {
      await _pump(
        tester,
        _FakeRepo(
          _detail(
            canRate: false,
            status: StatusEnum.NEEDS_INFO,
            openInfoRequest: request,
          ),
        ),
      );
      expect(tester.takeException(), isNull);
      expect(find.text('Ban quản lý cần thêm thông tin'), findsNothing);
    }
  });

  testWidgets('published spending is reachable from its resident report', (
    tester,
  ) async {
    await _pump(
      tester,
      _FakeRepo(_detail(canRate: false, ledgerEntryIds: const [17])),
    );
    await tester.scrollUntilVisible(
      find.text('Chi tiết khoản chi'),
      200,
      scrollable: find.byType(Scrollable).last,
    );
    expect(find.text('Chi tiết khoản chi'), findsOneWidget);
  });
}
