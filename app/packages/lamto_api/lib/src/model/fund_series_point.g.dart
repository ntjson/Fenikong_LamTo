// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'fund_series_point.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$FundSeriesPoint extends FundSeriesPoint {
  @override
  final DateTime periodStart;
  @override
  final int inflowsVnd;
  @override
  final int outflowsVnd;
  @override
  final int balanceVnd;

  factory _$FundSeriesPoint([void Function(FundSeriesPointBuilder)? updates]) =>
      (FundSeriesPointBuilder()..update(updates))._build();

  _$FundSeriesPoint._(
      {required this.periodStart,
      required this.inflowsVnd,
      required this.outflowsVnd,
      required this.balanceVnd})
      : super._();
  @override
  FundSeriesPoint rebuild(void Function(FundSeriesPointBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  FundSeriesPointBuilder toBuilder() => FundSeriesPointBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is FundSeriesPoint &&
        periodStart == other.periodStart &&
        inflowsVnd == other.inflowsVnd &&
        outflowsVnd == other.outflowsVnd &&
        balanceVnd == other.balanceVnd;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, periodStart.hashCode);
    _$hash = $jc(_$hash, inflowsVnd.hashCode);
    _$hash = $jc(_$hash, outflowsVnd.hashCode);
    _$hash = $jc(_$hash, balanceVnd.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'FundSeriesPoint')
          ..add('periodStart', periodStart)
          ..add('inflowsVnd', inflowsVnd)
          ..add('outflowsVnd', outflowsVnd)
          ..add('balanceVnd', balanceVnd))
        .toString();
  }
}

class FundSeriesPointBuilder
    implements Builder<FundSeriesPoint, FundSeriesPointBuilder> {
  _$FundSeriesPoint? _$v;

  DateTime? _periodStart;
  DateTime? get periodStart => _$this._periodStart;
  set periodStart(DateTime? periodStart) => _$this._periodStart = periodStart;

  int? _inflowsVnd;
  int? get inflowsVnd => _$this._inflowsVnd;
  set inflowsVnd(int? inflowsVnd) => _$this._inflowsVnd = inflowsVnd;

  int? _outflowsVnd;
  int? get outflowsVnd => _$this._outflowsVnd;
  set outflowsVnd(int? outflowsVnd) => _$this._outflowsVnd = outflowsVnd;

  int? _balanceVnd;
  int? get balanceVnd => _$this._balanceVnd;
  set balanceVnd(int? balanceVnd) => _$this._balanceVnd = balanceVnd;

  FundSeriesPointBuilder() {
    FundSeriesPoint._defaults(this);
  }

  FundSeriesPointBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _periodStart = $v.periodStart;
      _inflowsVnd = $v.inflowsVnd;
      _outflowsVnd = $v.outflowsVnd;
      _balanceVnd = $v.balanceVnd;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(FundSeriesPoint other) {
    _$v = other as _$FundSeriesPoint;
  }

  @override
  void update(void Function(FundSeriesPointBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  FundSeriesPoint build() => _build();

  _$FundSeriesPoint _build() {
    final _$result = _$v ??
        _$FundSeriesPoint._(
          periodStart: BuiltValueNullFieldError.checkNotNull(
              periodStart, r'FundSeriesPoint', 'periodStart'),
          inflowsVnd: BuiltValueNullFieldError.checkNotNull(
              inflowsVnd, r'FundSeriesPoint', 'inflowsVnd'),
          outflowsVnd: BuiltValueNullFieldError.checkNotNull(
              outflowsVnd, r'FundSeriesPoint', 'outflowsVnd'),
          balanceVnd: BuiltValueNullFieldError.checkNotNull(
              balanceVnd, r'FundSeriesPoint', 'balanceVnd'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
