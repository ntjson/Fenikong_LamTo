import 'package:built_collection/built_collection.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/features/proposals/proposal_detail_screen.dart';
import 'package:lamto/features/proposals/proposals_list_screen.dart';
import 'package:lamto/features/proposals/proposals_repository.dart';
import 'package:lamto/l10n/app_localizations.dart';
import 'package:lamto/theme.dart';
import 'package:lamto_api/lamto_api.dart';
import 'package:plugin_platform_interface/plugin_platform_interface.dart';
import 'package:url_launcher_platform_interface/url_launcher_platform_interface.dart';

Proposal _proposal({
  bool canRate = true,
  bool includeSettlement = true,
  String? explorerUrl,
}) => Proposal(
  (b) => b
    ..id = 7
    ..buildingId = 1
    ..status = 'COMPLETED'
    ..completedAt = DateTime.utc(2026, 7, 20)
    ..purpose = 'Repair the lobby lift'
    ..proposedAction = 'Replace the control board'
    ..amountVnd = 12500000
    ..contractorName = 'Acme Lift'
    ..expectedSchedule = 'Within 14 days'
    ..canRate = canRate
    ..explorerUrl = explorerUrl
    ..versions = ListBuilder<ProposalVersion>([
      ProposalVersion(
        (v) => v
          ..number = 1
          ..publishedAt = DateTime.utc(2026, 7, 1)
          ..evidenceLevel = 'CHAIN_CONFIRMED'
          ..supportingDocuments = ListBuilder<ProposalSupportingDocument>([
            ProposalSupportingDocument(
              (d) => d
                ..id = 11
                ..filename = 'quotation.pdf'
                ..sha256 = List.filled(64, 'a').join()
                ..downloadUrl = '/api/v1/documents/token',
            ),
          ]),
      ),
      ProposalVersion(
        (v) => v
          ..number = 2
          ..publishedAt = DateTime.utc(2026, 7, 10)
          ..evidenceLevel = 'LOCAL_SIGNED'
          ..supportingDocuments = ListBuilder(),
      ),
    ])
    ..progress = ListBuilder<ProposalProgress>([
      ProposalProgress(
        (u) => u
          ..id = 1
          ..cause = 'Scheduled maintenance'
          ..result = 'Control board installed'
          ..createdAt = DateTime.utc(2026, 7, 18),
      ),
    ])
    ..settlement = includeSettlement
        ? ProposalSettlement(
            (s) => s
              ..amountVnd = 12500000
              ..settledAt = DateTime.utc(2026, 7, 20),
          ).toBuilder()
        : null,
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

class _FakeProposalsRepository implements ProposalsRepository {
  _FakeProposalsRepository({Proposal? proposal})
    : proposal = proposal ?? _proposal();

  final Proposal proposal;
  bool? satisfied;

  @override
  Future<PaginatedProposalList> listProposals({String? cursor}) async =>
      PaginatedProposalList(
        (b) => b..results = ListBuilder<Proposal>([proposal]),
      );

  @override
  Future<Proposal> fetchProposal(int id) async => proposal;

  @override
  Future<ProposalRatingResult> rateProposal({
    required int id,
    required bool satisfied,
    String comment = '',
  }) async {
    this.satisfied = satisfied;
    return ProposalRatingResult(
      (b) => b
        ..id = 1
        ..proposalId = id
        ..satisfied = satisfied,
    );
  }
}

Widget _host(Widget child, _FakeProposalsRepository repository) =>
    ProviderScope(
      overrides: [proposalsRepositoryProvider.overrideWithValue(repository)],
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: const Locale('en'),
        home: child,
      ),
    );

