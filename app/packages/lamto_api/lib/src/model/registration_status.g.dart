// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'registration_status.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$RegistrationStatus extends RegistrationStatus {
  @override
  final RegistrationStatusEnum status;
  @override
  final String phone;
  @override
  final String building;
  @override
  final String unit;
  @override
  final String? rejectionReason;

  factory _$RegistrationStatus(
          [void Function(RegistrationStatusBuilder)? updates]) =>
      (RegistrationStatusBuilder()..update(updates))._build();

  _$RegistrationStatus._(
      {required this.status,
      required this.phone,
      required this.building,
      required this.unit,
      this.rejectionReason})
      : super._();
  @override
  RegistrationStatus rebuild(
          void Function(RegistrationStatusBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  RegistrationStatusBuilder toBuilder() =>
      RegistrationStatusBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is RegistrationStatus &&
        status == other.status &&
        phone == other.phone &&
        building == other.building &&
        unit == other.unit &&
        rejectionReason == other.rejectionReason;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, status.hashCode);
    _$hash = $jc(_$hash, phone.hashCode);
    _$hash = $jc(_$hash, building.hashCode);
    _$hash = $jc(_$hash, unit.hashCode);
    _$hash = $jc(_$hash, rejectionReason.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'RegistrationStatus')
          ..add('status', status)
          ..add('phone', phone)
          ..add('building', building)
          ..add('unit', unit)
          ..add('rejectionReason', rejectionReason))
        .toString();
  }
}

class RegistrationStatusBuilder
    implements Builder<RegistrationStatus, RegistrationStatusBuilder> {
  _$RegistrationStatus? _$v;

  RegistrationStatusEnum? _status;
  RegistrationStatusEnum? get status => _$this._status;
  set status(RegistrationStatusEnum? status) => _$this._status = status;

  String? _phone;
  String? get phone => _$this._phone;
  set phone(String? phone) => _$this._phone = phone;

  String? _building;
  String? get building => _$this._building;
  set building(String? building) => _$this._building = building;

  String? _unit;
  String? get unit => _$this._unit;
  set unit(String? unit) => _$this._unit = unit;

  String? _rejectionReason;
  String? get rejectionReason => _$this._rejectionReason;
  set rejectionReason(String? rejectionReason) =>
      _$this._rejectionReason = rejectionReason;

  RegistrationStatusBuilder() {
    RegistrationStatus._defaults(this);
  }

  RegistrationStatusBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _status = $v.status;
      _phone = $v.phone;
      _building = $v.building;
      _unit = $v.unit;
      _rejectionReason = $v.rejectionReason;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(RegistrationStatus other) {
    _$v = other as _$RegistrationStatus;
  }

  @override
  void update(void Function(RegistrationStatusBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  RegistrationStatus build() => _build();

  _$RegistrationStatus _build() {
    final _$result = _$v ??
        _$RegistrationStatus._(
          status: BuiltValueNullFieldError.checkNotNull(
              status, r'RegistrationStatus', 'status'),
          phone: BuiltValueNullFieldError.checkNotNull(
              phone, r'RegistrationStatus', 'phone'),
          building: BuiltValueNullFieldError.checkNotNull(
              building, r'RegistrationStatus', 'building'),
          unit: BuiltValueNullFieldError.checkNotNull(
              unit, r'RegistrationStatus', 'unit'),
          rejectionReason: rejectionReason,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
