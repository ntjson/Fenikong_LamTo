// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'kind_enum.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

const KindEnum _$BEFORE = const KindEnum._('BEFORE');
const KindEnum _$AFTER = const KindEnum._('AFTER');

KindEnum _$valueOf(String name) {
  switch (name) {
    case 'BEFORE':
      return _$BEFORE;
    case 'AFTER':
      return _$AFTER;
    default:
      throw ArgumentError(name);
  }
}

final BuiltSet<KindEnum> _$values = BuiltSet<KindEnum>(const <KindEnum>[
  _$BEFORE,
  _$AFTER,
]);

class _$KindEnumMeta {
  const _$KindEnumMeta();
  KindEnum get BEFORE => _$BEFORE;
  KindEnum get AFTER => _$AFTER;
  KindEnum valueOf(String name) => _$valueOf(name);
  BuiltSet<KindEnum> get values => _$values;
}

abstract class _$KindEnumMixin {
  // ignore: non_constant_identifier_names
  _$KindEnumMeta get KindEnum => const _$KindEnumMeta();
}

Serializer<KindEnum> _$kindEnumSerializer = _$KindEnumSerializer();

class _$KindEnumSerializer implements PrimitiveSerializer<KindEnum> {
  static const Map<String, Object> _toWire = const <String, Object>{
    'BEFORE': 'BEFORE',
    'AFTER': 'AFTER',
  };
  static const Map<Object, String> _fromWire = const <Object, String>{
    'BEFORE': 'BEFORE',
    'AFTER': 'AFTER',
  };

  @override
  final Iterable<Type> types = const <Type>[KindEnum];
  @override
  final String wireName = 'KindEnum';

  @override
  Object serialize(Serializers serializers, KindEnum object,
          {FullType specifiedType = FullType.unspecified}) =>
      _toWire[object.name] ?? object.name;

  @override
  KindEnum deserialize(Serializers serializers, Object serialized,
          {FullType specifiedType = FullType.unspecified}) =>
      KindEnum.valueOf(
          _fromWire[serialized] ?? (serialized is String ? serialized : ''));
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
