//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:lamto_api/src/model/registration_status_enum.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'registration_submission.g.dart';

/// RegistrationSubmission
///
/// Properties:
/// * [status]
/// * [statusToken]
/// * [phone]
@BuiltValue()
abstract class RegistrationSubmission implements Built<RegistrationSubmission, RegistrationSubmissionBuilder> {
  @BuiltValueField(wireName: r'status')
  RegistrationStatusEnum get status;
  // enum statusEnum {  PENDING,  APPROVED,  REJECTED,  EXPIRED,  };

  @BuiltValueField(wireName: r'status_token')
  String get statusToken;

  @BuiltValueField(wireName: r'phone')
  String get phone;

  RegistrationSubmission._();

  factory RegistrationSubmission([void updates(RegistrationSubmissionBuilder b)]) = _$RegistrationSubmission;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(RegistrationSubmissionBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<RegistrationSubmission> get serializer => _$RegistrationSubmissionSerializer();
}

class _$RegistrationSubmissionSerializer implements PrimitiveSerializer<RegistrationSubmission> {
  @override
  final Iterable<Type> types = const [RegistrationSubmission, _$RegistrationSubmission];

  @override
  final String wireName = r'RegistrationSubmission';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    RegistrationSubmission object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'status';
    yield serializers.serialize(
      object.status,
      specifiedType: const FullType(RegistrationStatusEnum),
    );
    yield r'status_token';
    yield serializers.serialize(
      object.statusToken,
      specifiedType: const FullType(String),
    );
    yield r'phone';
    yield serializers.serialize(
      object.phone,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    RegistrationSubmission object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required RegistrationSubmissionBuilder result,
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
        case r'status_token':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.statusToken = valueDes;
          break;
        case r'phone':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.phone = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  RegistrationSubmission deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = RegistrationSubmissionBuilder();
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