void main() {
  testWidgets('proposal list shows purpose, status and tabular amount', (
    tester,
  ) async {
    final repository = _FakeProposalsRepository();
    await tester.pumpWidget(
      _host(const Scaffold(body: ProposalsListScreen()), repository),
    );
    await tester.pumpAndSettle();

    expect(find.text('Repair the lobby lift'), findsOneWidget);
    expect(find.text('Completed'), findsOneWidget);
    expect(find.textContaining('12.500.000'), findsOneWidget);
  });

  testWidgets('proposal detail shows flat evidence, progress and rating', (
    tester,
  ) async {
    final repository = _FakeProposalsRepository();
    await tester.pumpWidget(
      _host(const ProposalDetailScreen(proposalId: 7), repository),
    );
    await tester.pumpAndSettle();

    // Status uses the one system pill, not a second Material Chip shape.
    expect(find.byType(Chip), findsNothing);
    expect(find.byType(StatusChip), findsWidgets);

    for (final label in [
      'Problem or need',
      'Proposed action',
      'Estimated cost',
      'Contractor',
      'Expected schedule',
      'Published versions',
      'Payment settlement',
    ]) {
      await tester.scrollUntilVisible(
        find.text(label),
        150,
        scrollable: find.byType(Scrollable).last,
      );
      expect(find.text(label), findsOneWidget);
    }
    expect(find.text('Version 1', skipOffstage: false), findsOneWidget);
    expect(
      find.text('Anchored on the blockchain', skipOffstage: false),
      findsOneWidget,
    );
    expect(
      find.text('Control board installed', skipOffstage: false),
      findsOneWidget,
    );
    expect(find.text('quotation.pdf', skipOffstage: false), findsOneWidget);
    expect(find.text('Paid'), findsOneWidget);

    await tester.scrollUntilVisible(
      find.text('Rate the result'),
      150,
      scrollable: find.byType(Scrollable).last,
    );
    await tester.tap(find.text('Rate the result'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Not satisfied'));
    await tester.tap(find.text('Send rating'));
    await tester.pumpAndSettle();
    expect(repository.satisfied, isFalse);
  });

  testWidgets('absent settlement shows no settlement section', (
    tester,
  ) async {
    final repository = _FakeProposalsRepository(
      proposal: _proposal(includeSettlement: false),
    );
    await tester.pumpWidget(
      _host(const ProposalDetailScreen(proposalId: 7), repository),
    );
    await tester.pumpAndSettle();

    expect(find.text('Payment settlement', skipOffstage: false), findsNothing);
  });

  testWidgets('completed proposal already rated has no rating action', (
    tester,
  ) async {
    final repository = _FakeProposalsRepository(
      proposal: _proposal(canRate: false),
    );
    await tester.pumpWidget(
      _host(const ProposalDetailScreen(proposalId: 7), repository),
    );
    await tester.pumpAndSettle();

    expect(find.text('Rate the result', skipOffstage: false), findsNothing);
  });

  testWidgets(
    'with explorer URL, link row renders and opens browser; per-version badges unchanged',
    (tester) async {
      final mockLauncher = _MockUrlLauncher();
      UrlLauncherPlatform.instance = mockLauncher;

      const explorerUrl = 'https://lamto.example/e/pub-token-123/';
      final repository = _FakeProposalsRepository(
        proposal: _proposal(explorerUrl: explorerUrl),
      );
      await tester.pumpWidget(
        _host(const ProposalDetailScreen(proposalId: 7), repository),
      );
      await tester.pumpAndSettle();

      // Per-version badges remain visible
      await tester.scrollUntilVisible(
        find.text('Version 1'),
        150,
        scrollable: find.byType(Scrollable).last,
      );
      expect(
        find.text('Anchored on the blockchain', skipOffstage: false),
        findsOneWidget,
      );

      // Explorer link row is rendered
      await tester.scrollUntilVisible(
        find.text('Evidence explorer'),
        150,
        scrollable: find.byType(Scrollable).last,
      );
      expect(find.text('Evidence explorer'), findsOneWidget);
      expect(find.byIcon(Icons.open_in_new), findsWidgets);

      // Tapping launches the external browser with exact URL
      await tester.tap(find.text('Evidence explorer'));
      await tester.pumpAndSettle();

      expect(mockLauncher.launchedUrl, explorerUrl);
      expect(
        mockLauncher.launchOptions?.mode,
        PreferredLaunchMode.externalApplication,
      );
    },
  );

  testWidgets(
    'without explorer URL, no link appears and per-version badges remain unchanged',
    (tester) async {
      final repository = _FakeProposalsRepository(
        proposal: _proposal(explorerUrl: null),
      );
      await tester.pumpWidget(
        _host(const ProposalDetailScreen(proposalId: 7), repository),
      );
      await tester.pumpAndSettle();

      // Link row is NOT present
      expect(find.text('Evidence explorer'), findsNothing);

      // Per-version badges remain visible
      await tester.scrollUntilVisible(
        find.text('Version 1'),
        150,
        scrollable: find.byType(Scrollable).last,
      );
      expect(
        find.text('Anchored on the blockchain', skipOffstage: false),
        findsOneWidget,
      );
    },
  );
}
