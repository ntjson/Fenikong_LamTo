// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'device.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$Device extends Device {
  @override
  final String installId;
  @override
  final String platform;
  @override
  final bool active;

  factory _$Device([void Function(DeviceBuilder)? updates]) =>
      (DeviceBuilder()..update(updates))._build();

  _$Device._(
      {required this.installId, required this.platform, required this.active})
      : super._();
  @override
  Device rebuild(void Function(DeviceBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  DeviceBuilder toBuilder() => DeviceBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is Device &&
        installId == other.installId &&
        platform == other.platform &&
        active == other.active;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, installId.hashCode);
    _$hash = $jc(_$hash, platform.hashCode);
    _$hash = $jc(_$hash, active.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'Device')
          ..add('installId', installId)
          ..add('platform', platform)
          ..add('active', active))
        .toString();
  }
}

class DeviceBuilder implements Builder<Device, DeviceBuilder> {
  _$Device? _$v;

  String? _installId;
  String? get installId => _$this._installId;
  set installId(String? installId) => _$this._installId = installId;

  String? _platform;
  String? get platform => _$this._platform;
  set platform(String? platform) => _$this._platform = platform;

  bool? _active;
  bool? get active => _$this._active;
  set active(bool? active) => _$this._active = active;

  DeviceBuilder() {
    Device._defaults(this);
  }

  DeviceBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _installId = $v.installId;
      _platform = $v.platform;
      _active = $v.active;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(Device other) {
    _$v = other as _$Device;
  }

  @override
  void update(void Function(DeviceBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  Device build() => _build();

  _$Device _build() {
    final _$result = _$v ??
        _$Device._(
          installId: BuiltValueNullFieldError.checkNotNull(
              installId, r'Device', 'installId'),
          platform: BuiltValueNullFieldError.checkNotNull(
              platform, r'Device', 'platform'),
          active: BuiltValueNullFieldError.checkNotNull(
              active, r'Device', 'active'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
