// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'gate_registrations.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$GateRegistrations extends GateRegistrations {
  @override
  final FaceEnrollment? face;
  @override
  final BuiltList<VehiclePlate> plates;

  factory _$GateRegistrations(
          [void Function(GateRegistrationsBuilder)? updates]) =>
      (GateRegistrationsBuilder()..update(updates))._build();

  _$GateRegistrations._({this.face, required this.plates}) : super._();
  @override
  GateRegistrations rebuild(void Function(GateRegistrationsBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  GateRegistrationsBuilder toBuilder() =>
      GateRegistrationsBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is GateRegistrations &&
        face == other.face &&
        plates == other.plates;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, face.hashCode);
    _$hash = $jc(_$hash, plates.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'GateRegistrations')
          ..add('face', face)
          ..add('plates', plates))
        .toString();
  }
}

class GateRegistrationsBuilder
    implements Builder<GateRegistrations, GateRegistrationsBuilder> {
  _$GateRegistrations? _$v;

  FaceEnrollmentBuilder? _face;
  FaceEnrollmentBuilder get face => _$this._face ??= FaceEnrollmentBuilder();
  set face(FaceEnrollmentBuilder? face) => _$this._face = face;

  ListBuilder<VehiclePlate>? _plates;
  ListBuilder<VehiclePlate> get plates =>
      _$this._plates ??= ListBuilder<VehiclePlate>();
  set plates(ListBuilder<VehiclePlate>? plates) => _$this._plates = plates;

  GateRegistrationsBuilder() {
    GateRegistrations._defaults(this);
  }

  GateRegistrationsBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _face = $v.face?.toBuilder();
      _plates = $v.plates.toBuilder();
      _$v = null;
    }
    return this;
  }

  @override
  void replace(GateRegistrations other) {
    _$v = other as _$GateRegistrations;
  }

  @override
  void update(void Function(GateRegistrationsBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  GateRegistrations build() => _build();

  _$GateRegistrations _build() {
    _$GateRegistrations _$result;
    try {
      _$result = _$v ??
          _$GateRegistrations._(
            face: _face?.build(),
            plates: plates.build(),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'face';
        _face?.build();
        _$failedField = 'plates';
        plates.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'GateRegistrations', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
