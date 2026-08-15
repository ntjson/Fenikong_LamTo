// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'proposal_progress.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ProposalProgress extends ProposalProgress {
  @override
  final int id;
  @override
  final String cause;
  @override
  final String result;
  @override
  final DateTime createdAt;

  factory _$ProposalProgress(
          [void Function(ProposalProgressBuilder)? updates]) =>
      (ProposalProgressBuilder()..update(updates))._build();

  _$ProposalProgress._(
      {required this.id,
      required this.cause,
      required this.result,
      required this.createdAt})
      : super._();
  @override
  ProposalProgress rebuild(void Function(ProposalProgressBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ProposalProgressBuilder toBuilder() =>
      ProposalProgressBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ProposalProgress &&
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
    return (newBuiltValueToStringHelper(r'ProposalProgress')
          ..add('id', id)
          ..add('cause', cause)
          ..add('result', result)
          ..add('createdAt', createdAt))
        .toString();
  }
}

class ProposalProgressBuilder
    implements Builder<ProposalProgress, ProposalProgressBuilder> {
  _$ProposalProgress? _$v;

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

  ProposalProgressBuilder() {
    ProposalProgress._defaults(this);
  }

  ProposalProgressBuilder get _$this {
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
  void replace(ProposalProgress other) {
    _$v = other as _$ProposalProgress;
  }

  @override
  void update(void Function(ProposalProgressBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ProposalProgress build() => _build();

  _$ProposalProgress _build() {
    final _$result = _$v ??
        _$ProposalProgress._(
          id: BuiltValueNullFieldError.checkNotNull(
              id, r'ProposalProgress', 'id'),
          cause: BuiltValueNullFieldError.checkNotNull(
              cause, r'ProposalProgress', 'cause'),
          result: BuiltValueNullFieldError.checkNotNull(
              result, r'ProposalProgress', 'result'),
          createdAt: BuiltValueNullFieldError.checkNotNull(
              createdAt, r'ProposalProgress', 'createdAt'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
