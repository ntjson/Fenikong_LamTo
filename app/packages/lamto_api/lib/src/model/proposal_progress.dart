//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'proposal_progress.g.dart';

/// ProposalProgress
///
/// Properties:
/// * [id]
/// * [cause]
/// * [result]
/// * [createdAt]
@BuiltValue()
abstract class ProposalProgress implements Built<ProposalProgress, ProposalProgressBuilder> {
  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'cause')
  String get cause;

  @BuiltValueField(wireName: r'result')
  String get result;

  @BuiltValueField(wireName: r'created_at')
  DateTime get createdAt;

  ProposalProgress._();

  factory ProposalProgress([void updates(ProposalProgressBuilder b)]) = _$ProposalProgress;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ProposalProgressBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ProposalProgress> get serializer => _$ProposalProgressSerializer();
}

class _$ProposalProgressSerializer implements PrimitiveSerializer<ProposalProgress> {
  @override
  final Iterable<Type> types = const [ProposalProgress, _$ProposalProgress];

  @override
  final String wireName = r'ProposalProgress';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ProposalProgress object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(int),
    );
    yield r'cause';
    yield serializers.serialize(
      object.cause,
      specifiedType: const FullType(String),
    );
    yield r'result';
    yield serializers.serialize(
      object.result,
      specifiedType: const FullType(String),
    );
    yield r'created_at';
    yield serializers.serialize(
      object.createdAt,
      specifiedType: const FullType(DateTime),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    ProposalProgress object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ProposalProgressBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.id = valueDes;
          break;
        case r'cause':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.cause = valueDes;
          break;
        case r'result':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.result = valueDes;
          break;
        case r'created_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.createdAt = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  ProposalProgress deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ProposalProgressBuilder();
    final serializedList = (serialized as Iterable<Object?>).toList();
    final unhandled = <Object?>[];
    _deserializeProperties(
      serializers,
      serialized,
      specifiedType: specifiedType,
      serializedList: serializedList,
      unhandled: unhandled,
      result: result,
    );
    return result.build();
  }
}
