//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:lamto_api/src/model/vehicle_plate.dart';
import 'package:lamto_api/src/model/face_enrollment.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'gate_registrations.g.dart';

/// GateRegistrations
///
/// Properties:
/// * [face]
/// * [plates]
@BuiltValue()
abstract class GateRegistrations implements Built<GateRegistrations, GateRegistrationsBuilder> {
  @BuiltValueField(wireName: r'face')
  FaceEnrollment? get face;

  @BuiltValueField(wireName: r'plates')
  BuiltList<VehiclePlate> get plates;

  GateRegistrations._();

  factory GateRegistrations([void updates(GateRegistrationsBuilder b)]) = _$GateRegistrations;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(GateRegistrationsBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<GateRegistrations> get serializer => _$GateRegistrationsSerializer();
}

class _$GateRegistrationsSerializer implements PrimitiveSerializer<GateRegistrations> {
  @override
  final Iterable<Type> types = const [GateRegistrations, _$GateRegistrations];

  @override
  final String wireName = r'GateRegistrations';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    GateRegistrations object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'face';
    yield object.face == null ? null : serializers.serialize(
      object.face,
      specifiedType: const FullType.nullable(FaceEnrollment),
    );
    yield r'plates';
    yield serializers.serialize(
      object.plates,
      specifiedType: const FullType(BuiltList, [FullType(VehiclePlate)]),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    GateRegistrations object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required GateRegistrationsBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'face':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(FaceEnrollment),
          ) as FaceEnrollment?;
          if (valueDes == null) continue;
          result.face.replace(valueDes);
          break;
        case r'plates':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(VehiclePlate)]),
          ) as BuiltList<VehiclePlate>;
          result.plates.replace(valueDes);
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  GateRegistrations deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = GateRegistrationsBuilder();
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
