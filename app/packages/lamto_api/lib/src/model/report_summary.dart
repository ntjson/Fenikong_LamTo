//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:lamto_api/src/model/status_enum.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'report_summary.g.dart';

/// ReportSummary
///
/// Properties:
/// * [id]
/// * [text]
/// * [status]
/// * [isPrivate]
/// * [locationPathSnapshot]
/// * [createdAt]
@BuiltValue()
abstract class ReportSummary implements Built<ReportSummary, ReportSummaryBuilder> {
  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'text')
  String get text;

  @BuiltValueField(wireName: r'status')
  StatusEnum get status;
  // enum statusEnum {  SUBMITTED,  IN_REVIEW,  NEEDS_INFO,  DECLINED,  IN_PROGRESS,  PROPOSED,  COMPLETED,  CLOSED,  };

  @BuiltValueField(wireName: r'is_private')
  bool get isPrivate;

  @BuiltValueField(wireName: r'location_path_snapshot')
  String get locationPathSnapshot;

  @BuiltValueField(wireName: r'created_at')
  DateTime get createdAt;

  ReportSummary._();

  factory ReportSummary([void updates(ReportSummaryBuilder b)]) = _$ReportSummary;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ReportSummaryBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ReportSummary> get serializer => _$ReportSummarySerializer();
}

class _$ReportSummarySerializer implements PrimitiveSerializer<ReportSummary> {
  @override
  final Iterable<Type> types = const [ReportSummary, _$ReportSummary];

  @override
  final String wireName = r'ReportSummary';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ReportSummary object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(int),
    );
    yield r'text';
    yield serializers.serialize(
      object.text,
      specifiedType: const FullType(String),
    );
    yield r'status';
    yield serializers.serialize(
      object.status,
      specifiedType: const FullType(StatusEnum),
    );
    yield r'is_private';
    yield serializers.serialize(
      object.isPrivate,
      specifiedType: const FullType(bool),
    );
    yield r'location_path_snapshot';
    yield serializers.serialize(
      object.locationPathSnapshot,
      specifiedType: const FullType(String),
    );
    yield r'created_at';
    yield serializers.serialize(
      object.createdAt,
      specifiedType: const FullType(DateTime),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    ReportSummary object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ReportSummaryBuilder result,
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
        case r'text':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.text = valueDes;
          break;
        case r'status':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(StatusEnum),
          ) as StatusEnum;
          result.status = valueDes;
          break;
        case r'is_private':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.isPrivate = valueDes;
          break;
        case r'location_path_snapshot':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.locationPathSnapshot = valueDes;
          break;
        case r'created_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.createdAt = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  ReportSummary deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ReportSummaryBuilder();
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
