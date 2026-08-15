// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'paginated_notification_feed_list.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$PaginatedNotificationFeedList extends PaginatedNotificationFeedList {
  @override
  final String? next;
  @override
  final String? previous;
  @override
  final BuiltList<NotificationFeed> results;

  factory _$PaginatedNotificationFeedList(
          [void Function(PaginatedNotificationFeedListBuilder)? updates]) =>
      (PaginatedNotificationFeedListBuilder()..update(updates))._build();

  _$PaginatedNotificationFeedList._(
      {this.next, this.previous, required this.results})
      : super._();
  @override
  PaginatedNotificationFeedList rebuild(
          void Function(PaginatedNotificationFeedListBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  PaginatedNotificationFeedListBuilder toBuilder() =>
      PaginatedNotificationFeedListBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is PaginatedNotificationFeedList &&
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
    return (newBuiltValueToStringHelper(r'PaginatedNotificationFeedList')
          ..add('next', next)
          ..add('previous', previous)
          ..add('results', results))
        .toString();
  }
}

class PaginatedNotificationFeedListBuilder
    implements
        Builder<PaginatedNotificationFeedList,
            PaginatedNotificationFeedListBuilder> {
  _$PaginatedNotificationFeedList? _$v;

  String? _next;
  String? get next => _$this._next;
  set next(String? next) => _$this._next = next;

  String? _previous;
  String? get previous => _$this._previous;
  set previous(String? previous) => _$this._previous = previous;

  ListBuilder<NotificationFeed>? _results;
  ListBuilder<NotificationFeed> get results =>
      _$this._results ??= ListBuilder<NotificationFeed>();
  set results(ListBuilder<NotificationFeed>? results) =>
      _$this._results = results;

  PaginatedNotificationFeedListBuilder() {
    PaginatedNotificationFeedList._defaults(this);
  }

  PaginatedNotificationFeedListBuilder get _$this {
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
  void replace(PaginatedNotificationFeedList other) {
    _$v = other as _$PaginatedNotificationFeedList;
  }

  @override
  void update(void Function(PaginatedNotificationFeedListBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  PaginatedNotificationFeedList build() => _build();

  _$PaginatedNotificationFeedList _build() {
    _$PaginatedNotificationFeedList _$result;
    try {
      _$result = _$v ??
          _$PaginatedNotificationFeedList._(
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
            r'PaginatedNotificationFeedList', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
