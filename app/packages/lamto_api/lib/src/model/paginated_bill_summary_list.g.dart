// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'paginated_bill_summary_list.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$PaginatedBillSummaryList extends PaginatedBillSummaryList {
  @override
  final String? next;
  @override
  final String? previous;
  @override
  final BuiltList<BillSummary> results;

  factory _$PaginatedBillSummaryList(
          [void Function(PaginatedBillSummaryListBuilder)? updates]) =>
      (PaginatedBillSummaryListBuilder()..update(updates))._build();

  _$PaginatedBillSummaryList._(
      {this.next, this.previous, required this.results})
      : super._();
  @override
  PaginatedBillSummaryList rebuild(
          void Function(PaginatedBillSummaryListBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  PaginatedBillSummaryListBuilder toBuilder() =>
      PaginatedBillSummaryListBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is PaginatedBillSummaryList &&
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
    return (newBuiltValueToStringHelper(r'PaginatedBillSummaryList')
          ..add('next', next)
          ..add('previous', previous)
          ..add('results', results))
        .toString();
  }
}

class PaginatedBillSummaryListBuilder
    implements
        Builder<PaginatedBillSummaryList, PaginatedBillSummaryListBuilder> {
  _$PaginatedBillSummaryList? _$v;

  String? _next;
  String? get next => _$this._next;
  set next(String? next) => _$this._next = next;

  String? _previous;
  String? get previous => _$this._previous;
  set previous(String? previous) => _$this._previous = previous;

  ListBuilder<BillSummary>? _results;
  ListBuilder<BillSummary> get results =>
      _$this._results ??= ListBuilder<BillSummary>();
  set results(ListBuilder<BillSummary>? results) => _$this._results = results;

  PaginatedBillSummaryListBuilder() {
    PaginatedBillSummaryList._defaults(this);
  }

  PaginatedBillSummaryListBuilder get _$this {
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
  void replace(PaginatedBillSummaryList other) {
    _$v = other as _$PaginatedBillSummaryList;
  }

  @override
  void update(void Function(PaginatedBillSummaryListBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  PaginatedBillSummaryList build() => _build();

  _$PaginatedBillSummaryList _build() {
    _$PaginatedBillSummaryList _$result;
    try {
      _$result = _$v ??
          _$PaginatedBillSummaryList._(
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
            r'PaginatedBillSummaryList', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
