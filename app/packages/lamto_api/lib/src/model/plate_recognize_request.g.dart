// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'plate_recognize_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$PlateRecognizeRequest extends PlateRecognizeRequest {
  @override
  final String plate;

  factory _$PlateRecognizeRequest(
          [void Function(PlateRecognizeRequestBuilder)? updates]) =>
      (PlateRecognizeRequestBuilder()..update(updates))._build();

  _$PlateRecognizeRequest._({required this.plate}) : super._();
  @override
  PlateRecognizeRequest rebuild(
          void Function(PlateRecognizeRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  PlateRecognizeRequestBuilder toBuilder() =>
      PlateRecognizeRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is PlateRecognizeRequest && plate == other.plate;
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
    return (newBuiltValueToStringHelper(r'PlateRecognizeRequest')
          ..add('plate', plate))
        .toString();
  }
}

class PlateRecognizeRequestBuilder
    implements Builder<PlateRecognizeRequest, PlateRecognizeRequestBuilder> {
  _$PlateRecognizeRequest? _$v;

  String? _plate;
  String? get plate => _$this._plate;
  set plate(String? plate) => _$this._plate = plate;

  PlateRecognizeRequestBuilder() {
    PlateRecognizeRequest._defaults(this);
  }

  PlateRecognizeRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _plate = $v.plate;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(PlateRecognizeRequest other) {
    _$v = other as _$PlateRecognizeRequest;
  }

  @override
  void update(void Function(PlateRecognizeRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  PlateRecognizeRequest build() => _build();

  _$PlateRecognizeRequest _build() {
    final _$result = _$v ??
        _$PlateRecognizeRequest._(
          plate: BuiltValueNullFieldError.checkNotNull(
              plate, r'PlateRecognizeRequest', 'plate'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
