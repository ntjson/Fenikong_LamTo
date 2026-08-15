//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'registration_create_request.g.dart';

/// RegistrationCreateRequest
///
/// Properties:
/// * [fullName]
/// * [phone]
/// * [email]
/// * [password]
/// * [buildingId]
/// * [unitId]
@BuiltValue()
abstract class RegistrationCreateRequest implements Built<RegistrationCreateRequest, RegistrationCreateRequestBuilder> {
  @BuiltValueField(wireName: r'full_name')
  String get fullName;

  @BuiltValueField(wireName: r'phone')
  String get phone;

  @BuiltValueField(wireName: r'email')
  String? get email;

  @BuiltValueField(wireName: r'password')
  String get password;

  @BuiltValueField(wireName: r'building_id')
  int get buildingId;

  @BuiltValueField(wireName: r'unit_id')
  int get unitId;

  RegistrationCreateRequest._();

  factory RegistrationCreateRequest([void updates(RegistrationCreateRequestBuilder b)]) = _$RegistrationCreateRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(RegistrationCreateRequestBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<RegistrationCreateRequest> get serializer => _$RegistrationCreateRequestSerializer();
}

class _$RegistrationCreateRequestSerializer implements PrimitiveSerializer<RegistrationCreateRequest> {
  @override
  final Iterable<Type> types = const [RegistrationCreateRequest, _$RegistrationCreateRequest];

  @override
  final String wireName = r'RegistrationCreateRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    RegistrationCreateRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'full_name';
    yield serializers.serialize(
      object.fullName,
      specifiedType: const FullType(String),
    );
    yield r'phone';
    yield serializers.serialize(
      object.phone,
      specifiedType: const FullType(String),
    );
    if (object.email != null) {
      yield r'email';
      yield serializers.serialize(
        object.email,
        specifiedType: const FullType(String),
      );
    }
    yield r'password';
    yield serializers.serialize(
      object.password,
      specifiedType: const FullType(String),
    );
    yield r'building_id';
    yield serializers.serialize(
      object.buildingId,
      specifiedType: const FullType(int),
    );
    yield r'unit_id';
    yield serializers.serialize(
      object.unitId,
      specifiedType: const FullType(int),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    RegistrationCreateRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required RegistrationCreateRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'full_name':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.fullName = valueDes;
          break;
        case r'phone':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.phone = valueDes;
          break;
        case r'email':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.email = valueDes;
          break;
        case r'password':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.password = valueDes;
          break;
        case r'building_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.buildingId = valueDes;
          break;
        case r'unit_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.unitId = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  RegistrationCreateRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = RegistrationCreateRequestBuilder();
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
