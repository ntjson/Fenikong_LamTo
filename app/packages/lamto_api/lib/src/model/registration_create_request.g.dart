// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'registration_create_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$RegistrationCreateRequest extends RegistrationCreateRequest {
  @override
  final String fullName;
  @override
  final String phone;
  @override
  final String? email;
  @override
  final String password;
  @override
  final int buildingId;
  @override
  final int unitId;

  factory _$RegistrationCreateRequest(
          [void Function(RegistrationCreateRequestBuilder)? updates]) =>
      (RegistrationCreateRequestBuilder()..update(updates))._build();

  _$RegistrationCreateRequest._(
      {required this.fullName,
      required this.phone,
      this.email,
      required this.password,
      required this.buildingId,
      required this.unitId})
      : super._();
  @override
  RegistrationCreateRequest rebuild(
          void Function(RegistrationCreateRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  RegistrationCreateRequestBuilder toBuilder() =>
      RegistrationCreateRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is RegistrationCreateRequest &&
        fullName == other.fullName &&
        phone == other.phone &&
        email == other.email &&
        password == other.password &&
        buildingId == other.buildingId &&
        unitId == other.unitId;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, fullName.hashCode);
    _$hash = $jc(_$hash, phone.hashCode);
    _$hash = $jc(_$hash, email.hashCode);
    _$hash = $jc(_$hash, password.hashCode);
    _$hash = $jc(_$hash, buildingId.hashCode);
    _$hash = $jc(_$hash, unitId.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'RegistrationCreateRequest')
          ..add('fullName', fullName)
          ..add('phone', phone)
          ..add('email', email)
          ..add('buildingId', buildingId)
          ..add('unitId', unitId))
        .toString();
  }
}

class RegistrationCreateRequestBuilder
    implements
        Builder<RegistrationCreateRequest, RegistrationCreateRequestBuilder> {
  _$RegistrationCreateRequest? _$v;

  String? _fullName;
  String? get fullName => _$this._fullName;
  set fullName(String? fullName) => _$this._fullName = fullName;

  String? _phone;
  String? get phone => _$this._phone;
  set phone(String? phone) => _$this._phone = phone;

  String? _email;
  String? get email => _$this._email;
  set email(String? email) => _$this._email = email;

  String? _password;
  String? get password => _$this._password;
  set password(String? password) => _$this._password = password;

  int? _buildingId;
  int? get buildingId => _$this._buildingId;
  set buildingId(int? buildingId) => _$this._buildingId = buildingId;

  int? _unitId;
  int? get unitId => _$this._unitId;
  set unitId(int? unitId) => _$this._unitId = unitId;

  RegistrationCreateRequestBuilder() {
    RegistrationCreateRequest._defaults(this);
  }

  RegistrationCreateRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _fullName = $v.fullName;
      _phone = $v.phone;
      _email = $v.email;
      _password = $v.password;
      _buildingId = $v.buildingId;
      _unitId = $v.unitId;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(RegistrationCreateRequest other) {
    _$v = other as _$RegistrationCreateRequest;
  }

  @override
  void update(void Function(RegistrationCreateRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  RegistrationCreateRequest build() => _build();

  _$RegistrationCreateRequest _build() {
    final _$result = _$v ??
        _$RegistrationCreateRequest._(
          fullName: BuiltValueNullFieldError.checkNotNull(
              fullName, r'RegistrationCreateRequest', 'fullName'),
          phone: BuiltValueNullFieldError.checkNotNull(
              phone, r'RegistrationCreateRequest', 'phone'),
          email: email,
          password: BuiltValueNullFieldError.checkNotNull(
              password, r'RegistrationCreateRequest', 'password'),
          buildingId: BuiltValueNullFieldError.checkNotNull(
              buildingId, r'RegistrationCreateRequest', 'buildingId'),
          unitId: BuiltValueNullFieldError.checkNotNull(
              unitId, r'RegistrationCreateRequest', 'unitId'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
