//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'notification_preference.g.dart';

/// NotificationPreference
///
/// Properties:
/// * [eventCode]
/// * [emailEnabled]
/// * [pushEnabled]
@BuiltValue()
abstract class NotificationPreference implements Built<NotificationPreference, NotificationPreferenceBuilder> {
  @BuiltValueField(wireName: r'event_code')
  String get eventCode;

  @BuiltValueField(wireName: r'email_enabled')
  bool get emailEnabled;

  @BuiltValueField(wireName: r'push_enabled')
  bool get pushEnabled;

  NotificationPreference._();

  factory NotificationPreference([void updates(NotificationPreferenceBuilder b)]) = _$NotificationPreference;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(NotificationPreferenceBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<NotificationPreference> get serializer => _$NotificationPreferenceSerializer();
}

class _$NotificationPreferenceSerializer implements PrimitiveSerializer<NotificationPreference> {
  @override
  final Iterable<Type> types = const [NotificationPreference, _$NotificationPreference];

  @override
  final String wireName = r'NotificationPreference';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    NotificationPreference object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'event_code';
    yield serializers.serialize(
      object.eventCode,
      specifiedType: const FullType(String),
    );
    yield r'email_enabled';
    yield serializers.serialize(
      object.emailEnabled,
      specifiedType: const FullType(bool),
    );
    yield r'push_enabled';
    yield serializers.serialize(
      object.pushEnabled,
      specifiedType: const FullType(bool),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    NotificationPreference object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required NotificationPreferenceBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'event_code':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.eventCode = valueDes;
          break;
        case r'email_enabled':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.emailEnabled = valueDes;
          break;
        case r'push_enabled':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.pushEnabled = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  NotificationPreference deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = NotificationPreferenceBuilder();
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
