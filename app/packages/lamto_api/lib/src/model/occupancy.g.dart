// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'occupancy.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$Occupancy extends Occupancy {
  @override
  final int id;
  @override
  final String unitLabel;
  @override
  final String buildingName;

  factory _$Occupancy([void Function(OccupancyBuilder)? updates]) =>
      (OccupancyBuilder()..update(updates))._build();

  _$Occupancy._(
      {required this.id, required this.unitLabel, required this.buildingName})
      : super._();
  @override
  Occupancy rebuild(void Function(OccupancyBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  OccupancyBuilder toBuilder() => OccupancyBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is Occupancy &&
        id == other.id &&
        unitLabel == other.unitLabel &&
        buildingName == other.buildingName;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, unitLabel.hashCode);
    _$hash = $jc(_$hash, buildingName.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'Occupancy')
          ..add('id', id)
          ..add('unitLabel', unitLabel)
          ..add('buildingName', buildingName))
        .toString();
  }
}

class OccupancyBuilder implements Builder<Occupancy, OccupancyBuilder> {
  _$Occupancy? _$v;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  String? _unitLabel;
  String? get unitLabel => _$this._unitLabel;
  set unitLabel(String? unitLabel) => _$this._unitLabel = unitLabel;

  String? _buildingName;
  String? get buildingName => _$this._buildingName;
  set buildingName(String? buildingName) => _$this._buildingName = buildingName;

  OccupancyBuilder() {
    Occupancy._defaults(this);
  }

  OccupancyBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _id = $v.id;
      _unitLabel = $v.unitLabel;
      _buildingName = $v.buildingName;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(Occupancy other) {
    _$v = other as _$Occupancy;
  }

  @override
  void update(void Function(OccupancyBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  Occupancy build() => _build();

  _$Occupancy _build() {
    final _$result = _$v ??
        _$Occupancy._(
          id: BuiltValueNullFieldError.checkNotNull(id, r'Occupancy', 'id'),
          unitLabel: BuiltValueNullFieldError.checkNotNull(
              unitLabel, r'Occupancy', 'unitLabel'),
          buildingName: BuiltValueNullFieldError.checkNotNull(
              buildingName, r'Occupancy', 'buildingName'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
