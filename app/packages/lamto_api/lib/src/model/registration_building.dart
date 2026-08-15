//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:lamto_api/src/model/registration_unit.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'registration_building.g.dart';

/// RegistrationBuilding
///
/// Properties:
/// * [id]
/// * [name]
/// * [units]
@BuiltValue()
abstract class RegistrationBuilding implements Built<RegistrationBuilding, RegistrationBuildingBuilder> {
  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'name')
  String get name;

  @BuiltValueField(wireName: r'units')
  BuiltList<RegistrationUnit> get units;

  RegistrationBuilding._();

  factory RegistrationBuilding([void updates(RegistrationBuildingBuilder b)]) = _$RegistrationBuilding;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(RegistrationBuildingBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<RegistrationBuilding> get serializer => _$RegistrationBuildingSerializer();
}

class _$RegistrationBuildingSerializer implements PrimitiveSerializer<RegistrationBuilding> {
  @override
  final Iterable<Type> types = const [RegistrationBuilding, _$RegistrationBuilding];

  @override
  final String wireName = r'RegistrationBuilding';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    RegistrationBuilding object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(int),
    );
    yield r'name';
    yield serializers.serialize(
      object.name,
      specifiedType: const FullType(String),
    );
    yield r'units';
    yield serializers.serialize(
      object.units,
      specifiedType: const FullType(BuiltList, [FullType(RegistrationUnit)]),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    RegistrationBuilding object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required RegistrationBuildingBuilder result,
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
        case r'name':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.name = valueDes;
          break;
        case r'units':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(RegistrationUnit)]),
          ) as BuiltList<RegistrationUnit>;
          result.units.replace(valueDes);
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  RegistrationBuilding deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = RegistrationBuildingBuilder();
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
