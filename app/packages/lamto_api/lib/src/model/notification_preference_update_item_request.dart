//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'notification_preference_update_item_request.g.dart';

/// One preference row for PATCH /me/notification-preferences.
///
/// Properties:
/// * [eventCode]
/// * [emailEnabled]
/// * [pushEnabled]
@BuiltValue()
abstract class NotificationPreferenceUpdateItemRequest implements Built<NotificationPreferenceUpdateItemRequest, NotificationPreferenceUpdateItemRequestBuilder> {
  @BuiltValueField(wireName: r'event_code')
  String get eventCode;

  @BuiltValueField(wireName: r'email_enabled')
  bool? get emailEnabled;

  @BuiltValueField(wireName: r'push_enabled')
  bool? get pushEnabled;

  NotificationPreferenceUpdateItemRequest._();

  factory NotificationPreferenceUpdateItemRequest([void updates(NotificationPreferenceUpdateItemRequestBuilder b)]) = _$NotificationPreferenceUpdateItemRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(NotificationPreferenceUpdateItemRequestBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<NotificationPreferenceUpdateItemRequest> get serializer => _$NotificationPreferenceUpdateItemRequestSerializer();
}

class _$NotificationPreferenceUpdateItemRequestSerializer implements PrimitiveSerializer<NotificationPreferenceUpdateItemRequest> {
  @override
  final Iterable<Type> types = const [NotificationPreferenceUpdateItemRequest, _$NotificationPreferenceUpdateItemRequest];

  @override
  final String wireName = r'NotificationPreferenceUpdateItemRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    NotificationPreferenceUpdateItemRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'event_code';
    yield serializers.serialize(
      object.eventCode,
      specifiedType: const FullType(String),
    );
    if (object.emailEnabled != null) {
      yield r'email_enabled';
      yield serializers.serialize(
        object.emailEnabled,
        specifiedType: const FullType(bool),
      );
    }
    if (object.pushEnabled != null) {
      yield r'push_enabled';
      yield serializers.serialize(
        object.pushEnabled,
        specifiedType: const FullType(bool),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    NotificationPreferenceUpdateItemRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required NotificationPreferenceUpdateItemRequestBuilder result,
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
  NotificationPreferenceUpdateItemRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = NotificationPreferenceUpdateItemRequestBuilder();
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
