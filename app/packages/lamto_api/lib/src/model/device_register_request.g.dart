// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'device_register_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$DeviceRegisterRequest extends DeviceRegisterRequest {
  @override
  final String installId;
  @override
  final String fcmToken;
  @override
  final PlatformEnum platform;
  @override
  final String? appVersion;

  factory _$DeviceRegisterRequest(
          [void Function(DeviceRegisterRequestBuilder)? updates]) =>
      (DeviceRegisterRequestBuilder()..update(updates))._build();

  _$DeviceRegisterRequest._(
      {required this.installId,
      required this.fcmToken,
      required this.platform,
      this.appVersion})
      : super._();
  @override
  DeviceRegisterRequest rebuild(
          void Function(DeviceRegisterRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  DeviceRegisterRequestBuilder toBuilder() =>
      DeviceRegisterRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is DeviceRegisterRequest &&
        installId == other.installId &&
        fcmToken == other.fcmToken &&
        platform == other.platform &&
        appVersion == other.appVersion;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, installId.hashCode);
    _$hash = $jc(_$hash, fcmToken.hashCode);
    _$hash = $jc(_$hash, platform.hashCode);
    _$hash = $jc(_$hash, appVersion.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'DeviceRegisterRequest')
          ..add('installId', installId)
          ..add('fcmToken', fcmToken)
          ..add('platform', platform)
          ..add('appVersion', appVersion))
        .toString();
  }
}

class DeviceRegisterRequestBuilder
    implements Builder<DeviceRegisterRequest, DeviceRegisterRequestBuilder> {
  _$DeviceRegisterRequest? _$v;

  String? _installId;
  String? get installId => _$this._installId;
  set installId(String? installId) => _$this._installId = installId;

  String? _fcmToken;
  String? get fcmToken => _$this._fcmToken;
  set fcmToken(String? fcmToken) => _$this._fcmToken = fcmToken;

  PlatformEnum? _platform;
  PlatformEnum? get platform => _$this._platform;
  set platform(PlatformEnum? platform) => _$this._platform = platform;

  String? _appVersion;
  String? get appVersion => _$this._appVersion;
  set appVersion(String? appVersion) => _$this._appVersion = appVersion;

  DeviceRegisterRequestBuilder() {
    DeviceRegisterRequest._defaults(this);
  }

  DeviceRegisterRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _installId = $v.installId;
      _fcmToken = $v.fcmToken;
      _platform = $v.platform;
      _appVersion = $v.appVersion;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(DeviceRegisterRequest other) {
    _$v = other as _$DeviceRegisterRequest;
  }

  @override
  void update(void Function(DeviceRegisterRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  DeviceRegisterRequest build() => _build();

  _$DeviceRegisterRequest _build() {
    final _$result = _$v ??
        _$DeviceRegisterRequest._(
          installId: BuiltValueNullFieldError.checkNotNull(
              installId, r'DeviceRegisterRequest', 'installId'),
          fcmToken: BuiltValueNullFieldError.checkNotNull(
              fcmToken, r'DeviceRegisterRequest', 'fcmToken'),
          platform: BuiltValueNullFieldError.checkNotNull(
              platform, r'DeviceRegisterRequest', 'platform'),
          appVersion: appVersion,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
