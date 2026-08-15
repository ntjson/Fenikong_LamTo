// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'gate_device.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$GateDevice extends GateDevice {
  @override
  final String label;
  @override
  final DirectionEnum direction;

  factory _$GateDevice([void Function(GateDeviceBuilder)? updates]) =>
      (GateDeviceBuilder()..update(updates))._build();

  _$GateDevice._({required this.label, required this.direction}) : super._();
  @override
  GateDevice rebuild(void Function(GateDeviceBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  GateDeviceBuilder toBuilder() => GateDeviceBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is GateDevice &&
        label == other.label &&
        direction == other.direction;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, label.hashCode);
    _$hash = $jc(_$hash, direction.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'GateDevice')
          ..add('label', label)
          ..add('direction', direction))
        .toString();
  }
}

class GateDeviceBuilder implements Builder<GateDevice, GateDeviceBuilder> {
  _$GateDevice? _$v;

  String? _label;
  String? get label => _$this._label;
  set label(String? label) => _$this._label = label;

  DirectionEnum? _direction;
  DirectionEnum? get direction => _$this._direction;
  set direction(DirectionEnum? direction) => _$this._direction = direction;

  GateDeviceBuilder() {
    GateDevice._defaults(this);
  }

  GateDeviceBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _label = $v.label;
      _direction = $v.direction;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(GateDevice other) {
    _$v = other as _$GateDevice;
  }

  @override
  void update(void Function(GateDeviceBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  GateDevice build() => _build();

  _$GateDevice _build() {
    final _$result = _$v ??
        _$GateDevice._(
          label: BuiltValueNullFieldError.checkNotNull(
              label, r'GateDevice', 'label'),
          direction: BuiltValueNullFieldError.checkNotNull(
              direction, r'GateDevice', 'direction'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
