// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'registration_status_enum.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

const RegistrationStatusEnum _$PENDING =
    const RegistrationStatusEnum._('PENDING');
const RegistrationStatusEnum _$APPROVED =
    const RegistrationStatusEnum._('APPROVED');
const RegistrationStatusEnum _$REJECTED =
    const RegistrationStatusEnum._('REJECTED');
const RegistrationStatusEnum _$EXPIRED =
    const RegistrationStatusEnum._('EXPIRED');

RegistrationStatusEnum _$valueOf(String name) {
  switch (name) {
    case 'PENDING':
      return _$PENDING;
    case 'APPROVED':
      return _$APPROVED;
    case 'REJECTED':
      return _$REJECTED;
    case 'EXPIRED':
      return _$EXPIRED;
    default:
      throw ArgumentError(name);
  }
}

final BuiltSet<RegistrationStatusEnum> _$values =
    BuiltSet<RegistrationStatusEnum>(const <RegistrationStatusEnum>[
  _$PENDING,
  _$APPROVED,
  _$REJECTED,
  _$EXPIRED,
]);

class _$RegistrationStatusEnumMeta {
  const _$RegistrationStatusEnumMeta();
  RegistrationStatusEnum get PENDING => _$PENDING;
  RegistrationStatusEnum get APPROVED => _$APPROVED;
  RegistrationStatusEnum get REJECTED => _$REJECTED;
  RegistrationStatusEnum get EXPIRED => _$EXPIRED;
  RegistrationStatusEnum valueOf(String name) => _$valueOf(name);
  BuiltSet<RegistrationStatusEnum> get values => _$values;
}

abstract class _$RegistrationStatusEnumMixin {
  // ignore: non_constant_identifier_names
  _$RegistrationStatusEnumMeta get RegistrationStatusEnum =>
      const _$RegistrationStatusEnumMeta();
}

Serializer<RegistrationStatusEnum> _$registrationStatusEnumSerializer =
    _$RegistrationStatusEnumSerializer();

class _$RegistrationStatusEnumSerializer
    implements PrimitiveSerializer<RegistrationStatusEnum> {
  static const Map<String, Object> _toWire = const <String, Object>{
    'PENDING': 'PENDING',
    'APPROVED': 'APPROVED',
    'REJECTED': 'REJECTED',
    'EXPIRED': 'EXPIRED',
  };
  static const Map<Object, String> _fromWire = const <Object, String>{
    'PENDING': 'PENDING',
    'APPROVED': 'APPROVED',
    'REJECTED': 'REJECTED',
    'EXPIRED': 'EXPIRED',
  };

  @override
  final Iterable<Type> types = const <Type>[RegistrationStatusEnum];
  @override
  final String wireName = 'RegistrationStatusEnum';

  @override
  Object serialize(Serializers serializers, RegistrationStatusEnum object,
          {FullType specifiedType = FullType.unspecified}) =>
      _toWire[object.name] ?? object.name;

  @override
  RegistrationStatusEnum deserialize(Serializers serializers, Object serialized,
          {FullType specifiedType = FullType.unspecified}) =>
      RegistrationStatusEnum.valueOf(
          _fromWire[serialized] ?? (serialized is String ? serialized : ''));
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
