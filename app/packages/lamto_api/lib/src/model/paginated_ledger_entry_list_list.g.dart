// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'paginated_ledger_entry_list_list.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$PaginatedLedgerEntryListList extends PaginatedLedgerEntryListList {
  @override
  final String? next;
  @override
  final String? previous;
  @override
  final BuiltList<LedgerEntryList> results;

  factory _$PaginatedLedgerEntryListList(
          [void Function(PaginatedLedgerEntryListListBuilder)? updates]) =>
      (PaginatedLedgerEntryListListBuilder()..update(updates))._build();

  _$PaginatedLedgerEntryListList._(
      {this.next, this.previous, required this.results})
      : super._();
  @override
  PaginatedLedgerEntryListList rebuild(
          void Function(PaginatedLedgerEntryListListBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  PaginatedLedgerEntryListListBuilder toBuilder() =>
      PaginatedLedgerEntryListListBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is PaginatedLedgerEntryListList &&
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
    return (newBuiltValueToStringHelper(r'PaginatedLedgerEntryListList')
          ..add('next', next)
          ..add('previous', previous)
          ..add('results', results))
        .toString();
  }
}

class PaginatedLedgerEntryListListBuilder
    implements
        Builder<PaginatedLedgerEntryListList,
            PaginatedLedgerEntryListListBuilder> {
  _$PaginatedLedgerEntryListList? _$v;

  String? _next;
  String? get next => _$this._next;
  set next(String? next) => _$this._next = next;

  String? _previous;
  String? get previous => _$this._previous;
  set previous(String? previous) => _$this._previous = previous;

  ListBuilder<LedgerEntryList>? _results;
  ListBuilder<LedgerEntryList> get results =>
      _$this._results ??= ListBuilder<LedgerEntryList>();
  set results(ListBuilder<LedgerEntryList>? results) =>
      _$this._results = results;

  PaginatedLedgerEntryListListBuilder() {
    PaginatedLedgerEntryListList._defaults(this);
  }

  PaginatedLedgerEntryListListBuilder get _$this {
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
  void replace(PaginatedLedgerEntryListList other) {
    _$v = other as _$PaginatedLedgerEntryListList;
  }

  @override
  void update(void Function(PaginatedLedgerEntryListListBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  PaginatedLedgerEntryListList build() => _build();

  _$PaginatedLedgerEntryListList _build() {
    _$PaginatedLedgerEntryListList _$result;
    try {
      _$result = _$v ??
          _$PaginatedLedgerEntryListList._(
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
            r'PaginatedLedgerEntryListList', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
