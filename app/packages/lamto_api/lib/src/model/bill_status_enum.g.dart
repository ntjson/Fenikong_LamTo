// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'bill_status_enum.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

const BillStatusEnum _$ISSUED = const BillStatusEnum._('ISSUED');
const BillStatusEnum _$PAID = const BillStatusEnum._('PAID');
const BillStatusEnum _$VOID = const BillStatusEnum._('VOID');

BillStatusEnum _$valueOf(String name) {
  switch (name) {
    case 'ISSUED':
      return _$ISSUED;
    case 'PAID':
      return _$PAID;
    case 'VOID':
      return _$VOID;
    default:
      throw ArgumentError(name);
  }
}

final BuiltSet<BillStatusEnum> _$values =
    BuiltSet<BillStatusEnum>(const <BillStatusEnum>[
  _$ISSUED,
  _$PAID,
  _$VOID,
]);

class _$BillStatusEnumMeta {
  const _$BillStatusEnumMeta();
  BillStatusEnum get ISSUED => _$ISSUED;
  BillStatusEnum get PAID => _$PAID;
  BillStatusEnum get VOID => _$VOID;
  BillStatusEnum valueOf(String name) => _$valueOf(name);
  BuiltSet<BillStatusEnum> get values => _$values;
}

abstract class _$BillStatusEnumMixin {
  // ignore: non_constant_identifier_names
  _$BillStatusEnumMeta get BillStatusEnum => const _$BillStatusEnumMeta();
}

Serializer<BillStatusEnum> _$billStatusEnumSerializer =
    _$BillStatusEnumSerializer();

class _$BillStatusEnumSerializer
    implements PrimitiveSerializer<BillStatusEnum> {
  static const Map<String, Object> _toWire = const <String, Object>{
    'ISSUED': 'ISSUED',
    'PAID': 'PAID',
    'VOID': 'VOID',
  };
  static const Map<Object, String> _fromWire = const <Object, String>{
    'ISSUED': 'ISSUED',
    'PAID': 'PAID',
    'VOID': 'VOID',
  };

  @override
  final Iterable<Type> types = const <Type>[BillStatusEnum];
  @override
  final String wireName = 'BillStatusEnum';

  @override
  Object serialize(Serializers serializers, BillStatusEnum object,
          {FullType specifiedType = FullType.unspecified}) =>
      _toWire[object.name] ?? object.name;

  @override
  BillStatusEnum deserialize(Serializers serializers, Object serialized,
          {FullType specifiedType = FullType.unspecified}) =>
      BillStatusEnum.valueOf(
          _fromWire[serialized] ?? (serialized is String ? serialized : ''));
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
