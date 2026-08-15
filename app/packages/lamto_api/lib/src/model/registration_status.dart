//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:lamto_api/src/model/registration_status_enum.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'registration_status.g.dart';

/// RegistrationStatus
///
/// Properties:
/// * [status]
/// * [phone]
/// * [building]
/// * [unit]
/// * [rejectionReason]
@BuiltValue()
abstract class RegistrationStatus implements Built<RegistrationStatus, RegistrationStatusBuilder> {
  @BuiltValueField(wireName: r'status')
  RegistrationStatusEnum get status;
  // enum statusEnum {  PENDING,  APPROVED,  REJECTED,  EXPIRED,  };

  @BuiltValueField(wireName: r'phone')
  String get phone;

  @BuiltValueField(wireName: r'building')
  String get building;

  @BuiltValueField(wireName: r'unit')
  String get unit;

  @BuiltValueField(wireName: r'rejection_reason')
  String? get rejectionReason;

  RegistrationStatus._();

  factory RegistrationStatus([void updates(RegistrationStatusBuilder b)]) = _$RegistrationStatus;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(RegistrationStatusBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<RegistrationStatus> get serializer => _$RegistrationStatusSerializer();
}

class _$RegistrationStatusSerializer implements PrimitiveSerializer<RegistrationStatus> {
  @override
  final Iterable<Type> types = const [RegistrationStatus, _$RegistrationStatus];

  @override
  final String wireName = r'RegistrationStatus';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    RegistrationStatus object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'status';
    yield serializers.serialize(
      object.status,
      specifiedType: const FullType(RegistrationStatusEnum),
    );
    yield r'phone';
    yield serializers.serialize(
      object.phone,
      specifiedType: const FullType(String),
    );
    yield r'building';
    yield serializers.serialize(
      object.building,
      specifiedType: const FullType(String),
    );
    yield r'unit';
    yield serializers.serialize(
      object.unit,
      specifiedType: const FullType(String),
    );
    if (object.rejectionReason != null) {
      yield r'rejection_reason';
      yield serializers.serialize(
        object.rejectionReason,
        specifiedType: const FullType(String),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    RegistrationStatus object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required RegistrationStatusBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'status':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(RegistrationStatusEnum),
          ) as RegistrationStatusEnum;
          result.status = valueDes;
          break;
        case r'phone':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.phone = valueDes;
          break;
        case r'building':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.building = valueDes;
          break;
        case r'unit':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.unit = valueDes;
          break;
        case r'rejection_reason':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.rejectionReason = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  RegistrationStatus deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = RegistrationStatusBuilder();
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
