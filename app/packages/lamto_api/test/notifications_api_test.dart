import 'package:test/test.dart';
import 'package:lamto_api/lamto_api.dart';


/// tests for NotificationsApi
void main() {
  final instance = LamtoApi().getNotificationsApi();

  group(NotificationsApi, () {
    //Future<PaginatedNotificationFeedList> notificationsList({ int xLamToOccupancy, String cursor, String eventCode, bool unread }) async
    test('test notificationsList', () async {
      // TODO
    });

    //Future notificationsReadCreate(int id) async
    test('test notificationsReadCreate', () async {
      // TODO
    });

  });
}
