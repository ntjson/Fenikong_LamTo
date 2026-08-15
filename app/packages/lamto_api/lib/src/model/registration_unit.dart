//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'registration_unit.g.dart';

/// RegistrationUnit
///
/// Properties:
/// * [id]
/// * [label]
@BuiltValue()
abstract class RegistrationUnit implements Built<RegistrationUnit, RegistrationUnitBuilder> {
  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'label')
  String get label;

  RegistrationUnit._();

  factory RegistrationUnit([void updates(RegistrationUnitBuilder b)]) = _$RegistrationUnit;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(RegistrationUnitBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<RegistrationUnit> get serializer => _$RegistrationUnitSerializer();
}

class _$RegistrationUnitSerializer implements PrimitiveSerializer<RegistrationUnit> {
  @override
  final Iterable<Type> types = const [RegistrationUnit, _$RegistrationUnit];

  @override
  final String wireName = r'RegistrationUnit';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    RegistrationUnit object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(int),
    );
    yield r'label';
    yield serializers.serialize(
      object.label,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    RegistrationUnit object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required RegistrationUnitBuilder result,
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
        case r'label':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.label = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  RegistrationUnit deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = RegistrationUnitBuilder();
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
