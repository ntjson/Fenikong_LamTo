import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../core/uuid.dart';

/// A report draft persists across app kill (spec 6.3): text, location,
/// attached photo paths, and the client_ref minted when the draft was born
/// so retries stay idempotent (spec 3.5).
///
/// [photoPaths] must be **app-owned** durable paths only (copied via
/// [ReportPhotoFileStore] under application documents) — not transient
/// picker/cache URIs, so drafts survive process death (plan amendment 8).
class ReportDraft {
  const ReportDraft({
    required this.clientRef,
    this.text = '',
    this.locationId,
    this.locationLabel = '',
    this.photoPaths = const [],
    this.isPrivate = false,
  });

  factory ReportDraft.fresh() => ReportDraft(clientRef: uuidV4());

  final String clientRef;
  final String text;
  final int? locationId;
  final String locationLabel;

  /// App-owned absolute paths under `report_draft_photos/<occupancyId>/`.
  final List<String> photoPaths;
  final bool isPrivate;

  bool get isEmpty => text.isEmpty && locationId == null && photoPaths.isEmpty;

  ReportDraft copyWith({
    String? clientRef,
    String? text,
    int? locationId,
    String? locationLabel,
    List<String>? photoPaths,
    bool? isPrivate,
  }) {
    return ReportDraft(
      clientRef: clientRef ?? this.clientRef,
      text: text ?? this.text,
      locationId: locationId ?? this.locationId,
      locationLabel: locationLabel ?? this.locationLabel,
      photoPaths: photoPaths ?? this.photoPaths,
      isPrivate: isPrivate ?? this.isPrivate,
    );
  }

  Map<String, dynamic> toJson() => {
    'client_ref': clientRef,
    'text': text,
    'location_id': locationId,
    'location_label': locationLabel,
    'photo_paths': photoPaths,
    'is_private': isPrivate,
  };

  factory ReportDraft.fromJson(Map<String, dynamic> json) => ReportDraft(
    clientRef: json['client_ref'] as String,
    text: (json['text'] as String?) ?? '',
    locationId: json['location_id'] as int?,
    locationLabel: (json['location_label'] as String?) ?? '',
    photoPaths: ((json['photo_paths'] as List?) ?? const []).cast<String>(),
    isPrivate: (json['is_private'] as bool?) ?? false,
  );
}

/// Draft persistence keyed by occupancy id (a report belongs to the selected
/// occupancy's unit; locations are building-scoped). Mirrors OccupancyStore.
///
/// **Privacy boundary (plan amendment 7):** drafts may hold resident issue
/// text, location labels, and photo paths. Persistence uses app-private
/// [SharedPreferences] (iOS/Android sandbox — not world-readable by other
/// apps). Keys are only ever written under the `lamto_report_draft_` prefix.
/// Full-disk encryption of prefs is out of scope for this slice; rely on the
/// OS sandbox. Call [clearAll] on logout / logout-all so issue text does not
/// linger after session end.
class ReportDraftStore {
  ReportDraftStore([SharedPreferences? prefs]) : _prefsOverride = prefs;

  final SharedPreferences? _prefsOverride;
  static const _prefix = 'lamto_report_draft_';

  /// Process-wide write/clear chains per occupancy so concurrent autosaves
  /// cannot complete out of order (plan amendment 9 — last enqueue wins), and
  /// so [clearAll] on a fresh instance (logout uses `ReportDraftStore()`)
  /// still awaits in-flight writes from any other instance.
  static final Map<int, Future<void>> _writeChains = {};

  /// Drops static write chains between widget tests (fake-async + unawaited
  /// debounce can otherwise leave a non-completing head that stalls later
  /// tests sharing the same occupancy id).
  @visibleForTesting
  static void debugResetWriteChains() => _writeChains.clear();

  Future<SharedPreferences> get _prefs async =>
      _prefsOverride ?? await SharedPreferences.getInstance();

  String _key(int occupancyId) => '$_prefix$occupancyId';

  Future<void> _enqueue(int occupancyId, Future<void> Function() op) {
    final previous = _writeChains[occupancyId] ?? Future<void>.value();
    // Swallow prior errors so a failed write does not block later ones.
    final next = previous.catchError((Object _) {}).then((_) => op());
    _writeChains[occupancyId] = next;
    return next;
  }

