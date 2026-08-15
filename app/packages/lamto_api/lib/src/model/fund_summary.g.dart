// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'fund_summary.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$FundSummary extends FundSummary {
  @override
  final int balanceVnd;
  @override
  final int periodDays;
  @override
  final int periodInflowsVnd;
  @override
  final int periodOutflowsVnd;

  factory _$FundSummary([void Function(FundSummaryBuilder)? updates]) =>
      (FundSummaryBuilder()..update(updates))._build();

  _$FundSummary._(
      {required this.balanceVnd,
      required this.periodDays,
      required this.periodInflowsVnd,
      required this.periodOutflowsVnd})
      : super._();
  @override
  FundSummary rebuild(void Function(FundSummaryBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  FundSummaryBuilder toBuilder() => FundSummaryBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is FundSummary &&
        balanceVnd == other.balanceVnd &&
        periodDays == other.periodDays &&
        periodInflowsVnd == other.periodInflowsVnd &&
        periodOutflowsVnd == other.periodOutflowsVnd;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, balanceVnd.hashCode);
    _$hash = $jc(_$hash, periodDays.hashCode);
    _$hash = $jc(_$hash, periodInflowsVnd.hashCode);
    _$hash = $jc(_$hash, periodOutflowsVnd.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'FundSummary')
          ..add('balanceVnd', balanceVnd)
          ..add('periodDays', periodDays)
          ..add('periodInflowsVnd', periodInflowsVnd)
          ..add('periodOutflowsVnd', periodOutflowsVnd))
        .toString();
  }
}

class FundSummaryBuilder implements Builder<FundSummary, FundSummaryBuilder> {
  _$FundSummary? _$v;

  int? _balanceVnd;
  int? get balanceVnd => _$this._balanceVnd;
  set balanceVnd(int? balanceVnd) => _$this._balanceVnd = balanceVnd;

  int? _periodDays;
  int? get periodDays => _$this._periodDays;
  set periodDays(int? periodDays) => _$this._periodDays = periodDays;

  int? _periodInflowsVnd;
  int? get periodInflowsVnd => _$this._periodInflowsVnd;
  set periodInflowsVnd(int? periodInflowsVnd) =>
      _$this._periodInflowsVnd = periodInflowsVnd;

  int? _periodOutflowsVnd;
  int? get periodOutflowsVnd => _$this._periodOutflowsVnd;
  set periodOutflowsVnd(int? periodOutflowsVnd) =>
      _$this._periodOutflowsVnd = periodOutflowsVnd;

  FundSummaryBuilder() {
    FundSummary._defaults(this);
  }

  FundSummaryBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _balanceVnd = $v.balanceVnd;
      _periodDays = $v.periodDays;
      _periodInflowsVnd = $v.periodInflowsVnd;
      _periodOutflowsVnd = $v.periodOutflowsVnd;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(FundSummary other) {
    _$v = other as _$FundSummary;
  }

  @override
  void update(void Function(FundSummaryBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  FundSummary build() => _build();

  _$FundSummary _build() {
    final _$result = _$v ??
        _$FundSummary._(
          balanceVnd: BuiltValueNullFieldError.checkNotNull(
              balanceVnd, r'FundSummary', 'balanceVnd'),
          periodDays: BuiltValueNullFieldError.checkNotNull(
              periodDays, r'FundSummary', 'periodDays'),
          periodInflowsVnd: BuiltValueNullFieldError.checkNotNull(
              periodInflowsVnd, r'FundSummary', 'periodInflowsVnd'),
          periodOutflowsVnd: BuiltValueNullFieldError.checkNotNull(
              periodOutflowsVnd, r'FundSummary', 'periodOutflowsVnd'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
