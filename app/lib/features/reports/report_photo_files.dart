import 'dart:io';

import 'package:path_provider/path_provider.dart';

import '../../core/uuid.dart';

/// App-owned durable copies of report draft photos (plan amendment 8).
///
/// Picker/cache paths alone do not survive process death. Before a path is
/// stored on a [ReportDraft], copy the selected image into application
/// documents under `report_draft_photos/<occupancyId>/` via [importPickerPath].
/// Delete owned files when a photo is removed, a draft is cleared/committed,
/// reminted without photos, abandoned, or wiped on logout.
class ReportPhotoFileStore {
  /// [rootOverride] is for tests (temp dir). Production uses
  /// `getApplicationDocumentsDirectory()/report_draft_photos`.
  ReportPhotoFileStore({this._rootOverride});

  final Directory? _rootOverride;

  static const relativeRootName = 'report_draft_photos';

  String _join(String a, String b) => '$a${Platform.pathSeparator}$b';

  String _extension(String path) {
    final base = path.split(RegExp(r'[/\\]')).last;
    final dot = base.lastIndexOf('.');
    if (dot <= 0) return '';
    return base.substring(dot);
  }

  Future<Directory> _root() async {
    final override = _rootOverride;
    if (override != null) {
      if (!await override.exists()) {
        await override.create(recursive: true);
      }
      return override;
    }
    final docs = await getApplicationDocumentsDirectory();
    final root = Directory(_join(docs.path, relativeRootName));
    if (!await root.exists()) {
      await root.create(recursive: true);
    }
    return root;
  }

  Future<Directory> _occupancyDir(int occupancyId) async {
    final root = await _root();
    final dir = Directory(_join(root.path, '$occupancyId'));
    if (!await dir.exists()) {
      await dir.create(recursive: true);
    }
    return dir;
  }

  /// Copies [sourcePath] into app-owned storage for [occupancyId] and returns
  /// the durable absolute path to store on the draft.
  Future<String> importPickerPath({
    required int occupancyId,
    required String sourcePath,
  }) async {
    final dir = await _occupancyDir(occupancyId);
    return _copyInto(dir, sourcePath);
  }

  /// Copies [sourcePath] into app-owned storage for a needs-info reply on
  /// [reportId] and returns the durable absolute path. Lives under
  /// `report_draft_photos/reply_<reportId>/` — the `reply_` prefix cannot
  /// collide with occupancy int dirs, and the logout [clearAll] wipe covers it.
  Future<String> importReplyPickerPath({
    required int reportId,
    required String sourcePath,
  }) async {
    final root = await _root();
    final dir = Directory(_join(root.path, 'reply_$reportId'));
    if (!await dir.exists()) {
      await dir.create(recursive: true);
    }
    return _copyInto(dir, sourcePath);
  }

  Future<String> _copyInto(Directory dir, String sourcePath) async {
    final ext = _extension(sourcePath);
    final destName = '${uuidV4()}${ext.isEmpty ? '.jpg' : ext}';
    final destPath = _join(dir.path, destName);
    await File(sourcePath).copy(destPath);
    return destPath;
  }

  /// Best-effort delete of individual owned (or any) file paths.
  Future<void> deletePaths(Iterable<String> paths) async {
    for (final path in paths) {
      final file = File(path);
      if (await file.exists()) {
        await file.delete();
      }
    }
  }

  /// Deletes all app-owned photo copies for one occupancy.
  Future<void> clearOccupancy(int occupancyId) async {
    final root = await _root();
    final dir = Directory(_join(root.path, '$occupancyId'));
    if (await dir.exists()) {
      await dir.delete(recursive: true);
    }
  }

  /// Deletes every occupancy's photo copies (logout / full wipe).
  Future<void> clearAll() async {
    final root = await _root();
    if (await root.exists()) {
      await root.delete(recursive: true);
    }
  }
}
