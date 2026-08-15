//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'case_rating_result.g.dart';

/// CaseRatingResult
///
/// Properties:
/// * [id]
/// * [caseId]
/// * [satisfied]
@BuiltValue()
abstract class CaseRatingResult implements Built<CaseRatingResult, CaseRatingResultBuilder> {
  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'case_id')
  int get caseId;

  @BuiltValueField(wireName: r'satisfied')
  bool get satisfied;

  CaseRatingResult._();

  factory CaseRatingResult([void updates(CaseRatingResultBuilder b)]) = _$CaseRatingResult;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(CaseRatingResultBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<CaseRatingResult> get serializer => _$CaseRatingResultSerializer();
}

class _$CaseRatingResultSerializer implements PrimitiveSerializer<CaseRatingResult> {
  @override
  final Iterable<Type> types = const [CaseRatingResult, _$CaseRatingResult];

  @override
  final String wireName = r'CaseRatingResult';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    CaseRatingResult object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(int),
    );
    yield r'case_id';
    yield serializers.serialize(
      object.caseId,
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
    CaseRatingResult object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required CaseRatingResultBuilder result,
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
        case r'case_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.caseId = valueDes;
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
  CaseRatingResult deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = CaseRatingResultBuilder();
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
