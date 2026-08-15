import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lamto_api/lamto_api.dart';

import 'core/adaptive_buttons.dart';
import 'core/adaptive_page_route.dart';
import 'core/error_retry.dart';
import 'core/failure.dart';
import 'core/occupancy.dart';
import 'core/providers.dart';
import 'features/auth/login_screen.dart';
import 'features/settings/api_base_url_tile.dart';
import 'features/auth/occupancy_picker_screen.dart';
import 'features/auth/session_controller.dart';
import 'features/bills/bill_detail_screen.dart';
import 'features/ledger/ledger_detail_screen.dart';
import 'features/notifications/deep_link.dart';
import 'features/notifications/notifications_screen.dart';
import 'features/reports/issue_detail_screen.dart';
import 'features/shell/home_shell.dart';
import 'l10n/app_localizations.dart';
import 'theme.dart';
import 'widgets/brand_identity.dart';

class LamToApp extends StatelessWidget {
  const LamToApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LÀM TỔ',
      theme: lamToTheme(Brightness.light),
      darkTheme: lamToTheme(Brightness.dark),
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: AppLocalizations.supportedLocales,
      locale: const Locale('vi'),
      home: const AppRouter(),
    );
  }
}

class AppRouter extends ConsumerStatefulWidget {
  const AppRouter({super.key});

  @override
  ConsumerState<AppRouter> createState() => _AppRouterState();
}

class _AppRouterState extends ConsumerState<AppRouter> {
  OccupancyHolder? _listened;

  /// Last push-open payload waiting for [SessionAuthenticated] (last-wins).
  Map<String, String>? _pendingPush;
  bool _pushWired = false;
  StreamSubscription<Map<String, String>>? _pushSub;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _wirePushTaps());
  }

  Future<void> _wirePushTaps() async {
    if (_pushWired) return;
    _pushWired = true;
    final source = ref.read(pushTokenSourceProvider);
    final initial = await source.initialMessageData();
    if (initial != null) _openPush(initial);
    _pushSub = source.onMessageOpened.listen(_openPush);
  }

  bool get _isAuthenticated {
    final session = ref.read(sessionControllerProvider);
    return switch (session) {
      AsyncData(value: SessionAuthenticated()) => true,
      _ => false,
    };
  }

  /// Gate navigation: buffer while unauthenticated / bootstrapping; apply when
  /// [SessionAuthenticated]. Destinations still re-fetch via the API (A8).
  void _openPush(Map<String, String> data) {
    if (!mounted) return;
    if (!_isAuthenticated) {
      _pendingPush = data;
      return;
    }
    _navigatePush(data);
  }

  void _flushPendingPush() {
    final pending = _pendingPush;
    if (pending == null || !mounted) return;
    if (!_isAuthenticated) return;
    _pendingPush = null;
    _navigatePush(pending);
  }

  void _navigatePush(Map<String, String> data) {
    if (!mounted) return;
    final link = parsePushLink(type: data['type'], id: data['id']);
    final navigator = Navigator.of(context);
    switch (link) {
      case DeepLinkReport(:final id):
        navigator.push(
          adaptivePageRoute(builder: (_) => IssueDetailScreen(reportId: id)),
        );
      case DeepLinkLedger(:final id):
        selectLedgerTab(ref);
        navigator.push(
          adaptivePageRoute(builder: (_) => LedgerDetailScreen(entryId: id)),
        );
      case DeepLinkFeed():
        navigator.push(
          adaptivePageRoute(builder: (_) => const NotificationsScreen()),
        );
      case DeepLinkBill(:final id):
        navigator.push(
          adaptivePageRoute(builder: (_) => BillDetailScreen(billId: id)),
        );
    }
  }

  @override
  void dispose() {
    _pushSub?.cancel();
    _listened?.removeListener(_onOccupancyChanged);
    super.dispose();
  }

  void _onOccupancyChanged() {
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final session = ref.watch(sessionControllerProvider);
    final holder = ref.watch(occupancyHolderProvider);
    if (!identical(_listened, holder)) {
      _listened?.removeListener(_onOccupancyChanged);
      _listened = holder;
      holder.addListener(_onOccupancyChanged);
    }

    // When auth becomes ready, apply any buffered cold-start / background tap.
    ref.listen(sessionControllerProvider, (previous, next) {
      final authed = switch (next) {
        AsyncData(value: SessionAuthenticated()) => true,
        _ => false,
      };
      if (!authed) return;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) _flushPendingPush();
      });
    });

    return switch (session) {
      AsyncData(:final value) => switch (value) {
        SessionUnauthenticated() => const LoginScreen(),
        SessionAuthenticated(:final me) => _routeAuthenticated(me, holder),
        SessionBootstrapError(:final failure) => BootstrapErrorScreen(
          failure: failure,
          onRetry: () => ref.invalidate(sessionControllerProvider),
        ),
      },
      AsyncError(:final error) => BootstrapErrorScreen(
        failure: error is Failure ? error : Failure(code: 'server_error'),
        onRetry: () => ref.invalidate(sessionControllerProvider),
      ),
      _ => const Scaffold(
        body: SafeArea(
          child: Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                BrandIdentity(width: 220),
                SizedBox(height: 24),
                CircularProgressIndicator.adaptive(),
              ],
            ),
          ),
        ),
      ),
    };
  }

  /// Pure routing over session + occupancy holder (no mutations in build).
  Widget _routeAuthenticated(Me me, OccupancyHolder holder) {
    if (me.occupancies.isEmpty) {
      return const OccupancyPickerScreen.empty();
    }
    if (me.occupancies.length == 1) {
      // Single occupancy is selected during bootstrap; just land on shell.
      return const HomeShell();
    }
    final selected = holder.occupancyId;
    if (selected != null && me.occupancies.any((o) => o.id == selected)) {
      return const HomeShell();
    }
    return OccupancyPickerScreen(me: me);
  }
}

/// Retryable bootstrap failure UI (clarification #1).
///
/// Also exposes API URL editor + sign-out so a dead tunnel / wrong host does
/// not trap the resident on "Retry" only (saved token + unreachable /me).
class BootstrapErrorScreen extends ConsumerWidget {
  const BootstrapErrorScreen({
    required this.failure,
    required this.onRetry,
    super.key,
  });
  final Failure failure;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const BrandIdentity(width: 180),
                  const SizedBox(height: 20),
                  ErrorRetry(error: failure, onRetry: onRetry),
                  const SizedBox(height: 16),
                  // Expanded so tunnel URL is visible without hunting.
                  const ApiBaseUrlTile(initiallyExpanded: true),
                  const SizedBox(height: 16),
                  AdaptiveTextButton(
                    onPressed: () =>
                        ref.read(sessionControllerProvider.notifier).signOut(),
                    child: Text(l10n.signOut),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
