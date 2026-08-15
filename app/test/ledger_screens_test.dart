import 'dart:async';
import 'dart:typed_data';

import 'package:built_collection/built_collection.dart';
import 'package:built_value/json_object.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lamto/core/failure.dart';
import 'package:lamto/features/ledger/ledger_detail_screen.dart';
import 'package:lamto/features/ledger/ledger_screen.dart';
import 'package:lamto/features/proposals/proposals_repository.dart';
import 'package:lamto/features/transparency/fund_chart.dart';
import 'package:lamto/features/transparency/transparency_repository.dart';
import 'package:lamto/l10n/app_localizations.dart';
import 'package:lamto/theme.dart';
import 'package:lamto_api/lamto_api.dart';
import 'package:pdfrx/pdfrx.dart';
import 'package:plugin_platform_interface/plugin_platform_interface.dart';
import 'package:url_launcher_platform_interface/url_launcher_platform_interface.dart';

import 'features/documents/document_fixtures.dart';
import 'features/documents/fake_share_platform.dart';

LedgerEntryList _entry(
  int id,
  String level, {
  String subject = 'Thay bóng đèn hành lang',
}) => LedgerEntryList(
  (b) => b
    ..id = id
    ..contractorName = 'Acme Co'
    ..actualCostVnd = 900000
    ..publishedAt = DateTime.utc(2026, 7, 10)
    ..integrityStatus = 'VERIFIED'
    ..evidenceLevel = level
    ..whatWasFixed = subject,
);

FundSeries _series(String range) => FundSeries(
  (b) => b
    ..range = range
    ..points = ListBuilder<FundSeriesPoint>([
      for (var i = 0; i < 6; i++)
        FundSeriesPoint(
          (p) => p
            ..periodStart = DateTime.utc(2026, 2 + i, 1)
            ..inflowsVnd = i == 2 ? 200000 : 0
            ..outflowsVnd = i == 4 ? -50000 : 0
            ..balanceVnd = 1500000 + i * 10000,
        ),
    ]),
);

LedgerEntryDetail _detail({String? explorerUrl}) => LedgerEntryDetail(
  (b) => b
    ..id = 42
    ..contractorName = 'Acme Co'
    ..actualCostVnd = 900000
    ..publishedAt = DateTime.utc(2026, 7, 10)
    ..proposedAmountVnd = 950000
    ..integrityStatus = 'VERIFIED'
    ..whatWasFixed = 'Cable secured'
    ..why = 'Worn cable'
    ..explorerUrl = explorerUrl
    ..payload = JsonObject({'proposal_id': 7})
    ..approvers = ListBuilder<JsonObject?>([
      JsonObject({'role': 'board', 'name': 'Ông Minh', 'decision': 'APPROVE'}),
      JsonObject({
        'role': 'resident_rep',
        'name': 'Bà Hoa',
        'decision': 'APPROVE',
      }),
    ])
    ..verification = Verification(
      (v) => v
        ..decision = 'VERIFIED'
        ..verifiedBy = 'Bà Lan'
        ..verifiedAt = DateTime.utc(2026, 7, 9),
    ).toBuilder()
    ..documents = ListBuilder<LedgerDocument>([
      LedgerDocument(
        (d) => d
          ..kind = 'PAYMENT_PROOF'
          ..contentType = 'application/pdf'
          ..filename = 'hoa-don.pdf'
          ..sha256 = 'doc-hash'
          ..downloadUrl = '/api/v1/documents/test-token',
      ),
    ])
    ..corrections = ListBuilder<JsonObject?>()
    ..proof = Proof(
      (p) => p
        ..evidenceLevel = 'LOCAL_SIGNED'
        ..anchoringBackend = 'disabled'
        ..payloadHash = 'ab12cd34'
        ..events = ListBuilder<ProofEvent>([
          ProofEvent(
            (e) => e
              ..eventId = '0xfeed'
              ..eventType = 9
              ..status = 'LOCAL'
              ..evidenceLevel = 'LOCAL_SIGNED'
              ..transactionHash = '',
          ),
        ]),
    ).toBuilder(),
);

