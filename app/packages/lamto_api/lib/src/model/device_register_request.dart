//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:lamto_api/src/model/platform_enum.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'device_register_request.g.dart';

/// DeviceRegisterRequest
///
/// Properties:
/// * [installId] - Stable per-install client UUID (spec 7.2).
/// * [fcmToken]
/// * [platform]
/// * [appVersion]
@BuiltValue()
abstract class DeviceRegisterRequest implements Built<DeviceRegisterRequest, DeviceRegisterRequestBuilder> {
  /// Stable per-install client UUID (spec 7.2).
  @BuiltValueField(wireName: r'install_id')
  String get installId;

  @BuiltValueField(wireName: r'fcm_token')
  String get fcmToken;

  @BuiltValueField(wireName: r'platform')
  PlatformEnum get platform;
  // enum platformEnum {  IOS,  ANDROID,  };

  @BuiltValueField(wireName: r'app_version')
  String? get appVersion;

  DeviceRegisterRequest._();

  factory DeviceRegisterRequest([void updates(DeviceRegisterRequestBuilder b)]) = _$DeviceRegisterRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(DeviceRegisterRequestBuilder b) => b
      ..appVersion = '';

  @BuiltValueSerializer(custom: true)
  static Serializer<DeviceRegisterRequest> get serializer => _$DeviceRegisterRequestSerializer();
}

class _$DeviceRegisterRequestSerializer implements PrimitiveSerializer<DeviceRegisterRequest> {
  @override
  final Iterable<Type> types = const [DeviceRegisterRequest, _$DeviceRegisterRequest];

  @override
  final String wireName = r'DeviceRegisterRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    DeviceRegisterRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'install_id';
    yield serializers.serialize(
      object.installId,
      specifiedType: const FullType(String),
    );
    yield r'fcm_token';
    yield serializers.serialize(
      object.fcmToken,
      specifiedType: const FullType(String),
    );
    yield r'platform';
    yield serializers.serialize(
      object.platform,
      specifiedType: const FullType(PlatformEnum),
    );
    if (object.appVersion != null) {
      yield r'app_version';
      yield serializers.serialize(
        object.appVersion,
        specifiedType: const FullType(String),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    DeviceRegisterRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required DeviceRegisterRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'install_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.installId = valueDes;
          break;
        case r'fcm_token':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.fcmToken = valueDes;
          break;
        case r'platform':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(PlatformEnum),
          ) as PlatformEnum;
          result.platform = valueDes;
          break;
        case r'app_version':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.appVersion = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  DeviceRegisterRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = DeviceRegisterRequestBuilder();
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
