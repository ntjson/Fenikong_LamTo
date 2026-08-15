//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'occupancy.g.dart';

/// Occupancy
///
/// Properties:
/// * [id]
/// * [unitLabel]
/// * [buildingName]
@BuiltValue()
abstract class Occupancy implements Built<Occupancy, OccupancyBuilder> {
  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'unit_label')
  String get unitLabel;

  @BuiltValueField(wireName: r'building_name')
  String get buildingName;

  Occupancy._();

  factory Occupancy([void updates(OccupancyBuilder b)]) = _$Occupancy;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(OccupancyBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<Occupancy> get serializer => _$OccupancySerializer();
}

class _$OccupancySerializer implements PrimitiveSerializer<Occupancy> {
  @override
  final Iterable<Type> types = const [Occupancy, _$Occupancy];

  @override
  final String wireName = r'Occupancy';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    Occupancy object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(int),
    );
    yield r'unit_label';
    yield serializers.serialize(
      object.unitLabel,
      specifiedType: const FullType(String),
    );
    yield r'building_name';
    yield serializers.serialize(
      object.buildingName,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    Occupancy object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required OccupancyBuilder result,
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
        case r'unit_label':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.unitLabel = valueDes;
          break;
        case r'building_name':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.buildingName = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  Occupancy deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = OccupancyBuilder();
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
