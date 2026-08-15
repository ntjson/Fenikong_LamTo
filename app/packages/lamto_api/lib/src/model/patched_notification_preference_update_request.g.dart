// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'patched_notification_preference_update_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$PatchedNotificationPreferenceUpdateRequest
    extends PatchedNotificationPreferenceUpdateRequest {
  @override
  final BuiltList<NotificationPreferenceUpdateItemRequest>? preferences;

  factory _$PatchedNotificationPreferenceUpdateRequest(
          [void Function(PatchedNotificationPreferenceUpdateRequestBuilder)?
              updates]) =>
      (PatchedNotificationPreferenceUpdateRequestBuilder()..update(updates))
          ._build();

  _$PatchedNotificationPreferenceUpdateRequest._({this.preferences})
      : super._();
  @override
  PatchedNotificationPreferenceUpdateRequest rebuild(
          void Function(PatchedNotificationPreferenceUpdateRequestBuilder)
              updates) =>
      (toBuilder()..update(updates)).build();

  @override
  PatchedNotificationPreferenceUpdateRequestBuilder toBuilder() =>
      PatchedNotificationPreferenceUpdateRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is PatchedNotificationPreferenceUpdateRequest &&
        preferences == other.preferences;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, preferences.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(
            r'PatchedNotificationPreferenceUpdateRequest')
          ..add('preferences', preferences))
        .toString();
  }
}

class PatchedNotificationPreferenceUpdateRequestBuilder
    implements
        Builder<PatchedNotificationPreferenceUpdateRequest,
            PatchedNotificationPreferenceUpdateRequestBuilder> {
  _$PatchedNotificationPreferenceUpdateRequest? _$v;

  ListBuilder<NotificationPreferenceUpdateItemRequest>? _preferences;
  ListBuilder<NotificationPreferenceUpdateItemRequest> get preferences =>
      _$this._preferences ??=
          ListBuilder<NotificationPreferenceUpdateItemRequest>();
  set preferences(
          ListBuilder<NotificationPreferenceUpdateItemRequest>? preferences) =>
      _$this._preferences = preferences;

  PatchedNotificationPreferenceUpdateRequestBuilder() {
    PatchedNotificationPreferenceUpdateRequest._defaults(this);
  }

  PatchedNotificationPreferenceUpdateRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _preferences = $v.preferences?.toBuilder();
      _$v = null;
    }
    return this;
  }

  @override
  void replace(PatchedNotificationPreferenceUpdateRequest other) {
    _$v = other as _$PatchedNotificationPreferenceUpdateRequest;
  }

  @override
  void update(
      void Function(PatchedNotificationPreferenceUpdateRequestBuilder)?
          updates) {
    if (updates != null) updates(this);
  }

  @override
  PatchedNotificationPreferenceUpdateRequest build() => _build();

  _$PatchedNotificationPreferenceUpdateRequest _build() {
    _$PatchedNotificationPreferenceUpdateRequest _$result;
    try {
      _$result = _$v ??
          _$PatchedNotificationPreferenceUpdateRequest._(
            preferences: _preferences?.build(),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'preferences';
        _preferences?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'PatchedNotificationPreferenceUpdateRequest',
            _$failedField,
            e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