  Future<ReportDraft?> read(int occupancyId) async {
    final raw = (await _prefs).getString(_key(occupancyId));
    if (raw == null) return null;
    try {
      return ReportDraft.fromJson(jsonDecode(raw) as Map<String, dynamic>);
    } on Object {
      return null; // corrupt draft: start fresh rather than crash
    }
  }

  /// Persists [draft] for [occupancyId]. Serialized per occupancy so concurrent
  /// autosave calls apply in enqueue order (last write wins).
  Future<void> write(int occupancyId, ReportDraft draft) {
    return _enqueue(occupancyId, () async {
      await (await _prefs).setString(
        _key(occupancyId),
        jsonEncode(draft.toJson()),
      );
    });
  }

  Future<void> clear(int occupancyId) {
    return _enqueue(occupancyId, () async {
      await (await _prefs).remove(_key(occupancyId));
    });
  }

  /// Whether any occupancy holds a non-empty draft or any report has pending
  /// info-reply photos — the unsent work [clearAll] would destroy. Draft
  /// records decode as JSON maps, reply-photo records as JSON lists.
  Future<bool> hasUnsentWork() async {
    final prefs = await _prefs;
    for (final key in prefs.getKeys()) {
      if (!key.startsWith(_prefix)) continue;
      final raw = prefs.getString(key);
      if (raw == null) continue;
      try {
        final decoded = jsonDecode(raw);
        if (decoded is List) {
          if (decoded.isNotEmpty) return true;
        } else if (decoded is Map<String, dynamic>) {
          if (!ReportDraft.fromJson(decoded).isEmpty) return true;
        }
      } on Object {
        // Corrupt record: nothing restorable, nothing worth warning about.
      }
    }
    return false;
  }

  /// Removes every draft key (all occupancies) **and** every pending
  /// info-reply photo record ([InfoReplyPhotoStore] shares the prefix). Used
  /// on logout so resident issue text does not remain after the session ends
  /// (amendment 7).
  ///
  /// Drains write chains in a loop until empty so a write enqueued while
  /// awaiting cannot re-persist after key removal.
  Future<void> clearAll() async {
    while (_writeChains.isNotEmpty) {
      final pending = List<Future<void>>.from(_writeChains.values);
      await Future.wait(pending.map((f) => f.catchError((Object _) {})));
      // Drop only the futures we waited on; keep any replacement chained
      // during the wait so the next loop pass awaits it too.
      _writeChains.removeWhere((_, future) => pending.contains(future));
    }
    final prefs = await _prefs;
    final keys = prefs.getKeys().where((k) => k.startsWith(_prefix)).toList();
    for (final key in keys) {
      await prefs.remove(key);
    }
  }
}

/// Pending needs-info reply photos per report: the paths of app-owned copies
/// not yet uploaded after the reply text committed (fail-safe doctrine —
/// the issue detail screen restores per-photo retry from this record after
/// process death). Written when the reply commits, shrunk per uploaded photo,
/// removed when empty.
///
/// Keys live under [ReportDraftStore]'s prefix (suffix `reply_photos_<id>`
/// never collides with the drafts' bare occupancy-int suffix) so the logout
/// [ReportDraftStore.clearAll] wipe drops these records too (amendment 7).
class InfoReplyPhotoStore {
  InfoReplyPhotoStore([SharedPreferences? prefs]) : _prefsOverride = prefs;

  final SharedPreferences? _prefsOverride;

  Future<SharedPreferences> get _prefs async =>
      _prefsOverride ?? await SharedPreferences.getInstance();

  String _key(int reportId) => '${ReportDraftStore._prefix}reply_photos_$reportId';

  Future<List<String>> read(int reportId) async {
    final raw = (await _prefs).getString(_key(reportId));
    if (raw == null) return const [];
    try {
      return (jsonDecode(raw) as List).cast<String>();
    } on Object {
      return const []; // corrupt record: nothing restorable
    }
  }

  /// Persists [paths] for [reportId]; an empty list removes the record.
  Future<void> write(int reportId, List<String> paths) async {
    final prefs = await _prefs;
    if (paths.isEmpty) {
      await prefs.remove(_key(reportId));
    } else {
      await prefs.setString(_key(reportId), jsonEncode(paths));
    }
  }
}
