//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:lamto_api/src/model/report_work_update_photo.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'report_work_update.g.dart';

/// ReportWorkUpdate
///
/// Properties:
/// * [id]
/// * [cause]
/// * [result]
/// * [createdAt]
/// * [photos]
@BuiltValue()
abstract class ReportWorkUpdate implements Built<ReportWorkUpdate, ReportWorkUpdateBuilder> {
  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'cause')
  String get cause;

  @BuiltValueField(wireName: r'result')
  String get result;

  @BuiltValueField(wireName: r'created_at')
  DateTime get createdAt;

  @BuiltValueField(wireName: r'photos')
  BuiltList<ReportWorkUpdatePhoto> get photos;

  ReportWorkUpdate._();

  factory ReportWorkUpdate([void updates(ReportWorkUpdateBuilder b)]) = _$ReportWorkUpdate;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ReportWorkUpdateBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ReportWorkUpdate> get serializer => _$ReportWorkUpdateSerializer();
}

class _$ReportWorkUpdateSerializer implements PrimitiveSerializer<ReportWorkUpdate> {
  @override
  final Iterable<Type> types = const [ReportWorkUpdate, _$ReportWorkUpdate];

  @override
  final String wireName = r'ReportWorkUpdate';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ReportWorkUpdate object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(int),
    );
    yield r'cause';
    yield serializers.serialize(
      object.cause,
      specifiedType: const FullType(String),
    );
    yield r'result';
    yield serializers.serialize(
      object.result,
      specifiedType: const FullType(String),
    );
    yield r'created_at';
    yield serializers.serialize(
      object.createdAt,
      specifiedType: const FullType(DateTime),
    );
    yield r'photos';
    yield serializers.serialize(
      object.photos,
      specifiedType: const FullType(BuiltList, [FullType(ReportWorkUpdatePhoto)]),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    ReportWorkUpdate object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ReportWorkUpdateBuilder result,
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
        case r'cause':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.cause = valueDes;
          break;
        case r'result':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.result = valueDes;
          break;
        case r'created_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.createdAt = valueDes;
          break;
        case r'photos':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(ReportWorkUpdatePhoto)]),
          ) as BuiltList<ReportWorkUpdatePhoto>;
          result.photos.replace(valueDes);
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  ReportWorkUpdate deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ReportWorkUpdateBuilder();
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
