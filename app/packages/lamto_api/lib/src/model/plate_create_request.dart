//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'plate_create_request.g.dart';

/// PlateCreateRequest
///
/// Properties:
/// * [plate]
@BuiltValue()
abstract class PlateCreateRequest implements Built<PlateCreateRequest, PlateCreateRequestBuilder> {
  @BuiltValueField(wireName: r'plate')
  String get plate;

  PlateCreateRequest._();

  factory PlateCreateRequest([void updates(PlateCreateRequestBuilder b)]) = _$PlateCreateRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(PlateCreateRequestBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<PlateCreateRequest> get serializer => _$PlateCreateRequestSerializer();
}

class _$PlateCreateRequestSerializer implements PrimitiveSerializer<PlateCreateRequest> {
  @override
  final Iterable<Type> types = const [PlateCreateRequest, _$PlateCreateRequest];

  @override
  final String wireName = r'PlateCreateRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    PlateCreateRequest object, {
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
    PlateCreateRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required PlateCreateRequestBuilder result,
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
  PlateCreateRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = PlateCreateRequestBuilder();
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
