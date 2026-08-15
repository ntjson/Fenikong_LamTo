// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'platform_enum.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

const PlatformEnum _$IOS = const PlatformEnum._('IOS');
const PlatformEnum _$ANDROID = const PlatformEnum._('ANDROID');

PlatformEnum _$valueOf(String name) {
  switch (name) {
    case 'IOS':
      return _$IOS;
    case 'ANDROID':
      return _$ANDROID;
    default:
      throw ArgumentError(name);
  }
}

final BuiltSet<PlatformEnum> _$values =
    BuiltSet<PlatformEnum>(const <PlatformEnum>[
  _$IOS,
  _$ANDROID,
]);

class _$PlatformEnumMeta {
  const _$PlatformEnumMeta();
  PlatformEnum get IOS => _$IOS;
  PlatformEnum get ANDROID => _$ANDROID;
  PlatformEnum valueOf(String name) => _$valueOf(name);
  BuiltSet<PlatformEnum> get values => _$values;
}

abstract class _$PlatformEnumMixin {
  // ignore: non_constant_identifier_names
  _$PlatformEnumMeta get PlatformEnum => const _$PlatformEnumMeta();
}

Serializer<PlatformEnum> _$platformEnumSerializer = _$PlatformEnumSerializer();

class _$PlatformEnumSerializer implements PrimitiveSerializer<PlatformEnum> {
  static const Map<String, Object> _toWire = const <String, Object>{
    'IOS': 'IOS',
    'ANDROID': 'ANDROID',
  };
  static const Map<Object, String> _fromWire = const <Object, String>{
    'IOS': 'IOS',
    'ANDROID': 'ANDROID',
  };

  @override
  final Iterable<Type> types = const <Type>[PlatformEnum];
  @override
  final String wireName = 'PlatformEnum';

  @override
  Object serialize(Serializers serializers, PlatformEnum object,
          {FullType specifiedType = FullType.unspecified}) =>
      _toWire[object.name] ?? object.name;

  @override
  PlatformEnum deserialize(Serializers serializers, Object serialized,
          {FullType specifiedType = FullType.unspecified}) =>
      PlatformEnum.valueOf(
          _fromWire[serialized] ?? (serialized is String ? serialized : ''));
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
