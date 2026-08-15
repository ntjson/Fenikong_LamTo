// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'notification_preference.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$NotificationPreference extends NotificationPreference {
  @override
  final String eventCode;
  @override
  final bool emailEnabled;
  @override
  final bool pushEnabled;

  factory _$NotificationPreference(
          [void Function(NotificationPreferenceBuilder)? updates]) =>
      (NotificationPreferenceBuilder()..update(updates))._build();

  _$NotificationPreference._(
      {required this.eventCode,
      required this.emailEnabled,
      required this.pushEnabled})
      : super._();
  @override
  NotificationPreference rebuild(
          void Function(NotificationPreferenceBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  NotificationPreferenceBuilder toBuilder() =>
      NotificationPreferenceBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is NotificationPreference &&
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
    return (newBuiltValueToStringHelper(r'NotificationPreference')
          ..add('eventCode', eventCode)
          ..add('emailEnabled', emailEnabled)
          ..add('pushEnabled', pushEnabled))
        .toString();
  }
}

class NotificationPreferenceBuilder
    implements Builder<NotificationPreference, NotificationPreferenceBuilder> {
  _$NotificationPreference? _$v;

  String? _eventCode;
  String? get eventCode => _$this._eventCode;
  set eventCode(String? eventCode) => _$this._eventCode = eventCode;

  bool? _emailEnabled;
  bool? get emailEnabled => _$this._emailEnabled;
  set emailEnabled(bool? emailEnabled) => _$this._emailEnabled = emailEnabled;

  bool? _pushEnabled;
  bool? get pushEnabled => _$this._pushEnabled;
  set pushEnabled(bool? pushEnabled) => _$this._pushEnabled = pushEnabled;

  NotificationPreferenceBuilder() {
    NotificationPreference._defaults(this);
  }

  NotificationPreferenceBuilder get _$this {
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
  void replace(NotificationPreference other) {
    _$v = other as _$NotificationPreference;
  }

  @override
  void update(void Function(NotificationPreferenceBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  NotificationPreference build() => _build();

  _$NotificationPreference _build() {
    final _$result = _$v ??
        _$NotificationPreference._(
          eventCode: BuiltValueNullFieldError.checkNotNull(
              eventCode, r'NotificationPreference', 'eventCode'),
          emailEnabled: BuiltValueNullFieldError.checkNotNull(
              emailEnabled, r'NotificationPreference', 'emailEnabled'),
          pushEnabled: BuiltValueNullFieldError.checkNotNull(
              pushEnabled, r'NotificationPreference', 'pushEnabled'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
