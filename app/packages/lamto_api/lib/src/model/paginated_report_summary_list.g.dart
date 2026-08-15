// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'paginated_report_summary_list.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$PaginatedReportSummaryList extends PaginatedReportSummaryList {
  @override
  final String? next;
  @override
  final String? previous;
  @override
  final BuiltList<ReportSummary> results;

  factory _$PaginatedReportSummaryList(
          [void Function(PaginatedReportSummaryListBuilder)? updates]) =>
      (PaginatedReportSummaryListBuilder()..update(updates))._build();

  _$PaginatedReportSummaryList._(
      {this.next, this.previous, required this.results})
      : super._();
  @override
  PaginatedReportSummaryList rebuild(
          void Function(PaginatedReportSummaryListBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  PaginatedReportSummaryListBuilder toBuilder() =>
      PaginatedReportSummaryListBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is PaginatedReportSummaryList &&
        next == other.next &&
        previous == other.previous &&
        results == other.results;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, next.hashCode);
    _$hash = $jc(_$hash, previous.hashCode);
    _$hash = $jc(_$hash, results.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'PaginatedReportSummaryList')
          ..add('next', next)
          ..add('previous', previous)
          ..add('results', results))
        .toString();
  }
}

class PaginatedReportSummaryListBuilder
    implements
        Builder<PaginatedReportSummaryList, PaginatedReportSummaryListBuilder> {
  _$PaginatedReportSummaryList? _$v;

  String? _next;
  String? get next => _$this._next;
  set next(String? next) => _$this._next = next;

  String? _previous;
  String? get previous => _$this._previous;
  set previous(String? previous) => _$this._previous = previous;

  ListBuilder<ReportSummary>? _results;
  ListBuilder<ReportSummary> get results =>
      _$this._results ??= ListBuilder<ReportSummary>();
  set results(ListBuilder<ReportSummary>? results) => _$this._results = results;

  PaginatedReportSummaryListBuilder() {
    PaginatedReportSummaryList._defaults(this);
  }

  PaginatedReportSummaryListBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _next = $v.next;
      _previous = $v.previous;
      _results = $v.results.toBuilder();
      _$v = null;
    }
    return this;
  }

  @override
  void replace(PaginatedReportSummaryList other) {
    _$v = other as _$PaginatedReportSummaryList;
  }

  @override
  void update(void Function(PaginatedReportSummaryListBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  PaginatedReportSummaryList build() => _build();

  _$PaginatedReportSummaryList _build() {
    _$PaginatedReportSummaryList _$result;
    try {
      _$result = _$v ??
          _$PaginatedReportSummaryList._(
            next: next,
            previous: previous,
            results: results.build(),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'results';
        results.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'PaginatedReportSummaryList', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
