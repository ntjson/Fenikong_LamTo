import 'dart:typed_data';

import 'package:built_collection/built_collection.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lamto_api/lamto_api.dart';

import '../../core/providers.dart';

/// Paths used by the transparency/account APIs — contract-tested vs OpenAPI.
abstract final class TransparencyApiPaths {
  static const ledger = '/api/v1/ledger';
  static const ledgerDetail = '/api/v1/ledger/{id}';
  static const fundSummary = '/api/v1/fund/summary';
  static const fundSeries = '/api/v1/fund/series';
  static const notifications = '/api/v1/notifications';
  static const notificationRead = '/api/v1/notifications/{id}/read';
  static const devices = '/api/v1/devices';
  static const deviceDelete = '/api/v1/devices/{install_id}';
  static const mePreferences = '/api/v1/me/notification-preferences';
}

abstract class TransparencyRepository {
  Future<FundSummary> fetchFundSummary();
  Future<FundSeries> fetchFundSeries({String range});
  Future<PaginatedLedgerEntryListList> listLedger({
    String? cursor,
    int? year,
    int? month,
  });
  Future<LedgerEntryDetail> fetchLedgerEntry(int id);
  Future<Uint8List> fetchDocument(String downloadUrl);
  Future<PaginatedNotificationFeedList> listNotifications({
    String? cursor,
    String? eventCode,
    bool? unread,
  });
  Future<void> markNotificationRead(int id);
  Future<Device> registerDevice({
    required String installId,
    required String fcmToken,
    required String platform,
    String appVersion = '',
  });
  Future<void> deactivateDevice(String installId);
  Future<List<NotificationPreference>> updatePreference({
    required String eventCode,
    bool? emailEnabled,
    bool? pushEnabled,
  });
}

/// Thin wrapper over the generated dart-dio APIs on the shared Dio
/// (token + X-LamTo-Occupancy interceptors already installed).
class DioTransparencyRepository implements TransparencyRepository {
  DioTransparencyRepository(Dio dio)
    : _ledger = LedgerApi(dio, standardSerializers),
      _documents = DocumentsApi(dio, standardSerializers),
      _fund = FundApi(dio, standardSerializers),
      _notifications = NotificationsApi(dio, standardSerializers),
      _devices = DevicesApi(dio, standardSerializers),
      _me = MeApi(dio, standardSerializers);

  final LedgerApi _ledger;
  final DocumentsApi _documents;
  final FundApi _fund;
  final NotificationsApi _notifications;
  final DevicesApi _devices;
  final MeApi _me;

  @override
  Future<FundSummary> fetchFundSummary() async {
    final res = await _fund.fundSummaryRetrieve();
    return res.data!;
  }

  @override
  Future<FundSeries> fetchFundSeries({String range = '6m'}) async {
    final res = await _fund.fundSeriesRetrieve(range: range);
    return res.data!;
  }

  @override
  Future<PaginatedLedgerEntryListList> listLedger({
    String? cursor,
    int? year,
    int? month,
  }) async {
    final res = await _ledger.ledgerList(
      cursor: cursor,
      year: year,
      month: month,
    );
    return res.data!;
  }

  @override
  Future<LedgerEntryDetail> fetchLedgerEntry(int id) async {
    final res = await _ledger.ledgerRetrieve(id: id);
    return res.data!;
  }

  @override
  Future<Uint8List> fetchDocument(String downloadUrl) async {
    final segments = Uri.parse(downloadUrl).pathSegments;
    if (segments.isEmpty || segments.last.isEmpty) {
      throw StateError('Document URL has no access token');
    }
    final res = await _documents.documentsRetrieve(token: segments.last);
    return res.data!;
  }

  @override
  Future<PaginatedNotificationFeedList> listNotifications({
    String? cursor,
    String? eventCode,
    bool? unread,
  }) async {
    final res = await _notifications.notificationsList(
      cursor: cursor,
      eventCode: eventCode,
      unread: unread,
    );
    return res.data!;
  }

  @override
  Future<void> markNotificationRead(int id) async {
    await _notifications.notificationsReadCreate(id: id);
  }

  @override
  Future<Device> registerDevice({
    required String installId,
    required String fcmToken,
    required String platform,
    String appVersion = '',
  }) async {
    final res = await _devices.devicesCreate(
      deviceRegisterRequest: DeviceRegisterRequest(
        (b) => b
          ..installId = installId
          ..fcmToken = fcmToken
          ..platform = PlatformEnum.valueOf(platform)
          ..appVersion = appVersion,
      ),
    );
    return res.data!;
  }

  @override
  Future<void> deactivateDevice(String installId) async {
    await _devices.devicesDestroy(installId: installId);
  }

  @override
  Future<List<NotificationPreference>> updatePreference({
    required String eventCode,
    bool? emailEnabled,
    bool? pushEnabled,
  }) async {
    final res = await _me.meNotificationPreferencesPartialUpdate(
      patchedNotificationPreferenceUpdateRequest:
          PatchedNotificationPreferenceUpdateRequest(
            (b) => b
              ..preferences =
                  ListBuilder<NotificationPreferenceUpdateItemRequest>([
                    NotificationPreferenceUpdateItemRequest(
                      (i) => i
                        ..eventCode = eventCode
                        ..emailEnabled = emailEnabled
                        ..pushEnabled = pushEnabled,
                    ),
                  ]),
          ),
    );
    return res.data!.toList();
  }
}

final transparencyRepositoryProvider = Provider<TransparencyRepository>(
  (ref) => DioTransparencyRepository(ref.watch(dioProvider)),
);

/// Building-scoped caches rebuild on occupancy change (providers.dart contract).
final fundSummaryProvider = FutureProvider.autoDispose<FundSummary>((ref) {
  ref.watch(occupancyScopedProviders);
  return ref.watch(transparencyRepositoryProvider).fetchFundSummary();
});

/// Ranges accepted by /fund/series, in display order.
const fundSeriesRanges = ['30d', '6m', '12m'];

/// Chart series keyed by range; building-scoped like fundSummaryProvider.
final fundSeriesProvider = FutureProvider.autoDispose
    .family<FundSeries, String>((ref, range) {
      ref.watch(occupancyScopedProviders);
      return ref
          .watch(transparencyRepositoryProvider)
          .fetchFundSeries(range: range);
    });

/// First few published entries for the Home "recent spending" block.
final recentSpendingProvider =
    FutureProvider.autoDispose<List<LedgerEntryList>>((ref) async {
      ref.watch(occupancyScopedProviders);
      final page = await ref.watch(transparencyRepositoryProvider).listLedger();
      return page.results.take(3).toList();
    });

final ledgerDetailProvider = FutureProvider.autoDispose
    .family<LedgerEntryDetail, int>((ref, id) {
      ref.watch(occupancyScopedProviders);
      return ref.watch(transparencyRepositoryProvider).fetchLedgerEntry(id);
    });
