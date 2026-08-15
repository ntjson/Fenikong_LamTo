//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'notification_feed.g.dart';

/// NotificationFeed
///
/// Properties:
/// * [id]
/// * [eventCode]
/// * [eventKey] - Deep-link reference '{code}:{entity}:{id}' (spec 6.3/7.4). Entity ids are resident-visible resources the API re-authorizes on fetch. Authorization-neutral and non-sensitive: codes/entity/ids only — no PII, bodies, or tokens.
/// * [subject]
/// * [body]
/// * [createdAt]
/// * [readAt]
@BuiltValue()
abstract class NotificationFeed implements Built<NotificationFeed, NotificationFeedBuilder> {
  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'event_code')
  String get eventCode;

  /// Deep-link reference '{code}:{entity}:{id}' (spec 6.3/7.4). Entity ids are resident-visible resources the API re-authorizes on fetch. Authorization-neutral and non-sensitive: codes/entity/ids only — no PII, bodies, or tokens.
  @BuiltValueField(wireName: r'event_key')
  String get eventKey;

  @BuiltValueField(wireName: r'subject')
  String get subject;

  @BuiltValueField(wireName: r'body')
  String get body;

  @BuiltValueField(wireName: r'created_at')
  DateTime get createdAt;

  @BuiltValueField(wireName: r'read_at')
  DateTime? get readAt;

  NotificationFeed._();

  factory NotificationFeed([void updates(NotificationFeedBuilder b)]) = _$NotificationFeed;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(NotificationFeedBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<NotificationFeed> get serializer => _$NotificationFeedSerializer();
}

class _$NotificationFeedSerializer implements PrimitiveSerializer<NotificationFeed> {
  @override
  final Iterable<Type> types = const [NotificationFeed, _$NotificationFeed];

  @override
  final String wireName = r'NotificationFeed';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    NotificationFeed object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(int),
    );
    yield r'event_code';
    yield serializers.serialize(
      object.eventCode,
      specifiedType: const FullType(String),
    );
    yield r'event_key';
    yield serializers.serialize(
      object.eventKey,
      specifiedType: const FullType(String),
    );
    yield r'subject';
    yield serializers.serialize(
      object.subject,
      specifiedType: const FullType(String),
    );
    yield r'body';
    yield serializers.serialize(
      object.body,
      specifiedType: const FullType(String),
    );
    yield r'created_at';
    yield serializers.serialize(
      object.createdAt,
      specifiedType: const FullType(DateTime),
    );
    yield r'read_at';
    yield object.readAt == null ? null : serializers.serialize(
      object.readAt,
      specifiedType: const FullType.nullable(DateTime),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    NotificationFeed object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required NotificationFeedBuilder result,
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
        case r'event_code':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.eventCode = valueDes;
          break;
        case r'event_key':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.eventKey = valueDes;
          break;
        case r'subject':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.subject = valueDes;
          break;
        case r'body':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.body = valueDes;
          break;
        case r'created_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.createdAt = valueDes;
          break;
        case r'read_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.readAt = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  NotificationFeed deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = NotificationFeedBuilder();
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