class _MockUrlLauncher extends Fake
    with MockPlatformInterfaceMixin
    implements UrlLauncherPlatform {
  String? launchedUrl;
  LaunchOptions? launchOptions;

  @override
  Future<bool> launchUrl(String url, LaunchOptions options) async {
    launchedUrl = url;
    launchOptions = options;
    return true;
  }
}

class _FakeRepo implements TransparencyRepository {
  final periods = <(int?, int?)>[];
  final seriesRanges = <String>[];
  final document = Completer<Uint8List>();
  final documentRetryErrors = <Object>[
    Failure(code: 'permission_denied'),
    StateError('broken file'),
  ];
  int documentCalls = 0;

  @override
  Future<FundSeries> fetchFundSeries({String range = '6m'}) async {
    seriesRanges.add(range);
    return _series(range);
  }

  @override
  Future<PaginatedLedgerEntryListList> listLedger({
    String? cursor,
    int? year,
    int? month,
  }) async {
    periods.add((year, month));
    return PaginatedLedgerEntryListList(
      (b) => b
        ..results = ListBuilder<LedgerEntryList>(
          year == null ? [_entry(42, 'LOCAL_SIGNED')] : [],
        ),
    );
  }

  @override
  Future<LedgerEntryDetail> fetchLedgerEntry(int id) async => _detail();

