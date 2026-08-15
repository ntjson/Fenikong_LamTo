// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'notification_preference_update_item_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$NotificationPreferenceUpdateItemRequest
    extends NotificationPreferenceUpdateItemRequest {
  @override
  final String eventCode;
  @override
  final bool? emailEnabled;
  @override
  final bool? pushEnabled;

  factory _$NotificationPreferenceUpdateItemRequest(
          [void Function(NotificationPreferenceUpdateItemRequestBuilder)?
              updates]) =>
      (NotificationPreferenceUpdateItemRequestBuilder()..update(updates))
          ._build();

  _$NotificationPreferenceUpdateItemRequest._(
      {required this.eventCode, this.emailEnabled, this.pushEnabled})
      : super._();
  @override
  NotificationPreferenceUpdateItemRequest rebuild(
          void Function(NotificationPreferenceUpdateItemRequestBuilder)
              updates) =>
      (toBuilder()..update(updates)).build();

  @override
  NotificationPreferenceUpdateItemRequestBuilder toBuilder() =>
      NotificationPreferenceUpdateItemRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is NotificationPreferenceUpdateItemRequest &&
        eventCode == other.eventCode &&
        emailEnabled == other.emailEnabled &&
        pushEnabled == other.pushEnabled;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, eventCode.hashCode);
    _$hash = $jc(_$hash, emailEnabled.hashCode);
    _$hash = $jc(_$hash, pushEnabled.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(
            r'NotificationPreferenceUpdateItemRequest')
          ..add('eventCode', eventCode)
          ..add('emailEnabled', emailEnabled)
          ..add('pushEnabled', pushEnabled))
        .toString();
  }
}

class NotificationPreferenceUpdateItemRequestBuilder
    implements
        Builder<NotificationPreferenceUpdateItemRequest,
            NotificationPreferenceUpdateItemRequestBuilder> {
  _$NotificationPreferenceUpdateItemRequest? _$v;

  String? _eventCode;
  String? get eventCode => _$this._eventCode;
  set eventCode(String? eventCode) => _$this._eventCode = eventCode;

  bool? _emailEnabled;
  bool? get emailEnabled => _$this._emailEnabled;
  set emailEnabled(bool? emailEnabled) => _$this._emailEnabled = emailEnabled;

  bool? _pushEnabled;
  bool? get pushEnabled => _$this._pushEnabled;
  set pushEnabled(bool? pushEnabled) => _$this._pushEnabled = pushEnabled;

  NotificationPreferenceUpdateItemRequestBuilder() {
    NotificationPreferenceUpdateItemRequest._defaults(this);
  }

  NotificationPreferenceUpdateItemRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _eventCode = $v.eventCode;
      _emailEnabled = $v.emailEnabled;
      _pushEnabled = $v.pushEnabled;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(NotificationPreferenceUpdateItemRequest other) {
    _$v = other as _$NotificationPreferenceUpdateItemRequest;
  }

  @override
  void update(
      void Function(NotificationPreferenceUpdateItemRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  NotificationPreferenceUpdateItemRequest build() => _build();

  _$NotificationPreferenceUpdateItemRequest _build() {
    final _$result = _$v ??
        _$NotificationPreferenceUpdateItemRequest._(
          eventCode: BuiltValueNullFieldError.checkNotNull(eventCode,
              r'NotificationPreferenceUpdateItemRequest', 'eventCode'),
          emailEnabled: emailEnabled,
          pushEnabled: pushEnabled,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
