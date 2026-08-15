//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'vehicle_plate.g.dart';

/// VehiclePlate
///
/// Properties:
/// * [id]
/// * [plate]
/// * [status]
/// * [submittedAt]
/// * [reviewNote]
@BuiltValue()
abstract class VehiclePlate implements Built<VehiclePlate, VehiclePlateBuilder> {
  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'plate')
  String get plate;

  @BuiltValueField(wireName: r'status')
  String get status;

  @BuiltValueField(wireName: r'submitted_at')
  DateTime get submittedAt;

  @BuiltValueField(wireName: r'review_note')
  String get reviewNote;

  VehiclePlate._();

  factory VehiclePlate([void updates(VehiclePlateBuilder b)]) = _$VehiclePlate;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(VehiclePlateBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<VehiclePlate> get serializer => _$VehiclePlateSerializer();
}

class _$VehiclePlateSerializer implements PrimitiveSerializer<VehiclePlate> {
  @override
  final Iterable<Type> types = const [VehiclePlate, _$VehiclePlate];

  @override
  final String wireName = r'VehiclePlate';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    VehiclePlate object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(int),
    );
    yield r'plate';
    yield serializers.serialize(
      object.plate,
      specifiedType: const FullType(String),
    );
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
    VehiclePlate object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required VehiclePlateBuilder result,
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
        case r'plate':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.plate = valueDes;
          break;
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
  VehiclePlate deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = VehiclePlateBuilder();
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
