// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'report_work_update.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ReportWorkUpdate extends ReportWorkUpdate {
  @override
  final int id;
  @override
  final String cause;
  @override
  final String result;
  @override
  final DateTime createdAt;

  factory _$ReportWorkUpdate(
          [void Function(ReportWorkUpdateBuilder)? updates]) =>
      (ReportWorkUpdateBuilder()..update(updates))._build();

  _$ReportWorkUpdate._(
      {required this.id,
      required this.cause,
      required this.result,
      required this.createdAt})
      : super._();
  @override
  ReportWorkUpdate rebuild(void Function(ReportWorkUpdateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ReportWorkUpdateBuilder toBuilder() =>
      ReportWorkUpdateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ReportWorkUpdate &&
        id == other.id &&
        cause == other.cause &&
        result == other.result &&
        createdAt == other.createdAt;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, cause.hashCode);
    _$hash = $jc(_$hash, result.hashCode);
    _$hash = $jc(_$hash, createdAt.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ReportWorkUpdate')
          ..add('id', id)
          ..add('cause', cause)
          ..add('result', result)
          ..add('createdAt', createdAt))
        .toString();
  }
}

class ReportWorkUpdateBuilder
    implements Builder<ReportWorkUpdate, ReportWorkUpdateBuilder> {
  _$ReportWorkUpdate? _$v;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  String? _cause;
  String? get cause => _$this._cause;
  set cause(String? cause) => _$this._cause = cause;

  String? _result;
  String? get result => _$this._result;
  set result(String? result) => _$this._result = result;

  DateTime? _createdAt;
  DateTime? get createdAt => _$this._createdAt;
  set createdAt(DateTime? createdAt) => _$this._createdAt = createdAt;

  ReportWorkUpdateBuilder() {
    ReportWorkUpdate._defaults(this);
  }

  ReportWorkUpdateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _id = $v.id;
      _cause = $v.cause;
      _result = $v.result;
      _createdAt = $v.createdAt;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ReportWorkUpdate other) {
    _$v = other as _$ReportWorkUpdate;
  }

  @override
  void update(void Function(ReportWorkUpdateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ReportWorkUpdate build() => _build();

  _$ReportWorkUpdate _build() {
    final _$result = _$v ??
        _$ReportWorkUpdate._(
          id: BuiltValueNullFieldError.checkNotNull(
              id, r'ReportWorkUpdate', 'id'),
          cause: BuiltValueNullFieldError.checkNotNull(
              cause, r'ReportWorkUpdate', 'cause'),
          result: BuiltValueNullFieldError.checkNotNull(
              result, r'ReportWorkUpdate', 'result'),
          createdAt: BuiltValueNullFieldError.checkNotNull(
              createdAt, r'ReportWorkUpdate', 'createdAt'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
