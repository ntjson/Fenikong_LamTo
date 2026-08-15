//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'face_enrollment.g.dart';

/// FaceEnrollment
///
/// Properties:
/// * [status]
/// * [submittedAt]
/// * [reviewNote]
@BuiltValue()
abstract class FaceEnrollment implements Built<FaceEnrollment, FaceEnrollmentBuilder> {
  @BuiltValueField(wireName: r'status')
  String get status;

  @BuiltValueField(wireName: r'submitted_at')
  DateTime get submittedAt;

  @BuiltValueField(wireName: r'review_note')
  String get reviewNote;

  FaceEnrollment._();

  factory FaceEnrollment([void updates(FaceEnrollmentBuilder b)]) = _$FaceEnrollment;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(FaceEnrollmentBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<FaceEnrollment> get serializer => _$FaceEnrollmentSerializer();
}

class _$FaceEnrollmentSerializer implements PrimitiveSerializer<FaceEnrollment> {
  @override
  final Iterable<Type> types = const [FaceEnrollment, _$FaceEnrollment];

  @override
  final String wireName = r'FaceEnrollment';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    FaceEnrollment object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'status';
    yield serializers.serialize(
      object.status,
      specifiedType: const FullType(String),
    );
    yield r'submitted_at';
    yield serializers.serialize(
      object.submittedAt,
      specifiedType: const FullType(DateTime),
    );
    yield r'review_note';
    yield serializers.serialize(
      object.reviewNote,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    FaceEnrollment object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required FaceEnrollmentBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'status':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.status = valueDes;
          break;
        case r'submitted_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.submittedAt = valueDes;
          break;
        case r'review_note':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.reviewNote = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  FaceEnrollment deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = FaceEnrollmentBuilder();
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
