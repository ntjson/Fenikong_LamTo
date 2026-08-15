// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'registration_building.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$RegistrationBuilding extends RegistrationBuilding {
  @override
  final int id;
  @override
  final String name;
  @override
  final BuiltList<RegistrationUnit> units;

  factory _$RegistrationBuilding(
          [void Function(RegistrationBuildingBuilder)? updates]) =>
      (RegistrationBuildingBuilder()..update(updates))._build();

  _$RegistrationBuilding._(
      {required this.id, required this.name, required this.units})
      : super._();
  @override
  RegistrationBuilding rebuild(
          void Function(RegistrationBuildingBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  RegistrationBuildingBuilder toBuilder() =>
      RegistrationBuildingBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is RegistrationBuilding &&
        id == other.id &&
        name == other.name &&
        units == other.units;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, name.hashCode);
    _$hash = $jc(_$hash, units.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'RegistrationBuilding')
          ..add('id', id)
          ..add('name', name)
          ..add('units', units))
        .toString();
  }
}

class RegistrationBuildingBuilder
    implements Builder<RegistrationBuilding, RegistrationBuildingBuilder> {
  _$RegistrationBuilding? _$v;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  String? _name;
  String? get name => _$this._name;
  set name(String? name) => _$this._name = name;

  ListBuilder<RegistrationUnit>? _units;
  ListBuilder<RegistrationUnit> get units =>
      _$this._units ??= ListBuilder<RegistrationUnit>();
  set units(ListBuilder<RegistrationUnit>? units) => _$this._units = units;

  RegistrationBuildingBuilder() {
    RegistrationBuilding._defaults(this);
  }

  RegistrationBuildingBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _id = $v.id;
      _name = $v.name;
      _units = $v.units.toBuilder();
      _$v = null;
    }
    return this;
  }

  @override
  void replace(RegistrationBuilding other) {
    _$v = other as _$RegistrationBuilding;
  }

  @override
  void update(void Function(RegistrationBuildingBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  RegistrationBuilding build() => _build();

  _$RegistrationBuilding _build() {
    _$RegistrationBuilding _$result;
    try {
      _$result = _$v ??
          _$RegistrationBuilding._(
            id: BuiltValueNullFieldError.checkNotNull(
                id, r'RegistrationBuilding', 'id'),
            name: BuiltValueNullFieldError.checkNotNull(
                name, r'RegistrationBuilding', 'name'),
            units: units.build(),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'units';
        units.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'RegistrationBuilding', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
