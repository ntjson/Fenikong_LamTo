//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'plate_recognize_request.g.dart';

/// PlateRecognizeRequest
///
/// Properties:
/// * [plate]
@BuiltValue()
abstract class PlateRecognizeRequest implements Built<PlateRecognizeRequest, PlateRecognizeRequestBuilder> {
  @BuiltValueField(wireName: r'plate')
  String get plate;

  PlateRecognizeRequest._();

  factory PlateRecognizeRequest([void updates(PlateRecognizeRequestBuilder b)]) = _$PlateRecognizeRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(PlateRecognizeRequestBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<PlateRecognizeRequest> get serializer => _$PlateRecognizeRequestSerializer();
}

class _$PlateRecognizeRequestSerializer implements PrimitiveSerializer<PlateRecognizeRequest> {
  @override
  final Iterable<Type> types = const [PlateRecognizeRequest, _$PlateRecognizeRequest];

  @override
  final String wireName = r'PlateRecognizeRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    PlateRecognizeRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'plate';
    yield serializers.serialize(
      object.plate,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    PlateRecognizeRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required PlateRecognizeRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'plate':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.plate = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  PlateRecognizeRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = PlateRecognizeRequestBuilder();
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
