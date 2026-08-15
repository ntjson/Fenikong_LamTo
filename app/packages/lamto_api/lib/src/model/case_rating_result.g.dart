// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'case_rating_result.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$CaseRatingResult extends CaseRatingResult {
  @override
  final int id;
  @override
  final int caseId;
  @override
  final bool satisfied;

  factory _$CaseRatingResult(
          [void Function(CaseRatingResultBuilder)? updates]) =>
      (CaseRatingResultBuilder()..update(updates))._build();

  _$CaseRatingResult._(
      {required this.id, required this.caseId, required this.satisfied})
      : super._();
  @override
  CaseRatingResult rebuild(void Function(CaseRatingResultBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  CaseRatingResultBuilder toBuilder() =>
      CaseRatingResultBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is CaseRatingResult &&
        id == other.id &&
        caseId == other.caseId &&
        satisfied == other.satisfied;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, caseId.hashCode);
    _$hash = $jc(_$hash, satisfied.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'CaseRatingResult')
          ..add('id', id)
          ..add('caseId', caseId)
          ..add('satisfied', satisfied))
        .toString();
  }
}

class CaseRatingResultBuilder
    implements Builder<CaseRatingResult, CaseRatingResultBuilder> {
  _$CaseRatingResult? _$v;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  int? _caseId;
  int? get caseId => _$this._caseId;
  set caseId(int? caseId) => _$this._caseId = caseId;

  bool? _satisfied;
  bool? get satisfied => _$this._satisfied;
  set satisfied(bool? satisfied) => _$this._satisfied = satisfied;

  CaseRatingResultBuilder() {
    CaseRatingResult._defaults(this);
  }

  CaseRatingResultBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _id = $v.id;
      _caseId = $v.caseId;
      _satisfied = $v.satisfied;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(CaseRatingResult other) {
    _$v = other as _$CaseRatingResult;
  }

  @override
  void update(void Function(CaseRatingResultBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  CaseRatingResult build() => _build();

  _$CaseRatingResult _build() {
    final _$result = _$v ??
        _$CaseRatingResult._(
          id: BuiltValueNullFieldError.checkNotNull(
              id, r'CaseRatingResult', 'id'),
          caseId: BuiltValueNullFieldError.checkNotNull(
              caseId, r'CaseRatingResult', 'caseId'),
          satisfied: BuiltValueNullFieldError.checkNotNull(
              satisfied, r'CaseRatingResult', 'satisfied'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
