//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:lamto_api/src/model/direction_enum.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'gate_device.g.dart';

/// GateDevice
///
/// Properties:
/// * [label]
/// * [direction]
@BuiltValue()
abstract class GateDevice implements Built<GateDevice, GateDeviceBuilder> {
  @BuiltValueField(wireName: r'label')
  String get label;

  @BuiltValueField(wireName: r'direction')
  DirectionEnum get direction;
  // enum directionEnum {  ENTRY,  EXIT,  };

  GateDevice._();

  factory GateDevice([void updates(GateDeviceBuilder b)]) = _$GateDevice;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(GateDeviceBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<GateDevice> get serializer => _$GateDeviceSerializer();
}

class _$GateDeviceSerializer implements PrimitiveSerializer<GateDevice> {
  @override
  final Iterable<Type> types = const [GateDevice, _$GateDevice];

  @override
  final String wireName = r'GateDevice';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    GateDevice object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'label';
    yield serializers.serialize(
      object.label,
      specifiedType: const FullType(String),
    );
    yield r'direction';
    yield serializers.serialize(
      object.direction,
      specifiedType: const FullType(DirectionEnum),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    GateDevice object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required GateDeviceBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'label':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.label = valueDes;
          break;
        case r'direction':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DirectionEnum),
          ) as DirectionEnum;
          result.direction = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  GateDevice deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = GateDeviceBuilder();
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
