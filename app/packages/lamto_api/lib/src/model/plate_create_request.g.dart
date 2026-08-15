// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'plate_create_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$PlateCreateRequest extends PlateCreateRequest {
  @override
  final String plate;

  factory _$PlateCreateRequest(
          [void Function(PlateCreateRequestBuilder)? updates]) =>
      (PlateCreateRequestBuilder()..update(updates))._build();

  _$PlateCreateRequest._({required this.plate}) : super._();
  @override
  PlateCreateRequest rebuild(
          void Function(PlateCreateRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  PlateCreateRequestBuilder toBuilder() =>
      PlateCreateRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is PlateCreateRequest && plate == other.plate;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, plate.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'PlateCreateRequest')
          ..add('plate', plate))
        .toString();
  }
}

class PlateCreateRequestBuilder
    implements Builder<PlateCreateRequest, PlateCreateRequestBuilder> {
  _$PlateCreateRequest? _$v;

  String? _plate;
  String? get plate => _$this._plate;
  set plate(String? plate) => _$this._plate = plate;

  PlateCreateRequestBuilder() {
    PlateCreateRequest._defaults(this);
  }

  PlateCreateRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _plate = $v.plate;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(PlateCreateRequest other) {
    _$v = other as _$PlateCreateRequest;
  }

  @override
  void update(void Function(PlateCreateRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  PlateCreateRequest build() => _build();

  _$PlateCreateRequest _build() {
    final _$result = _$v ??
        _$PlateCreateRequest._(
          plate: BuiltValueNullFieldError.checkNotNull(
              plate, r'PlateCreateRequest', 'plate'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