  @override
  Future<Uint8List> fetchDocument(String downloadUrl) {
    documentCalls++;
    if (documentCalls == 1) return document.future;
    return Future.error(documentRetryErrors.removeAt(0));
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class _SubjectRepo extends _FakeRepo {
  @override
  Future<PaginatedLedgerEntryListList> listLedger({
    String? cursor,
    int? year,
    int? month,
  }) async => PaginatedLedgerEntryListList(
    (b) => b
      ..results = ListBuilder<LedgerEntryList>([
        _entry(1, 'LOCAL_SIGNED'),
        _entry(2, 'LOCAL_SIGNED', subject: ''),
      ]),
  );
}

class _NoVerificationRepo extends _FakeRepo {
  @override
  Future<LedgerEntryDetail> fetchLedgerEntry(int id) async =>
      _detail().rebuild((b) => b.verification = null);
}

class _IntegrityRepo extends _FakeRepo {
  _IntegrityRepo(this.status);
  final String status;

  @override
  Future<LedgerEntryDetail> fetchLedgerEntry(int id) async =>
      _detail().rebuild((b) => b..integrityStatus = status);
}

/// Serves a PDF, so the document tile reaches its viewer.
class _PdfDocumentRepo extends _FakeRepo {

  @override
  Future<Uint8List> fetchDocument(String downloadUrl) async {
    documentCalls++;
    return minimalPdfBytes;
  }
}

class _ExplorerRepo extends _FakeRepo {
  _ExplorerRepo(this.url);
  final String? url;

  @override
  Future<LedgerEntryDetail> fetchLedgerEntry(int id) async =>
      _detail(explorerUrl: url);
}

class _EmptyProposalsRepository implements ProposalsRepository {
  @override
  Future<PaginatedProposalList> listProposals({String? cursor}) async =>
      PaginatedProposalList((b) => b..results = ListBuilder());

  @override
  Future<Proposal> fetchProposal(int id) async => Proposal(
    (b) => b
      ..id = id
      ..buildingId = 1
      ..status = 'PUBLISHED'
      ..purpose = 'Lift repair proposal'
      ..proposedAction = 'Repair lift'
      ..amountVnd = 1000000
      ..contractorName = 'Lift Co'
      ..expectedSchedule = 'August'
      ..versions = ListBuilder()
      ..progress = ListBuilder()
      ..canRate = false,
  );

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

Widget _host(
  Widget child,
  _FakeRepo repo, {
  Locale locale = const Locale('vi'),
}) => ProviderScope(
  overrides: [
    transparencyRepositoryProvider.overrideWithValue(repo),
    proposalsRepositoryProvider.overrideWithValue(_EmptyProposalsRepository()),
  ],
  child: MaterialApp(
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
    locale: locale,
    home: child,
  ),
);

late FakeSharePlatform share;

void main() {
  // Installed once: SharePlus latches the platform on first use.
  setUpAll(() => share = FakeSharePlatform.install());
  setUp(() => share.reset());

  testWidgets('ledger tab switches between ledger and proposals segments', (
    tester,
  ) async {
    final repo = _FakeRepo();
    await tester.pumpWidget(_host(const Scaffold(body: LedgerScreen()), repo));
    await tester.pumpAndSettle();

    expect(find.text('Sổ quỹ'), findsOneWidget);
    expect(find.text('Đề xuất'), findsOneWidget);
    expect(find.text('Acme Co', skipOffstage: false), findsOneWidget);
    await tester.tap(find.text('Đề xuất'));
    await tester.pumpAndSettle();
    expect(find.text('Acme Co', skipOffstage: false), findsNothing);
  });

  testWidgets('ledger tab shows one fixed trailing-year fund chart', (
    tester,
  ) async {
    final repo = _FakeRepo();
    await tester.pumpWidget(_host(const Scaffold(body: LedgerScreen()), repo));
    await tester.pumpAndSettle();
    expect(find.text('Số dư quỹ'), findsOneWidget);
    expect(find.byType(FundChart), findsOneWidget);
    expect(find.byType(LineChart), findsOneWidget);
    expect(find.byType(BarChart), findsOneWidget);
    // Legend names each flow series; color never carries meaning alone.
    expect(find.text('Thu'), findsOneWidget);
    expect(find.text('Chi'), findsOneWidget);
    expect(find.byType(SegmentedButton<String>), findsNothing);
    expect(repo.seriesRanges, ['12m']);
  });

  testWidgets('ledger chart supports large text without overflow', (
    tester,
  ) async {
    final repo = _FakeRepo();
    await tester.pumpWidget(
      _host(
        const MediaQuery(
          data: MediaQueryData(textScaler: TextScaler.linear(2)),
          child: Scaffold(body: LedgerScreen()),
        ),
        repo,
      ),
    );
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
    expect(find.byType(FundChart), findsOneWidget);
  });

  testWidgets('list shows entries with evidence badge and period filter', (
    tester,
  ) async {
    final repo = _FakeRepo();
    await tester.pumpWidget(_host(const Scaffold(body: LedgerScreen()), repo));
    await tester.pumpAndSettle();
    expect(find.text('Acme Co', skipOffstage: false), findsOneWidget);
    expect(
      find.textContaining('Đã ký — chưa bật neo', skipOffstage: false),
      findsOneWidget,
    );

    // Month is a within-year refinement: disabled until a year is chosen
    // (a tap opens no menu, so the item text exists only once, in the field).
    expect(repo.periods, [(null, null)]);
    await tester.tap(find.byType(DropdownButtonFormField<int?>).last);
    await tester.pumpAndSettle();
    expect(find.text('Tháng 3', skipOffstage: false), findsOneWidget);
    expect(repo.periods, [(null, null)]);

    // Choosing a year re-queries with the filter; empty period shows copy.
    final year = DateTime.now().year;
    await tester.tap(find.byType(DropdownButtonFormField<int?>).first);
    await tester.pumpAndSettle();
    await tester.tap(find.text('$year').last);
    await tester.pumpAndSettle();
    expect(repo.periods.last, (year, null));
    // The field keeps showing the selected year (filter state survives the
    // notifier rebuild).
    expect(
      tester
          .widget<DropdownButtonFormField<int?>>(
            find.byType(DropdownButtonFormField<int?>).first,
          )
          .initialValue,
      year,
    );
    expect(
      find.text('Không có khoản chi nào trong kỳ này.', skipOffstage: false),
      findsOneWidget,
    );

    // Month narrows the same year.
    await tester.tap(find.byType(DropdownButtonFormField<int?>).last);
    await tester.pumpAndSettle();
    await tester.tap(find.text('Tháng 3').last);
    await tester.pumpAndSettle();
    expect(repo.periods.last, (year, 3));
  });

  testWidgets('ledger rows lead with the subject and never a bare blank', (
    tester,
  ) async {
    final repo = _SubjectRepo();
    await tester.pumpWidget(_host(const Scaffold(body: LedgerScreen()), repo));
    await tester.pumpAndSettle();

    // Subject present: the story leads the row.
    expect(
      find.text('Thay bóng đèn hành lang', skipOffstage: false),
      findsOneWidget,
    );
    // Subject empty: the constant title stands in.
    expect(
      find.text('Chi tiết khoản chi', skipOffstage: false),
      findsOneWidget,
    );
  });

  testWidgets(
    'detail keeps accountability visible and technical proof disclosed',
    (tester) async {
      final repo = _FakeRepo();
      await tester.pumpWidget(
        _host(const LedgerDetailScreen(entryId: 42), repo),
      );
      await tester.pumpAndSettle();

      expect(find.text('Khoản chi này đã được xác minh'), findsOneWidget);
      expect(find.text('Chuỗi trách nhiệm'), findsOneWidget);
      expect(find.text('Xem đề xuất'), findsOneWidget);
      await tester.tap(find.text('Xem đề xuất'));
      await tester.pumpAndSettle();
      expect(find.text('Lift repair proposal'), findsOneWidget);
      Navigator.pop(tester.element(find.text('Lift repair proposal')));
      await tester.pumpAndSettle();
      expect(find.text('Phản ánh và lý do'), findsOneWidget);
      expect(find.text('ab12cd34'), findsNothing); // hash hidden until expanded
      expect(find.text('Công việc đã hoàn thành'), findsOneWidget);
      expect(find.text('Phê duyệt'), findsOneWidget);
      expect(find.text('Chứng từ thanh toán'), findsOneWidget);
      await tester.scrollUntilVisible(
        find.text('Xác minh độc lập'),
        200,
        scrollable: find.byType(Scrollable).last,
      );
      expect(find.text('Xác minh độc lập'), findsOneWidget);
      expect(find.text('Cable secured'), findsOneWidget);
      expect(find.text('Worn cable'), findsOneWidget);
      expect(find.textContaining('900.000 ₫'), findsWidgets);
      expect(find.textContaining('Ông Minh'), findsOneWidget);
      expect(find.textContaining('Bà Hoa'), findsOneWidget);
      expect(find.textContaining('Bà Lan'), findsOneWidget);

      await tester.scrollUntilVisible(
        find.text('Chi tiết xác thực'),
        200,
        scrollable: find.byType(Scrollable).last,
      );
      await tester.tap(find.text('Chi tiết xác thực'));
      await tester.pumpAndSettle();
      expect(find.text('ab12cd34'), findsOneWidget);
      expect(find.textContaining('0xfeed'), findsOneWidget);
    },
  );

  testWidgets('verified integrity does not require verifier attribution', (
    tester,
  ) async {
    final repo = _NoVerificationRepo();
    await tester.pumpWidget(_host(const LedgerDetailScreen(entryId: 42), repo));
    await tester.pumpAndSettle();

    expect(find.text('Khoản chi này đã được xác minh'), findsOneWidget);
    expect(find.text('Khoản chi này chưa được xác minh đầy đủ'), findsNothing);
  });

  testWidgets('MISMATCH renders its own red conclusion, not routine pending', (
    tester,
  ) async {
    await tester.pumpWidget(
      _host(const LedgerDetailScreen(entryId: 42), _IntegrityRepo('MISMATCH')),
    );
    await tester.pumpAndSettle();

    const headline = 'Bản ghi này không khớp với bằng chứng đã neo';
    expect(find.text(headline), findsOneWidget);
    expect(
      find.text(
        'Dữ liệu đã công bố khác với bằng chứng đã neo cho khoản chi này. '
        'Hãy báo ban quản lý kiểm tra khoản chi.',
      ),
      findsOneWidget,
    );
    expect(find.text('Khoản chi này chưa được xác minh đầy đủ'), findsNothing);
    expect(find.text('Khoản chi này đã được xác minh'), findsNothing);
    // Mismatch Red + error icon: never the amber pending presentation
    // (Separate States Rule — icon and text carry the state, not color alone).
    expect(
      tester.widget<Text>(find.text(headline)).style?.color,
      LamToColors.error,
    );
    expect(find.byIcon(Icons.error_outline), findsOneWidget);
    expect(find.byIcon(Icons.pending_outlined), findsNothing);
  });

  testWidgets('genuinely-pending integrity keeps the amber conclusion', (
    tester,
  ) async {
    await tester.pumpWidget(
      _host(const LedgerDetailScreen(entryId: 42), _IntegrityRepo('UNCHECKED')),
    );
    await tester.pumpAndSettle();

    const headline = 'Khoản chi này chưa được xác minh đầy đủ';
    expect(find.text(headline), findsOneWidget);
    expect(
      find.text('Bản ghi này không khớp với bằng chứng đã neo'),
      findsNothing,
    );
    expect(
      tester.widget<Text>(find.text(headline)).style?.color,
      LamToColors.warning,
    );
    expect(find.byIcon(Icons.pending_outlined), findsOneWidget);
  });

  testWidgets('a downloaded PDF opens in the app, never in a share sheet', (
    tester,
  ) async {
    final repo = _PdfDocumentRepo();
    await tester.pumpWidget(_host(const LedgerDetailScreen(entryId: 42), repo));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Chuỗi trách nhiệm'));
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(
      find.text('hoa-don.pdf'),
      200,
      scrollable: find.byType(Scrollable).last,
    );
    await tester.ensureVisible(find.text('hoa-don.pdf'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('hoa-don.pdf'));
    for (var i = 0; i < 20; i++) {
      await tester.pump(const Duration(milliseconds: 100));
    }

    // `flutter test` has no PDFium, so this asserts where the bytes go — into
    // an in-app viewer, never the OS share sheet. That the pages actually
    // render is a device-level fact, asserted in
    // integration_test/document_viewer_test.dart.
    expect(find.byType(PdfViewer), findsOneWidget);
    expect(share.shared, isEmpty);
    // The filename titles the viewer; the ledger row behind it still shows it.
    expect(find.text('hoa-don.pdf'), findsWidgets);
  });

  testWidgets('document row covers loading, offline, authorization and retry', (
    tester,
  ) async {
    final repo = _FakeRepo();
    await tester.pumpWidget(_host(const LedgerDetailScreen(entryId: 42), repo));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Chuỗi trách nhiệm'));
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(
      find.text('hoa-don.pdf'),
      200,
      scrollable: find.byType(Scrollable).last,
    );
    await tester.ensureVisible(find.text('hoa-don.pdf'));
    await tester.pumpAndSettle();
    expect(find.text('Chứng từ thanh toán'), findsNWidgets(2));
    expect(find.text('Xem hoặc tải xuống'), findsOneWidget);
    await tester.tap(find.text('hoa-don.pdf'));
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    repo.document.completeError(Failure(code: 'network_error'));
    await tester.pumpAndSettle();
    expect(find.textContaining('ngoại tuyến'), findsOneWidget);
    expect(find.text('Thử lại'), findsOneWidget);

    await tester.tap(find.text('Thử lại'));
    await tester.pumpAndSettle();
    expect(find.textContaining('không có quyền'), findsOneWidget);

    await tester.tap(find.text('Thử lại'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Không mở được tài liệu'), findsOneWidget);
    expect(repo.documentCalls, 3);
  });

  testWidgets(
    'with explorer URL, link row renders and opens browser; ExpansionTile is gone and step 5 badge remains',
    (tester) async {
      final mockLauncher = _MockUrlLauncher();
      UrlLauncherPlatform.instance = mockLauncher;

      const explorerUrl = 'https://lamto.example/e/pub-token-123/';
      final repo = _ExplorerRepo(explorerUrl);
      await tester.pumpWidget(
        _host(const LedgerDetailScreen(entryId: 42), repo),
      );
      await tester.pumpAndSettle();

      // Step 5 verification badge remains visible
      await tester.scrollUntilVisible(
        find.text('Xác minh độc lập'),
        200,
        scrollable: find.byType(Scrollable).last,
      );
      expect(find.text('Xác minh độc lập'), findsOneWidget);
      expect(
        find.textContaining('Đã ký — chưa bật neo'),
        findsOneWidget,
      );

      // Raw-hash ExpansionTile is gone
      expect(find.text('Chi tiết xác thực'), findsNothing);
      expect(find.text('ab12cd34'), findsNothing);

      // Explorer link row is rendered
      await tester.scrollUntilVisible(
        find.text('Trình khám phá bằng chứng'),
        200,
        scrollable: find.byType(Scrollable).last,
      );
      expect(find.text('Trình khám phá bằng chứng'), findsOneWidget);
      expect(find.byIcon(Icons.open_in_new), findsWidgets);

      // Tapping launches the external browser with exact URL
      await tester.tap(find.text('Trình khám phá bằng chứng'));
      await tester.pumpAndSettle();

      expect(mockLauncher.launchedUrl, explorerUrl);
      expect(
        mockLauncher.launchOptions?.mode,
        PreferredLaunchMode.externalApplication,
      );
    },
  );

  testWidgets(
    'without explorer URL, the old raw-hash ExpansionTile renders as before',
    (tester) async {
      final repo = _ExplorerRepo(null);
      await tester.pumpWidget(
        _host(const LedgerDetailScreen(entryId: 42), repo),
      );
      await tester.pumpAndSettle();

      // Link row is NOT present
      expect(find.text('Trình khám phá bằng chứng'), findsNothing);

      // Step 5 badge remains visible
      await tester.scrollUntilVisible(
        find.text('Xác minh độc lập'),
        200,
        scrollable: find.byType(Scrollable).last,
      );
      expect(find.text('Xác minh độc lập'), findsOneWidget);
      expect(
        find.textContaining('Đã ký — chưa bật neo'),
        findsOneWidget,
      );

      // ExpansionTile is present
      await tester.scrollUntilVisible(
        find.text('Chi tiết xác thực'),
        200,
        scrollable: find.byType(Scrollable).last,
      );
      expect(find.text('Chi tiết xác thực'), findsOneWidget);

      await tester.tap(find.text('Chi tiết xác thực'));
      await tester.pumpAndSettle();
      expect(find.text('ab12cd34'), findsOneWidget);
      expect(find.textContaining('0xfeed'), findsOneWidget);
    },
  );

  testWidgets(
    'English catalogue uses Transfer proof for chain step and document row',
    (tester) async {
      final repo = _FakeRepo();
      await tester.pumpWidget(
        _host(
          const LedgerDetailScreen(entryId: 42),
          repo,
          locale: const Locale('en'),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Transfer proof'), findsOneWidget); // Step 4
      await tester.scrollUntilVisible(
        find.text('hoa-don.pdf'),
        200,
        scrollable: find.byType(Scrollable).last,
      );
      await tester.ensureVisible(find.text('hoa-don.pdf'));
      await tester.pumpAndSettle();
      expect(find.text('Transfer proof'), findsNWidgets(2)); // Step 4 + Document row
    },
  );
}
