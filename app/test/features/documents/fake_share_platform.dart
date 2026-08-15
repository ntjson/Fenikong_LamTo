import 'package:flutter_test/flutter_test.dart';
import 'package:plugin_platform_interface/plugin_platform_interface.dart';
import 'package:share_plus_platform_interface/share_plus_platform_interface.dart';

/// Records what the app hands to the OS share sheet.
///
/// `SharePlus.instance` captures `SharePlatform.instance` once, on first use,
/// so install this with [install] before the widget under test can share —
/// [setUpAll] is the safe place. Every test in the file then reads the same
/// recorder, which [reset] clears between them.
class FakeSharePlatform extends Fake
    with MockPlatformInterfaceMixin
    implements SharePlatform {
  final shared = <ShareParams>[];

  /// When set, [share] throws it instead of recording — the OS refusing the
  /// hand-off.
  Object? failure;

  static FakeSharePlatform install() {
    final fake = FakeSharePlatform();
    SharePlatform.instance = fake;
    return fake;
  }

  void reset() {
    shared.clear();
    failure = null;
  }

  @override
  Future<ShareResult> share(ShareParams params) async {
    if (failure case final error?) throw error;
    shared.add(params);
    return const ShareResult('test', ShareResultStatus.success);
  }
}
