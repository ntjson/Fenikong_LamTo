import 'package:test/test.dart';
import 'package:lamto_api/lamto_api.dart';


/// tests for MeApi
void main() {
  final instance = LamtoApi().getMeApi();

  group(MeApi, () {
    // PATCH resident email/push preferences per event code (Flutter Account).
    //
    //Future<BuiltList<NotificationPreference>> meNotificationPreferencesPartialUpdate({ PatchedNotificationPreferenceUpdateRequest patchedNotificationPreferenceUpdateRequest }) async
    test('test meNotificationPreferencesPartialUpdate', () async {
      // TODO
    });

    //Future<Me> meRetrieve() async
    test('test meRetrieve', () async {
      // TODO
    });

  });
}
