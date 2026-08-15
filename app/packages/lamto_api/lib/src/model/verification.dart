//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'verification.g.dart';

/// Verification
///
/// Properties:
/// * [decision]
/// * [verifiedBy]
/// * [verifiedAt]
@BuiltValue()
abstract class Verification implements Built<Verification, VerificationBuilder> {
  @BuiltValueField(wireName: r'decision')
  String get decision;

  @BuiltValueField(wireName: r'verified_by')
  String get verifiedBy;

  @BuiltValueField(wireName: r'verified_at')
  DateTime get verifiedAt;

  Verification._();

  factory Verification([void updates(VerificationBuilder b)]) = _$Verification;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(VerificationBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<Verification> get serializer => _$VerificationSerializer();
}

class _$VerificationSerializer implements PrimitiveSerializer<Verification> {
  @override
  final Iterable<Type> types = const [Verification, _$Verification];

  @override
  final String wireName = r'Verification';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    Verification object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'decision';
    yield serializers.serialize(
      object.decision,
      specifiedType: const FullType(String),
    );
    yield r'verified_by';
    yield serializers.serialize(
      object.verifiedBy,
      specifiedType: const FullType(String),
    );
    yield r'verified_at';
    yield serializers.serialize(
      object.verifiedAt,
      specifiedType: const FullType(DateTime),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    Verification object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required VerificationBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'decision':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.decision = valueDes;
          break;
        case r'verified_by':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.verifiedBy = valueDes;
          break;
        case r'verified_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.verifiedAt = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  Verification deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = VerificationBuilder();
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
