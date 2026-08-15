// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'registration_submission.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$RegistrationSubmission extends RegistrationSubmission {
  @override
  final RegistrationStatusEnum status;
  @override
  final String statusToken;
  @override
  final String phone;

  factory _$RegistrationSubmission(
          [void Function(RegistrationSubmissionBuilder)? updates]) =>
      (RegistrationSubmissionBuilder()..update(updates))._build();

  _$RegistrationSubmission._(
      {required this.status, required this.statusToken, required this.phone})
      : super._();
  @override
  RegistrationSubmission rebuild(
          void Function(RegistrationSubmissionBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  RegistrationSubmissionBuilder toBuilder() =>
      RegistrationSubmissionBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is RegistrationSubmission &&
        status == other.status &&
        statusToken == other.statusToken &&
        phone == other.phone;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, status.hashCode);
    _$hash = $jc(_$hash, statusToken.hashCode);
    _$hash = $jc(_$hash, phone.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'RegistrationSubmission')
          ..add('status', status)
          ..add('phone', phone))
        .toString();
  }
}

class RegistrationSubmissionBuilder
    implements Builder<RegistrationSubmission, RegistrationSubmissionBuilder> {
  _$RegistrationSubmission? _$v;

  RegistrationStatusEnum? _status;
  RegistrationStatusEnum? get status => _$this._status;
  set status(RegistrationStatusEnum? status) => _$this._status = status;

  String? _statusToken;
  String? get statusToken => _$this._statusToken;
  set statusToken(String? statusToken) => _$this._statusToken = statusToken;

  String? _phone;
  String? get phone => _$this._phone;
  set phone(String? phone) => _$this._phone = phone;

  RegistrationSubmissionBuilder() {
    RegistrationSubmission._defaults(this);
  }

  RegistrationSubmissionBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _status = $v.status;
      _statusToken = $v.statusToken;
      _phone = $v.phone;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(RegistrationSubmission other) {
    _$v = other as _$RegistrationSubmission;
  }

  @override
  void update(void Function(RegistrationSubmissionBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  RegistrationSubmission build() => _build();

  _$RegistrationSubmission _build() {
    final _$result = _$v ??
        _$RegistrationSubmission._(
          status: BuiltValueNullFieldError.checkNotNull(
              status, r'RegistrationSubmission', 'status'),
          statusToken: BuiltValueNullFieldError.checkNotNull(
              statusToken, r'RegistrationSubmission', 'statusToken'),
          phone: BuiltValueNullFieldError.checkNotNull(
              phone, r'RegistrationSubmission', 'phone'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
