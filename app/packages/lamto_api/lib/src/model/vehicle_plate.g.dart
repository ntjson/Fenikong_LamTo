// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'vehicle_plate.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$VehiclePlate extends VehiclePlate {
  @override
  final int id;
  @override
  final String plate;
  @override
  final String status;
  @override
  final DateTime submittedAt;
  @override
  final String reviewNote;

  factory _$VehiclePlate([void Function(VehiclePlateBuilder)? updates]) =>
      (VehiclePlateBuilder()..update(updates))._build();

  _$VehiclePlate._(
      {required this.id,
      required this.plate,
      required this.status,
      required this.submittedAt,
      required this.reviewNote})
      : super._();
  @override
  VehiclePlate rebuild(void Function(VehiclePlateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  VehiclePlateBuilder toBuilder() => VehiclePlateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is VehiclePlate &&
        id == other.id &&
        plate == other.plate &&
        status == other.status &&
        submittedAt == other.submittedAt &&
        reviewNote == other.reviewNote;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, plate.hashCode);
    _$hash = $jc(_$hash, status.hashCode);
    _$hash = $jc(_$hash, submittedAt.hashCode);
    _$hash = $jc(_$hash, reviewNote.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'VehiclePlate')
          ..add('id', id)
          ..add('plate', plate)
          ..add('status', status)
          ..add('submittedAt', submittedAt)
          ..add('reviewNote', reviewNote))
        .toString();
  }
}

class VehiclePlateBuilder
    implements Builder<VehiclePlate, VehiclePlateBuilder> {
  _$VehiclePlate? _$v;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  String? _plate;
  String? get plate => _$this._plate;
  set plate(String? plate) => _$this._plate = plate;

  String? _status;
  String? get status => _$this._status;
  set status(String? status) => _$this._status = status;

  DateTime? _submittedAt;
  DateTime? get submittedAt => _$this._submittedAt;
  set submittedAt(DateTime? submittedAt) => _$this._submittedAt = submittedAt;

  String? _reviewNote;
  String? get reviewNote => _$this._reviewNote;
  set reviewNote(String? reviewNote) => _$this._reviewNote = reviewNote;

  VehiclePlateBuilder() {
    VehiclePlate._defaults(this);
  }

  VehiclePlateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _id = $v.id;
      _plate = $v.plate;
      _status = $v.status;
      _submittedAt = $v.submittedAt;
      _reviewNote = $v.reviewNote;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(VehiclePlate other) {
    _$v = other as _$VehiclePlate;
  }

  @override
  void update(void Function(VehiclePlateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  VehiclePlate build() => _build();

  _$VehiclePlate _build() {
    final _$result = _$v ??
        _$VehiclePlate._(
          id: BuiltValueNullFieldError.checkNotNull(id, r'VehiclePlate', 'id'),
          plate: BuiltValueNullFieldError.checkNotNull(
              plate, r'VehiclePlate', 'plate'),
          status: BuiltValueNullFieldError.checkNotNull(
              status, r'VehiclePlate', 'status'),
          submittedAt: BuiltValueNullFieldError.checkNotNull(
              submittedAt, r'VehiclePlate', 'submittedAt'),
          reviewNote: BuiltValueNullFieldError.checkNotNull(
              reviewNote, r'VehiclePlate', 'reviewNote'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
