// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'case_rating_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$CaseRatingRequest extends CaseRatingRequest {
  @override
  final bool satisfied;
  @override
  final String? comment;

  factory _$CaseRatingRequest(
          [void Function(CaseRatingRequestBuilder)? updates]) =>
      (CaseRatingRequestBuilder()..update(updates))._build();

  _$CaseRatingRequest._({required this.satisfied, this.comment}) : super._();
  @override
  CaseRatingRequest rebuild(void Function(CaseRatingRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  CaseRatingRequestBuilder toBuilder() =>
      CaseRatingRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is CaseRatingRequest &&
        satisfied == other.satisfied &&
        comment == other.comment;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, satisfied.hashCode);
    _$hash = $jc(_$hash, comment.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'CaseRatingRequest')
          ..add('satisfied', satisfied)
          ..add('comment', comment))
        .toString();
  }
}

class CaseRatingRequestBuilder
    implements Builder<CaseRatingRequest, CaseRatingRequestBuilder> {
  _$CaseRatingRequest? _$v;

  bool? _satisfied;
  bool? get satisfied => _$this._satisfied;
  set satisfied(bool? satisfied) => _$this._satisfied = satisfied;

  String? _comment;
  String? get comment => _$this._comment;
  set comment(String? comment) => _$this._comment = comment;

  CaseRatingRequestBuilder() {
    CaseRatingRequest._defaults(this);
  }

  CaseRatingRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _satisfied = $v.satisfied;
      _comment = $v.comment;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(CaseRatingRequest other) {
    _$v = other as _$CaseRatingRequest;
  }

  @override
  void update(void Function(CaseRatingRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  CaseRatingRequest build() => _build();

  _$CaseRatingRequest _build() {
    final _$result = _$v ??
        _$CaseRatingRequest._(
          satisfied: BuiltValueNullFieldError.checkNotNull(
              satisfied, r'CaseRatingRequest', 'satisfied'),
          comment: comment,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
