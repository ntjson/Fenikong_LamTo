// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'logout_install_id_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$LogoutInstallIdRequest extends LogoutInstallIdRequest {
  @override
  final String? installId;

  factory _$LogoutInstallIdRequest(
          [void Function(LogoutInstallIdRequestBuilder)? updates]) =>
      (LogoutInstallIdRequestBuilder()..update(updates))._build();

  _$LogoutInstallIdRequest._({this.installId}) : super._();
  @override
  LogoutInstallIdRequest rebuild(
          void Function(LogoutInstallIdRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  LogoutInstallIdRequestBuilder toBuilder() =>
      LogoutInstallIdRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is LogoutInstallIdRequest && installId == other.installId;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, installId.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'LogoutInstallIdRequest')
          ..add('installId', installId))
        .toString();
  }
}

class LogoutInstallIdRequestBuilder
    implements Builder<LogoutInstallIdRequest, LogoutInstallIdRequestBuilder> {
  _$LogoutInstallIdRequest? _$v;

  String? _installId;
  String? get installId => _$this._installId;
  set installId(String? installId) => _$this._installId = installId;

  LogoutInstallIdRequestBuilder() {
    LogoutInstallIdRequest._defaults(this);
  }

  LogoutInstallIdRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _installId = $v.installId;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(LogoutInstallIdRequest other) {
    _$v = other as _$LogoutInstallIdRequest;
  }

  @override
  void update(void Function(LogoutInstallIdRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  LogoutInstallIdRequest build() => _build();

  _$LogoutInstallIdRequest _build() {
    final _$result = _$v ??
        _$LogoutInstallIdRequest._(
          installId: installId,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
