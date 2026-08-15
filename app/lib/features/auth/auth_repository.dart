import 'package:dio/dio.dart';
import 'package:lamto_api/lamto_api.dart';

/// Paths used by the auth/me APIs — must exist in OpenAPI (contract tests).
/// Prefer generated [AuthApi]/[MeApi]; these constants mirror the generated
/// path strings for contract assertions only.
abstract final class AuthApiPaths {
  static const login = '/api/v1/auth/login';
  static const me = '/api/v1/me';
  static const logout = '/api/v1/auth/logout';
  static const logoutAll = '/api/v1/auth/logout-all';
}

abstract class AuthRepository {
  Future<String> login(String identifier, String password);
  Future<Me> fetchMe();
  Future<void> logout();
  Future<void> logoutAll();
}

/// Thin wrapper over generated dart-dio [AuthApi]/[MeApi] on the shared Dio.
class DioAuthRepository implements AuthRepository {
  DioAuthRepository(Dio dio)
    : _auth = AuthApi(dio, standardSerializers),
      _me = MeApi(dio, standardSerializers);

  final AuthApi _auth;
  final MeApi _me;

  @override
  Future<String> login(String identifier, String password) async {
    final res = await _auth.authLoginCreate(
      loginRequest: LoginRequest(
        (b) => b
          ..identifier = identifier
          ..password = password,
      ),
    );
    return res.data!.token;
  }

  @override
  Future<Me> fetchMe() async {
    final res = await _me.meRetrieve();
    return res.data!;
  }

  @override
  Future<void> logout() async {
    await _auth.authLogoutCreate();
  }

  @override
  Future<void> logoutAll() async {
    await _auth.authLogoutAllCreate();
  }
}
