import 'package:shared_preferences/shared_preferences.dart';

/// Persists selected occupancy id per user/install (never the auth token).
class OccupancyStore {
  OccupancyStore([SharedPreferences? prefs]) : _prefsOverride = prefs;

  final SharedPreferences? _prefsOverride;
  static const _prefix = 'lamto_occupancy_';

  Future<SharedPreferences> get _prefs async =>
      _prefsOverride ?? await SharedPreferences.getInstance();

  String _key(String userKey) => '$_prefix$userKey';

  Future<int?> read(String userKey) async {
    final prefs = await _prefs;
    final v = prefs.getInt(_key(userKey));
    return v;
  }

  Future<void> write(String userKey, int id) async {
    final prefs = await _prefs;
    await prefs.setInt(_key(userKey), id);
  }

  Future<void> clear(String userKey) async {
    final prefs = await _prefs;
    await prefs.remove(_key(userKey));
  }
}
