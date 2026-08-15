// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'me.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$Me extends Me {
  @override
  final String displayName;
  @override
  final String? email;
  @override
  final String? phone;
  @override
  final BuiltList<Occupancy> occupancies;
  @override
  final BuiltList<NotificationPreference> notificationPreferences;

  factory _$Me([void Function(MeBuilder)? updates]) =>
      (MeBuilder()..update(updates))._build();

  _$Me._(
      {required this.displayName,
      this.email,
      this.phone,
      required this.occupancies,
      required this.notificationPreferences})
      : super._();
  @override
  Me rebuild(void Function(MeBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  MeBuilder toBuilder() => MeBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is Me &&
        displayName == other.displayName &&
        email == other.email &&
        phone == other.phone &&
        occupancies == other.occupancies &&
        notificationPreferences == other.notificationPreferences;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, displayName.hashCode);
    _$hash = $jc(_$hash, email.hashCode);
    _$hash = $jc(_$hash, phone.hashCode);
    _$hash = $jc(_$hash, occupancies.hashCode);
    _$hash = $jc(_$hash, notificationPreferences.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'Me')
          ..add('displayName', displayName)
          ..add('email', email)
          ..add('phone', phone)
          ..add('occupancies', occupancies)
          ..add('notificationPreferences', notificationPreferences))
        .toString();
  }
}

class MeBuilder implements Builder<Me, MeBuilder> {
  _$Me? _$v;

  String? _displayName;
  String? get displayName => _$this._displayName;
  set displayName(String? displayName) => _$this._displayName = displayName;

  String? _email;
  String? get email => _$this._email;
  set email(String? email) => _$this._email = email;

  String? _phone;
  String? get phone => _$this._phone;
  set phone(String? phone) => _$this._phone = phone;

  ListBuilder<Occupancy>? _occupancies;
  ListBuilder<Occupancy> get occupancies =>
      _$this._occupancies ??= ListBuilder<Occupancy>();
  set occupancies(ListBuilder<Occupancy>? occupancies) =>
      _$this._occupancies = occupancies;

  ListBuilder<NotificationPreference>? _notificationPreferences;
  ListBuilder<NotificationPreference> get notificationPreferences =>
      _$this._notificationPreferences ??= ListBuilder<NotificationPreference>();
  set notificationPreferences(
          ListBuilder<NotificationPreference>? notificationPreferences) =>
      _$this._notificationPreferences = notificationPreferences;

  MeBuilder() {
    Me._defaults(this);
  }

  MeBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _displayName = $v.displayName;
      _email = $v.email;
      _phone = $v.phone;
      _occupancies = $v.occupancies.toBuilder();
      _notificationPreferences = $v.notificationPreferences.toBuilder();
      _$v = null;
    }
    return this;
  }

  @override
  void replace(Me other) {
    _$v = other as _$Me;
  }

  @override
  void update(void Function(MeBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  Me build() => _build();

  _$Me _build() {
    _$Me _$result;
    try {
      _$result = _$v ??
          _$Me._(
            displayName: BuiltValueNullFieldError.checkNotNull(
                displayName, r'Me', 'displayName'),
            email: email,
            phone: phone,
            occupancies: occupancies.build(),
            notificationPreferences: notificationPreferences.build(),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'occupancies';
        occupancies.build();
        _$failedField = 'notificationPreferences';
        notificationPreferences.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(r'Me', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
