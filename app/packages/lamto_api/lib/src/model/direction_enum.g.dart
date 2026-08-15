// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'direction_enum.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

const DirectionEnum _$ENTRY = const DirectionEnum._('ENTRY');
const DirectionEnum _$EXIT = const DirectionEnum._('EXIT');

DirectionEnum _$valueOf(String name) {
  switch (name) {
    case 'ENTRY':
      return _$ENTRY;
    case 'EXIT':
      return _$EXIT;
    default:
      throw ArgumentError(name);
  }
}

final BuiltSet<DirectionEnum> _$values =
    BuiltSet<DirectionEnum>(const <DirectionEnum>[
  _$ENTRY,
  _$EXIT,
]);

class _$DirectionEnumMeta {
  const _$DirectionEnumMeta();
  DirectionEnum get ENTRY => _$ENTRY;
  DirectionEnum get EXIT => _$EXIT;
  DirectionEnum valueOf(String name) => _$valueOf(name);
  BuiltSet<DirectionEnum> get values => _$values;
}

abstract class _$DirectionEnumMixin {
  // ignore: non_constant_identifier_names
  _$DirectionEnumMeta get DirectionEnum => const _$DirectionEnumMeta();
}

Serializer<DirectionEnum> _$directionEnumSerializer =
    _$DirectionEnumSerializer();

class _$DirectionEnumSerializer implements PrimitiveSerializer<DirectionEnum> {
  static const Map<String, Object> _toWire = const <String, Object>{
    'ENTRY': 'ENTRY',
    'EXIT': 'EXIT',
  };
  static const Map<Object, String> _fromWire = const <Object, String>{
    'ENTRY': 'ENTRY',
    'EXIT': 'EXIT',
  };

  @override
  final Iterable<Type> types = const <Type>[DirectionEnum];
  @override
  final String wireName = 'DirectionEnum';

  @override
  Object serialize(Serializers serializers, DirectionEnum object,
          {FullType specifiedType = FullType.unspecified}) =>
      _toWire[object.name] ?? object.name;

  @override
  DirectionEnum deserialize(Serializers serializers, Object serialized,
          {FullType specifiedType = FullType.unspecified}) =>
      DirectionEnum.valueOf(
          _fromWire[serialized] ?? (serialized is String ? serialized : ''));
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
