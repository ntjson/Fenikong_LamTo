// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'proposal_comparison.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ProposalComparison extends ProposalComparison {
  @override
  final String direction;
  @override
  final int percentage;
  @override
  final String range;
  @override
  final String reasoning;
  @override
  final String source_;

  factory _$ProposalComparison(
          [void Function(ProposalComparisonBuilder)? updates]) =>
      (ProposalComparisonBuilder()..update(updates))._build();

  _$ProposalComparison._(
      {required this.direction,
      required this.percentage,
      required this.range,
      required this.reasoning,
      required this.source_})
      : super._();
  @override
  ProposalComparison rebuild(
          void Function(ProposalComparisonBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ProposalComparisonBuilder toBuilder() =>
      ProposalComparisonBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ProposalComparison &&
        direction == other.direction &&
        percentage == other.percentage &&
        range == other.range &&
        reasoning == other.reasoning &&
        source_ == other.source_;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, direction.hashCode);
    _$hash = $jc(_$hash, percentage.hashCode);
    _$hash = $jc(_$hash, range.hashCode);
    _$hash = $jc(_$hash, reasoning.hashCode);
    _$hash = $jc(_$hash, source_.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ProposalComparison')
          ..add('direction', direction)
          ..add('percentage', percentage)
          ..add('range', range)
          ..add('reasoning', reasoning)
          ..add('source_', source_))
        .toString();
  }
}

class ProposalComparisonBuilder
    implements Builder<ProposalComparison, ProposalComparisonBuilder> {
  _$ProposalComparison? _$v;

  String? _direction;
  String? get direction => _$this._direction;
  set direction(String? direction) => _$this._direction = direction;

  int? _percentage;
  int? get percentage => _$this._percentage;
  set percentage(int? percentage) => _$this._percentage = percentage;

  String? _range;
  String? get range => _$this._range;
  set range(String? range) => _$this._range = range;

  String? _reasoning;
  String? get reasoning => _$this._reasoning;
  set reasoning(String? reasoning) => _$this._reasoning = reasoning;

  String? _source_;
  String? get source_ => _$this._source_;
  set source_(String? source_) => _$this._source_ = source_;

  ProposalComparisonBuilder() {
    ProposalComparison._defaults(this);
  }

  ProposalComparisonBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _direction = $v.direction;
      _percentage = $v.percentage;
      _range = $v.range;
      _reasoning = $v.reasoning;
      _source_ = $v.source_;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ProposalComparison other) {
    _$v = other as _$ProposalComparison;
  }

  @override
  void update(void Function(ProposalComparisonBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ProposalComparison build() => _build();

  _$ProposalComparison _build() {
    final _$result = _$v ??
        _$ProposalComparison._(
          direction: BuiltValueNullFieldError.checkNotNull(
              direction, r'ProposalComparison', 'direction'),
          percentage: BuiltValueNullFieldError.checkNotNull(
              percentage, r'ProposalComparison', 'percentage'),
          range: BuiltValueNullFieldError.checkNotNull(
              range, r'ProposalComparison', 'range'),
          reasoning: BuiltValueNullFieldError.checkNotNull(
              reasoning, r'ProposalComparison', 'reasoning'),
          source_: BuiltValueNullFieldError.checkNotNull(
              source_, r'ProposalComparison', 'source_'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
