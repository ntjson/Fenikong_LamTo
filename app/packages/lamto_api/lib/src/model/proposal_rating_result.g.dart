// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'proposal_rating_result.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ProposalRatingResult extends ProposalRatingResult {
  @override
  final int id;
  @override
  final int proposalId;
  @override
  final bool satisfied;

  factory _$ProposalRatingResult(
          [void Function(ProposalRatingResultBuilder)? updates]) =>
      (ProposalRatingResultBuilder()..update(updates))._build();

  _$ProposalRatingResult._(
      {required this.id, required this.proposalId, required this.satisfied})
      : super._();
  @override
  ProposalRatingResult rebuild(
          void Function(ProposalRatingResultBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ProposalRatingResultBuilder toBuilder() =>
      ProposalRatingResultBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ProposalRatingResult &&
        id == other.id &&
        proposalId == other.proposalId &&
        satisfied == other.satisfied;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, proposalId.hashCode);
    _$hash = $jc(_$hash, satisfied.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ProposalRatingResult')
          ..add('id', id)
          ..add('proposalId', proposalId)
          ..add('satisfied', satisfied))
        .toString();
  }
}

class ProposalRatingResultBuilder
    implements Builder<ProposalRatingResult, ProposalRatingResultBuilder> {
  _$ProposalRatingResult? _$v;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  int? _proposalId;
  int? get proposalId => _$this._proposalId;
  set proposalId(int? proposalId) => _$this._proposalId = proposalId;

  bool? _satisfied;
  bool? get satisfied => _$this._satisfied;
  set satisfied(bool? satisfied) => _$this._satisfied = satisfied;

  ProposalRatingResultBuilder() {
    ProposalRatingResult._defaults(this);
  }

  ProposalRatingResultBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _id = $v.id;
      _proposalId = $v.proposalId;
      _satisfied = $v.satisfied;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ProposalRatingResult other) {
    _$v = other as _$ProposalRatingResult;
  }

  @override
  void update(void Function(ProposalRatingResultBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ProposalRatingResult build() => _build();

  _$ProposalRatingResult _build() {
    final _$result = _$v ??
        _$ProposalRatingResult._(
          id: BuiltValueNullFieldError.checkNotNull(
              id, r'ProposalRatingResult', 'id'),
          proposalId: BuiltValueNullFieldError.checkNotNull(
              proposalId, r'ProposalRatingResult', 'proposalId'),
          satisfied: BuiltValueNullFieldError.checkNotNull(
              satisfied, r'ProposalRatingResult', 'satisfied'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
