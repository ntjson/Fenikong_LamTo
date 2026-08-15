// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'registration_unit.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$RegistrationUnit extends RegistrationUnit {
  @override
  final int id;
  @override
  final String label;

  factory _$RegistrationUnit(
          [void Function(RegistrationUnitBuilder)? updates]) =>
      (RegistrationUnitBuilder()..update(updates))._build();

  _$RegistrationUnit._({required this.id, required this.label}) : super._();
  @override
  RegistrationUnit rebuild(void Function(RegistrationUnitBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  RegistrationUnitBuilder toBuilder() =>
      RegistrationUnitBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is RegistrationUnit && id == other.id && label == other.label;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, label.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'RegistrationUnit')
          ..add('id', id)
          ..add('label', label))
        .toString();
  }
}

class RegistrationUnitBuilder
    implements Builder<RegistrationUnit, RegistrationUnitBuilder> {
  _$RegistrationUnit? _$v;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  String? _label;
  String? get label => _$this._label;
  set label(String? label) => _$this._label = label;

  RegistrationUnitBuilder() {
    RegistrationUnit._defaults(this);
  }

  RegistrationUnitBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _id = $v.id;
      _label = $v.label;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(RegistrationUnit other) {
    _$v = other as _$RegistrationUnit;
  }

  @override
  void update(void Function(RegistrationUnitBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  RegistrationUnit build() => _build();

  _$RegistrationUnit _build() {
    final _$result = _$v ??
        _$RegistrationUnit._(
          id: BuiltValueNullFieldError.checkNotNull(
              id, r'RegistrationUnit', 'id'),
          label: BuiltValueNullFieldError.checkNotNull(
              label, r'RegistrationUnit', 'label'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
