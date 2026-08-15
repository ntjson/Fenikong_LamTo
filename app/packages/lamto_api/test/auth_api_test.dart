import 'package:test/test.dart';
import 'package:lamto_api/lamto_api.dart';


/// tests for AuthApi
void main() {
  final instance = LamtoApi().getAuthApi();

  group(AuthApi, () {
    //Future<TokenResponse> authLoginCreate(LoginRequest loginRequest) async
    test('test authLoginCreate', () async {
      // TODO
    });

    // Log the user out of all sessions I.E. deletes all auth tokens for the user
    //
    //Future authLogoutAllCreate() async
    test('test authLogoutAllCreate', () async {
      // TODO
    });

    //Future authLogoutCreate({ String xInstallId, LogoutInstallIdRequest logoutInstallIdRequest }) async
    test('test authLogoutCreate', () async {
      // TODO
    });

  });
}
