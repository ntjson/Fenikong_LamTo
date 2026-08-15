// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'status_enum.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

const StatusEnum _$SUBMITTED = const StatusEnum._('SUBMITTED');
const StatusEnum _$IN_REVIEW = const StatusEnum._('IN_REVIEW');
const StatusEnum _$NEEDS_INFO = const StatusEnum._('NEEDS_INFO');
const StatusEnum _$DECLINED = const StatusEnum._('DECLINED');
const StatusEnum _$IN_PROGRESS = const StatusEnum._('IN_PROGRESS');
const StatusEnum _$PROPOSED = const StatusEnum._('PROPOSED');
const StatusEnum _$COMPLETED = const StatusEnum._('COMPLETED');
const StatusEnum _$CLOSED = const StatusEnum._('CLOSED');

StatusEnum _$valueOf(String name) {
  switch (name) {
    case 'SUBMITTED':
      return _$SUBMITTED;
    case 'IN_REVIEW':
      return _$IN_REVIEW;
    case 'NEEDS_INFO':
      return _$NEEDS_INFO;
    case 'DECLINED':
      return _$DECLINED;
    case 'IN_PROGRESS':
      return _$IN_PROGRESS;
    case 'PROPOSED':
      return _$PROPOSED;
    case 'COMPLETED':
      return _$COMPLETED;
    case 'CLOSED':
      return _$CLOSED;
    default:
      throw ArgumentError(name);
  }
}

final BuiltSet<StatusEnum> _$values = BuiltSet<StatusEnum>(const <StatusEnum>[
  _$SUBMITTED,
  _$IN_REVIEW,
  _$NEEDS_INFO,
  _$DECLINED,
  _$IN_PROGRESS,
  _$PROPOSED,
  _$COMPLETED,
  _$CLOSED,
]);

class _$StatusEnumMeta {
  const _$StatusEnumMeta();
  StatusEnum get SUBMITTED => _$SUBMITTED;
  StatusEnum get IN_REVIEW => _$IN_REVIEW;
  StatusEnum get NEEDS_INFO => _$NEEDS_INFO;
  StatusEnum get DECLINED => _$DECLINED;
  StatusEnum get IN_PROGRESS => _$IN_PROGRESS;
  StatusEnum get PROPOSED => _$PROPOSED;
  StatusEnum get COMPLETED => _$COMPLETED;
  StatusEnum get CLOSED => _$CLOSED;
  StatusEnum valueOf(String name) => _$valueOf(name);
  BuiltSet<StatusEnum> get values => _$values;
}

abstract class _$StatusEnumMixin {
  // ignore: non_constant_identifier_names
  _$StatusEnumMeta get StatusEnum => const _$StatusEnumMeta();
}

Serializer<StatusEnum> _$statusEnumSerializer = _$StatusEnumSerializer();

class _$StatusEnumSerializer implements PrimitiveSerializer<StatusEnum> {
  static const Map<String, Object> _toWire = const <String, Object>{
    'SUBMITTED': 'SUBMITTED',
    'IN_REVIEW': 'IN_REVIEW',
    'NEEDS_INFO': 'NEEDS_INFO',
    'DECLINED': 'DECLINED',
    'IN_PROGRESS': 'IN_PROGRESS',
    'PROPOSED': 'PROPOSED',
    'COMPLETED': 'COMPLETED',
    'CLOSED': 'CLOSED',
  };
  static const Map<Object, String> _fromWire = const <Object, String>{
    'SUBMITTED': 'SUBMITTED',
    'IN_REVIEW': 'IN_REVIEW',
    'NEEDS_INFO': 'NEEDS_INFO',
    'DECLINED': 'DECLINED',
    'IN_PROGRESS': 'IN_PROGRESS',
    'PROPOSED': 'PROPOSED',
    'COMPLETED': 'COMPLETED',
    'CLOSED': 'CLOSED',
  };

  @override
  final Iterable<Type> types = const <Type>[StatusEnum];
  @override
  final String wireName = 'StatusEnum';

  @override
  Object serialize(Serializers serializers, StatusEnum object,
          {FullType specifiedType = FullType.unspecified}) =>
      _toWire[object.name] ?? object.name;

  @override
  StatusEnum deserialize(Serializers serializers, Object serialized,
          {FullType specifiedType = FullType.unspecified}) =>
      StatusEnum.valueOf(
          _fromWire[serialized] ?? (serialized is String ? serialized : ''));
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
