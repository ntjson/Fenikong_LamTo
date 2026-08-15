//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'proposal_rating_result.g.dart';

/// ProposalRatingResult
///
/// Properties:
/// * [id]
/// * [proposalId]
/// * [satisfied]
@BuiltValue()
abstract class ProposalRatingResult implements Built<ProposalRatingResult, ProposalRatingResultBuilder> {
  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'proposal_id')
  int get proposalId;

  @BuiltValueField(wireName: r'satisfied')
  bool get satisfied;

  ProposalRatingResult._();

  factory ProposalRatingResult([void updates(ProposalRatingResultBuilder b)]) = _$ProposalRatingResult;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ProposalRatingResultBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ProposalRatingResult> get serializer => _$ProposalRatingResultSerializer();
}

class _$ProposalRatingResultSerializer implements PrimitiveSerializer<ProposalRatingResult> {
  @override
  final Iterable<Type> types = const [ProposalRatingResult, _$ProposalRatingResult];

  @override
  final String wireName = r'ProposalRatingResult';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ProposalRatingResult object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(int),
    );
    yield r'proposal_id';
    yield serializers.serialize(
      object.proposalId,
      specifiedType: const FullType(int),
    );
    yield r'satisfied';
    yield serializers.serialize(
      object.satisfied,
      specifiedType: const FullType(bool),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    ProposalRatingResult object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ProposalRatingResultBuilder result,
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
        case r'proposal_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.proposalId = valueDes;
          break;
        case r'satisfied':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.satisfied = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  ProposalRatingResult deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ProposalRatingResultBuilder();
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
