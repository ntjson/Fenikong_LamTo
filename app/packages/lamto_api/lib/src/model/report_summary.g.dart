// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'report_summary.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ReportSummary extends ReportSummary {
  @override
  final int id;
  @override
  final String text;
  @override
  final StatusEnum status;
  @override
  final bool isPrivate;
  @override
  final String locationPathSnapshot;
  @override
  final DateTime createdAt;

  factory _$ReportSummary([void Function(ReportSummaryBuilder)? updates]) =>
      (ReportSummaryBuilder()..update(updates))._build();

  _$ReportSummary._(
      {required this.id,
      required this.text,
      required this.status,
      required this.isPrivate,
      required this.locationPathSnapshot,
      required this.createdAt})
      : super._();
  @override
  ReportSummary rebuild(void Function(ReportSummaryBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ReportSummaryBuilder toBuilder() => ReportSummaryBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ReportSummary &&
        id == other.id &&
        text == other.text &&
        status == other.status &&
        isPrivate == other.isPrivate &&
        locationPathSnapshot == other.locationPathSnapshot &&
        createdAt == other.createdAt;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, text.hashCode);
    _$hash = $jc(_$hash, status.hashCode);
    _$hash = $jc(_$hash, isPrivate.hashCode);
    _$hash = $jc(_$hash, locationPathSnapshot.hashCode);
    _$hash = $jc(_$hash, createdAt.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ReportSummary')
          ..add('id', id)
          ..add('text', text)
          ..add('status', status)
          ..add('isPrivate', isPrivate)
          ..add('locationPathSnapshot', locationPathSnapshot)
          ..add('createdAt', createdAt))
        .toString();
  }
}

class ReportSummaryBuilder
    implements Builder<ReportSummary, ReportSummaryBuilder> {
  _$ReportSummary? _$v;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  String? _text;
  String? get text => _$this._text;
  set text(String? text) => _$this._text = text;

  StatusEnum? _status;
  StatusEnum? get status => _$this._status;
  set status(StatusEnum? status) => _$this._status = status;

  bool? _isPrivate;
  bool? get isPrivate => _$this._isPrivate;
  set isPrivate(bool? isPrivate) => _$this._isPrivate = isPrivate;

  String? _locationPathSnapshot;
  String? get locationPathSnapshot => _$this._locationPathSnapshot;
  set locationPathSnapshot(String? locationPathSnapshot) =>
      _$this._locationPathSnapshot = locationPathSnapshot;

  DateTime? _createdAt;
  DateTime? get createdAt => _$this._createdAt;
  set createdAt(DateTime? createdAt) => _$this._createdAt = createdAt;

  ReportSummaryBuilder() {
    ReportSummary._defaults(this);
  }

  ReportSummaryBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _id = $v.id;
      _text = $v.text;
      _status = $v.status;
      _isPrivate = $v.isPrivate;
      _locationPathSnapshot = $v.locationPathSnapshot;
      _createdAt = $v.createdAt;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ReportSummary other) {
    _$v = other as _$ReportSummary;
  }

  @override
  void update(void Function(ReportSummaryBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ReportSummary build() => _build();

  _$ReportSummary _build() {
    final _$result = _$v ??
        _$ReportSummary._(
          id: BuiltValueNullFieldError.checkNotNull(id, r'ReportSummary', 'id'),
          text: BuiltValueNullFieldError.checkNotNull(
              text, r'ReportSummary', 'text'),
          status: BuiltValueNullFieldError.checkNotNull(
              status, r'ReportSummary', 'status'),
          isPrivate: BuiltValueNullFieldError.checkNotNull(
              isPrivate, r'ReportSummary', 'isPrivate'),
          locationPathSnapshot: BuiltValueNullFieldError.checkNotNull(
              locationPathSnapshot, r'ReportSummary', 'locationPathSnapshot'),
          createdAt: BuiltValueNullFieldError.checkNotNull(
              createdAt, r'ReportSummary', 'createdAt'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
