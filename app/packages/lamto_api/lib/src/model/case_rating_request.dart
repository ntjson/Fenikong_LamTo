//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'case_rating_request.g.dart';

/// CaseRatingRequest
///
/// Properties:
/// * [satisfied]
/// * [comment]
@BuiltValue()
abstract class CaseRatingRequest implements Built<CaseRatingRequest, CaseRatingRequestBuilder> {
  @BuiltValueField(wireName: r'satisfied')
  bool get satisfied;

  @BuiltValueField(wireName: r'comment')
  String? get comment;

  CaseRatingRequest._();

  factory CaseRatingRequest([void updates(CaseRatingRequestBuilder b)]) = _$CaseRatingRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(CaseRatingRequestBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<CaseRatingRequest> get serializer => _$CaseRatingRequestSerializer();
}

class _$CaseRatingRequestSerializer implements PrimitiveSerializer<CaseRatingRequest> {
  @override
  final Iterable<Type> types = const [CaseRatingRequest, _$CaseRatingRequest];

  @override
  final String wireName = r'CaseRatingRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    CaseRatingRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'satisfied';
    yield serializers.serialize(
      object.satisfied,
      specifiedType: const FullType(bool),
    );
    if (object.comment != null) {
      yield r'comment';
      yield serializers.serialize(
        object.comment,
        specifiedType: const FullType(String),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    CaseRatingRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required CaseRatingRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'satisfied':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.satisfied = valueDes;
          break;
        case r'comment':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.comment = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  CaseRatingRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = CaseRatingRequestBuilder();
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
