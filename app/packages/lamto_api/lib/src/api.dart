//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

import 'package:dio/dio.dart';
import 'package:built_value/serializer.dart';
import 'package:lamto_api/src/serializers.dart';
import 'package:lamto_api/src/auth/api_key_auth.dart';
import 'package:lamto_api/src/auth/basic_auth.dart';
import 'package:lamto_api/src/auth/bearer_auth.dart';
import 'package:lamto_api/src/auth/oauth.dart';
import 'package:lamto_api/src/api/auth_api.dart';
import 'package:lamto_api/src/api/bills_api.dart';
import 'package:lamto_api/src/api/cases_api.dart';
import 'package:lamto_api/src/api/devices_api.dart';
import 'package:lamto_api/src/api/documents_api.dart';
import 'package:lamto_api/src/api/fund_api.dart';
import 'package:lamto_api/src/api/gate_api.dart';
import 'package:lamto_api/src/api/ledger_api.dart';
import 'package:lamto_api/src/api/locations_api.dart';
import 'package:lamto_api/src/api/me_api.dart';
import 'package:lamto_api/src/api/notifications_api.dart';
import 'package:lamto_api/src/api/proposals_api.dart';
import 'package:lamto_api/src/api/registration_api.dart';
import 'package:lamto_api/src/api/reports_api.dart';

class LamtoApi {
  static const String basePath = r'http://localhost';

  final Dio dio;
  final Serializers serializers;

  LamtoApi({
    Dio? dio,
    Serializers? serializers,
    String? basePathOverride,
    List<Interceptor>? interceptors,
  })  : this.serializers = serializers ?? standardSerializers,
        this.dio = dio ??
            Dio(BaseOptions(
              baseUrl: basePathOverride ?? basePath,
              connectTimeout: const Duration(milliseconds: 5000),
              receiveTimeout: const Duration(milliseconds: 3000),
            )) {
    if (interceptors == null) {
      this.dio.interceptors.addAll([
        OAuthInterceptor(),
        BasicAuthInterceptor(),
        BearerAuthInterceptor(),
        ApiKeyAuthInterceptor(),
      ]);
    } else {
      this.dio.interceptors.addAll(interceptors);
    }
  }

  void setOAuthToken(String name, String token) {
    if (this.dio.interceptors.any((i) => i is OAuthInterceptor)) {
      (this.dio.interceptors.firstWhere((i) => i is OAuthInterceptor) as OAuthInterceptor).tokens[name] = token;
    }
  }

  void setBearerAuth(String name, String token) {
    if (this.dio.interceptors.any((i) => i is BearerAuthInterceptor)) {
      (this.dio.interceptors.firstWhere((i) => i is BearerAuthInterceptor) as BearerAuthInterceptor).tokens[name] = token;
    }
  }

  void setBasicAuth(String name, String username, String password) {
    if (this.dio.interceptors.any((i) => i is BasicAuthInterceptor)) {
      (this.dio.interceptors.firstWhere((i) => i is BasicAuthInterceptor) as BasicAuthInterceptor).authInfo[name] = BasicAuthInfo(username, password);
    }
  }

  void setApiKey(String name, String apiKey) {
    if (this.dio.interceptors.any((i) => i is ApiKeyAuthInterceptor)) {
      (this.dio.interceptors.firstWhere((element) => element is ApiKeyAuthInterceptor) as ApiKeyAuthInterceptor).apiKeys[name] = apiKey;
    }
  }

  /// Get AuthApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  AuthApi getAuthApi() {
    return AuthApi(dio, serializers);
  }

  /// Get BillsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  BillsApi getBillsApi() {
    return BillsApi(dio, serializers);
  }

  /// Get CasesApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  CasesApi getCasesApi() {
    return CasesApi(dio, serializers);
  }

  /// Get DevicesApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  DevicesApi getDevicesApi() {
    return DevicesApi(dio, serializers);
  }

  /// Get DocumentsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  DocumentsApi getDocumentsApi() {
    return DocumentsApi(dio, serializers);
  }

  /// Get FundApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  FundApi getFundApi() {
    return FundApi(dio, serializers);
  }

  /// Get GateApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  GateApi getGateApi() {
    return GateApi(dio, serializers);
  }

  /// Get LedgerApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  LedgerApi getLedgerApi() {
    return LedgerApi(dio, serializers);
  }

  /// Get LocationsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  LocationsApi getLocationsApi() {
    return LocationsApi(dio, serializers);
  }

  /// Get MeApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  MeApi getMeApi() {
    return MeApi(dio, serializers);
  }

  /// Get NotificationsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  NotificationsApi getNotificationsApi() {
    return NotificationsApi(dio, serializers);
  }

  /// Get ProposalsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  ProposalsApi getProposalsApi() {
    return ProposalsApi(dio, serializers);
  }

  /// Get RegistrationApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  RegistrationApi getRegistrationApi() {
    return RegistrationApi(dio, serializers);
  }

  /// Get ReportsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  ReportsApi getReportsApi() {
    return ReportsApi(dio, serializers);
  }
}
