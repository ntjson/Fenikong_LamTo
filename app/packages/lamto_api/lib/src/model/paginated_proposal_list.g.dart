// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'paginated_proposal_list.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$PaginatedProposalList extends PaginatedProposalList {
  @override
  final String? next;
  @override
  final String? previous;
  @override
  final BuiltList<Proposal> results;

  factory _$PaginatedProposalList(
          [void Function(PaginatedProposalListBuilder)? updates]) =>
      (PaginatedProposalListBuilder()..update(updates))._build();

  _$PaginatedProposalList._({this.next, this.previous, required this.results})
      : super._();
  @override
  PaginatedProposalList rebuild(
          void Function(PaginatedProposalListBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  PaginatedProposalListBuilder toBuilder() =>
      PaginatedProposalListBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is PaginatedProposalList &&
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
    return (newBuiltValueToStringHelper(r'PaginatedProposalList')
          ..add('next', next)
          ..add('previous', previous)
          ..add('results', results))
        .toString();
  }
}

class PaginatedProposalListBuilder
    implements Builder<PaginatedProposalList, PaginatedProposalListBuilder> {
  _$PaginatedProposalList? _$v;

  String? _next;
  String? get next => _$this._next;
  set next(String? next) => _$this._next = next;

  String? _previous;
  String? get previous => _$this._previous;
  set previous(String? previous) => _$this._previous = previous;

  ListBuilder<Proposal>? _results;
  ListBuilder<Proposal> get results =>
      _$this._results ??= ListBuilder<Proposal>();
  set results(ListBuilder<Proposal>? results) => _$this._results = results;

  PaginatedProposalListBuilder() {
    PaginatedProposalList._defaults(this);
  }

  PaginatedProposalListBuilder get _$this {
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
  void replace(PaginatedProposalList other) {
    _$v = other as _$PaginatedProposalList;
  }

  @override
  void update(void Function(PaginatedProposalListBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  PaginatedProposalList build() => _build();

  _$PaginatedProposalList _build() {
    _$PaginatedProposalList _$result;
    try {
      _$result = _$v ??
          _$PaginatedProposalList._(
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
            r'PaginatedProposalList', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
