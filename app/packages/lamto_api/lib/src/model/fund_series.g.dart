// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'fund_series.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$FundSeries extends FundSeries {
  @override
  final String range;
  @override
  final BuiltList<FundSeriesPoint> points;

  factory _$FundSeries([void Function(FundSeriesBuilder)? updates]) =>
      (FundSeriesBuilder()..update(updates))._build();

  _$FundSeries._({required this.range, required this.points}) : super._();
  @override
  FundSeries rebuild(void Function(FundSeriesBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  FundSeriesBuilder toBuilder() => FundSeriesBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is FundSeries &&
        range == other.range &&
        points == other.points;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, range.hashCode);
    _$hash = $jc(_$hash, points.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'FundSeries')
          ..add('range', range)
          ..add('points', points))
        .toString();
  }
}

class FundSeriesBuilder implements Builder<FundSeries, FundSeriesBuilder> {
  _$FundSeries? _$v;

  String? _range;
  String? get range => _$this._range;
  set range(String? range) => _$this._range = range;

  ListBuilder<FundSeriesPoint>? _points;
  ListBuilder<FundSeriesPoint> get points =>
      _$this._points ??= ListBuilder<FundSeriesPoint>();
  set points(ListBuilder<FundSeriesPoint>? points) => _$this._points = points;

  FundSeriesBuilder() {
    FundSeries._defaults(this);
  }

  FundSeriesBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _range = $v.range;
      _points = $v.points.toBuilder();
      _$v = null;
    }
    return this;
  }

  @override
  void replace(FundSeries other) {
    _$v = other as _$FundSeries;
  }

  @override
  void update(void Function(FundSeriesBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  FundSeries build() => _build();

  _$FundSeries _build() {
    _$FundSeries _$result;
    try {
      _$result = _$v ??
          _$FundSeries._(
            range: BuiltValueNullFieldError.checkNotNull(
                range, r'FundSeries', 'range'),
            points: points.build(),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'points';
        points.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'FundSeries', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
