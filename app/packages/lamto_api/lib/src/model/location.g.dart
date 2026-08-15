// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'location.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$Location extends Location {
  @override
  final int id;
  @override
  final String name;
  @override
  final int? parentId;

  factory _$Location([void Function(LocationBuilder)? updates]) =>
      (LocationBuilder()..update(updates))._build();

  _$Location._({required this.id, required this.name, this.parentId})
      : super._();
  @override
  Location rebuild(void Function(LocationBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  LocationBuilder toBuilder() => LocationBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is Location &&
        id == other.id &&
        name == other.name &&
        parentId == other.parentId;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, name.hashCode);
    _$hash = $jc(_$hash, parentId.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'Location')
          ..add('id', id)
          ..add('name', name)
          ..add('parentId', parentId))
        .toString();
  }
}

class LocationBuilder implements Builder<Location, LocationBuilder> {
  _$Location? _$v;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  String? _name;
  String? get name => _$this._name;
  set name(String? name) => _$this._name = name;

  int? _parentId;
  int? get parentId => _$this._parentId;
  set parentId(int? parentId) => _$this._parentId = parentId;

  LocationBuilder() {
    Location._defaults(this);
  }

  LocationBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _id = $v.id;
      _name = $v.name;
      _parentId = $v.parentId;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(Location other) {
    _$v = other as _$Location;
  }

  @override
  void update(void Function(LocationBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  Location build() => _build();

  _$Location _build() {
    final _$result = _$v ??
        _$Location._(
          id: BuiltValueNullFieldError.checkNotNull(id, r'Location', 'id'),
          name:
              BuiltValueNullFieldError.checkNotNull(name, r'Location', 'name'),
          parentId: parentId,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
