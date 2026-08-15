//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:lamto_api/src/model/notification_feed.dart';
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'paginated_notification_feed_list.g.dart';

/// PaginatedNotificationFeedList
///
/// Properties:
/// * [next]
/// * [previous]
/// * [results]
@BuiltValue()
abstract class PaginatedNotificationFeedList implements Built<PaginatedNotificationFeedList, PaginatedNotificationFeedListBuilder> {
  @BuiltValueField(wireName: r'next')
  String? get next;

  @BuiltValueField(wireName: r'previous')
  String? get previous;

  @BuiltValueField(wireName: r'results')
  BuiltList<NotificationFeed> get results;

  PaginatedNotificationFeedList._();

  factory PaginatedNotificationFeedList([void updates(PaginatedNotificationFeedListBuilder b)]) = _$PaginatedNotificationFeedList;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(PaginatedNotificationFeedListBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<PaginatedNotificationFeedList> get serializer => _$PaginatedNotificationFeedListSerializer();
}

class _$PaginatedNotificationFeedListSerializer implements PrimitiveSerializer<PaginatedNotificationFeedList> {
  @override
  final Iterable<Type> types = const [PaginatedNotificationFeedList, _$PaginatedNotificationFeedList];

  @override
  final String wireName = r'PaginatedNotificationFeedList';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    PaginatedNotificationFeedList object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.next != null) {
      yield r'next';
      yield serializers.serialize(
        object.next,
        specifiedType: const FullType.nullable(String),
      );
    }
    if (object.previous != null) {
      yield r'previous';
      yield serializers.serialize(
        object.previous,
        specifiedType: const FullType.nullable(String),
      );
    }
    yield r'results';
    yield serializers.serialize(
      object.results,
      specifiedType: const FullType(BuiltList, [FullType(NotificationFeed)]),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    PaginatedNotificationFeedList object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required PaginatedNotificationFeedListBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'next':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.next = valueDes;
          break;
        case r'previous':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.previous = valueDes;
          break;
        case r'results':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(NotificationFeed)]),
          ) as BuiltList<NotificationFeed>;
          result.results.replace(valueDes);
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  PaginatedNotificationFeedList deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = PaginatedNotificationFeedListBuilder();
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
