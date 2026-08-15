//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'recognition_outcome.g.dart';

/// RecognitionOutcome
///
/// Properties:
/// * [matched]
/// * [displayName]
/// * [unitLabel]
/// * [direction]
/// * [score]
@BuiltValue()
abstract class RecognitionOutcome implements Built<RecognitionOutcome, RecognitionOutcomeBuilder> {
  @BuiltValueField(wireName: r'matched')
  bool get matched;

  @BuiltValueField(wireName: r'display_name')
  String get displayName;

  @BuiltValueField(wireName: r'unit_label')
  String get unitLabel;

  @BuiltValueField(wireName: r'direction')
  String get direction;

  @BuiltValueField(wireName: r'score')
  double? get score;

  RecognitionOutcome._();

  factory RecognitionOutcome([void updates(RecognitionOutcomeBuilder b)]) = _$RecognitionOutcome;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(RecognitionOutcomeBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<RecognitionOutcome> get serializer => _$RecognitionOutcomeSerializer();
}

class _$RecognitionOutcomeSerializer implements PrimitiveSerializer<RecognitionOutcome> {
  @override
  final Iterable<Type> types = const [RecognitionOutcome, _$RecognitionOutcome];

  @override
  final String wireName = r'RecognitionOutcome';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    RecognitionOutcome object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'matched';
    yield serializers.serialize(
      object.matched,
      specifiedType: const FullType(bool),
    );
    yield r'display_name';
    yield serializers.serialize(
      object.displayName,
      specifiedType: const FullType(String),
    );
    yield r'unit_label';
    yield serializers.serialize(
      object.unitLabel,
      specifiedType: const FullType(String),
    );
    yield r'direction';
    yield serializers.serialize(
      object.direction,
      specifiedType: const FullType(String),
    );
    yield r'score';
    yield object.score == null ? null : serializers.serialize(
      object.score,
      specifiedType: const FullType.nullable(double),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    RecognitionOutcome object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required RecognitionOutcomeBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'matched':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.matched = valueDes;
          break;
        case r'display_name':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.displayName = valueDes;
          break;
        case r'unit_label':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.unitLabel = valueDes;
          break;
        case r'direction':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.direction = valueDes;
          break;
        case r'score':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(double),
          ) as double?;
          if (valueDes == null) continue;
          result.score = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  RecognitionOutcome deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = RecognitionOutcomeBuilder();
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
