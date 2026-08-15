// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'notification_feed.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$NotificationFeed extends NotificationFeed {
  @override
  final int id;
  @override
  final String eventCode;
  @override
  final String eventKey;
  @override
  final String subject;
  @override
  final String body;
  @override
  final DateTime createdAt;
  @override
  final DateTime? readAt;

  factory _$NotificationFeed(
          [void Function(NotificationFeedBuilder)? updates]) =>
      (NotificationFeedBuilder()..update(updates))._build();

  _$NotificationFeed._(
      {required this.id,
      required this.eventCode,
      required this.eventKey,
      required this.subject,
      required this.body,
      required this.createdAt,
      this.readAt})
      : super._();
  @override
  NotificationFeed rebuild(void Function(NotificationFeedBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  NotificationFeedBuilder toBuilder() =>
      NotificationFeedBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is NotificationFeed &&
        id == other.id &&
        eventCode == other.eventCode &&
        eventKey == other.eventKey &&
        subject == other.subject &&
        body == other.body &&
        createdAt == other.createdAt &&
        readAt == other.readAt;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, eventCode.hashCode);
    _$hash = $jc(_$hash, eventKey.hashCode);
    _$hash = $jc(_$hash, subject.hashCode);
    _$hash = $jc(_$hash, body.hashCode);
    _$hash = $jc(_$hash, createdAt.hashCode);
    _$hash = $jc(_$hash, readAt.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'NotificationFeed')
          ..add('id', id)
          ..add('eventCode', eventCode)
          ..add('eventKey', eventKey)
          ..add('subject', subject)
          ..add('body', body)
          ..add('createdAt', createdAt)
          ..add('readAt', readAt))
        .toString();
  }
}

class NotificationFeedBuilder
    implements Builder<NotificationFeed, NotificationFeedBuilder> {
  _$NotificationFeed? _$v;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  String? _eventCode;
  String? get eventCode => _$this._eventCode;
  set eventCode(String? eventCode) => _$this._eventCode = eventCode;

  String? _eventKey;
  String? get eventKey => _$this._eventKey;
  set eventKey(String? eventKey) => _$this._eventKey = eventKey;

  String? _subject;
  String? get subject => _$this._subject;
  set subject(String? subject) => _$this._subject = subject;

  String? _body;
  String? get body => _$this._body;
  set body(String? body) => _$this._body = body;

  DateTime? _createdAt;
  DateTime? get createdAt => _$this._createdAt;
  set createdAt(DateTime? createdAt) => _$this._createdAt = createdAt;

  DateTime? _readAt;
  DateTime? get readAt => _$this._readAt;
  set readAt(DateTime? readAt) => _$this._readAt = readAt;

  NotificationFeedBuilder() {
    NotificationFeed._defaults(this);
  }

  NotificationFeedBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _id = $v.id;
      _eventCode = $v.eventCode;
      _eventKey = $v.eventKey;
      _subject = $v.subject;
      _body = $v.body;
      _createdAt = $v.createdAt;
      _readAt = $v.readAt;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(NotificationFeed other) {
    _$v = other as _$NotificationFeed;
  }

  @override
  void update(void Function(NotificationFeedBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  NotificationFeed build() => _build();

  _$NotificationFeed _build() {
    final _$result = _$v ??
        _$NotificationFeed._(
          id: BuiltValueNullFieldError.checkNotNull(
              id, r'NotificationFeed', 'id'),
          eventCode: BuiltValueNullFieldError.checkNotNull(
              eventCode, r'NotificationFeed', 'eventCode'),
          eventKey: BuiltValueNullFieldError.checkNotNull(
              eventKey, r'NotificationFeed', 'eventKey'),
          subject: BuiltValueNullFieldError.checkNotNull(
              subject, r'NotificationFeed', 'subject'),
          body: BuiltValueNullFieldError.checkNotNull(
              body, r'NotificationFeed', 'body'),
          createdAt: BuiltValueNullFieldError.checkNotNull(
              createdAt, r'NotificationFeed', 'createdAt'),
          readAt: readAt,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
