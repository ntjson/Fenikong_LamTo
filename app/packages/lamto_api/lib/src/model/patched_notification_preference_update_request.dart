//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:lamto_api/src/model/notification_preference_update_item_request.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'patched_notification_preference_update_request.g.dart';

/// PatchedNotificationPreferenceUpdateRequest
///
/// Properties:
/// * [preferences]
@BuiltValue()
abstract class PatchedNotificationPreferenceUpdateRequest implements Built<PatchedNotificationPreferenceUpdateRequest, PatchedNotificationPreferenceUpdateRequestBuilder> {
  @BuiltValueField(wireName: r'preferences')
  BuiltList<NotificationPreferenceUpdateItemRequest>? get preferences;

  PatchedNotificationPreferenceUpdateRequest._();

  factory PatchedNotificationPreferenceUpdateRequest([void updates(PatchedNotificationPreferenceUpdateRequestBuilder b)]) = _$PatchedNotificationPreferenceUpdateRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(PatchedNotificationPreferenceUpdateRequestBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<PatchedNotificationPreferenceUpdateRequest> get serializer => _$PatchedNotificationPreferenceUpdateRequestSerializer();
}

class _$PatchedNotificationPreferenceUpdateRequestSerializer implements PrimitiveSerializer<PatchedNotificationPreferenceUpdateRequest> {
  @override
  final Iterable<Type> types = const [PatchedNotificationPreferenceUpdateRequest, _$PatchedNotificationPreferenceUpdateRequest];

  @override
  final String wireName = r'PatchedNotificationPreferenceUpdateRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    PatchedNotificationPreferenceUpdateRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.preferences != null) {
      yield r'preferences';
      yield serializers.serialize(
        object.preferences,
        specifiedType: const FullType(BuiltList, [FullType(NotificationPreferenceUpdateItemRequest)]),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    PatchedNotificationPreferenceUpdateRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required PatchedNotificationPreferenceUpdateRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'preferences':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(NotificationPreferenceUpdateItemRequest)]),
          ) as BuiltList<NotificationPreferenceUpdateItemRequest>;
          result.preferences.replace(valueDes);
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  PatchedNotificationPreferenceUpdateRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = PatchedNotificationPreferenceUpdateRequestBuilder();
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
