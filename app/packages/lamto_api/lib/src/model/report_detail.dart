//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:lamto_api/src/model/report_case.dart';
import 'package:lamto_api/src/model/report_photo.dart';
import 'package:built_value/json_object.dart';
import 'package:lamto_api/src/model/status_enum.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'report_detail.g.dart';

/// ReportDetail
///
/// Properties:
/// * [id]
/// * [text]
/// * [status]
/// * [declinedReason]
/// * [isPrivate]
/// * [openInfoRequest]
/// * [locationPathSnapshot]
/// * [unitLabel]
/// * [createdAt]
/// * [triageStatus]
/// * [category]
/// * [photos]
/// * [cases]
/// * [ledgerEntryIds]
@BuiltValue()
abstract class ReportDetail implements Built<ReportDetail, ReportDetailBuilder> {
  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'text')
  String get text;

  @BuiltValueField(wireName: r'status')
  StatusEnum get status;
  // enum statusEnum {  SUBMITTED,  IN_REVIEW,  NEEDS_INFO,  DECLINED,  IN_PROGRESS,  PROPOSED,  COMPLETED,  CLOSED,  };

  @BuiltValueField(wireName: r'declined_reason')
  String? get declinedReason;

  @BuiltValueField(wireName: r'is_private')
  bool get isPrivate;

  @BuiltValueField(wireName: r'open_info_request')
  BuiltMap<String, JsonObject?>? get openInfoRequest;

  @BuiltValueField(wireName: r'location_path_snapshot')
  String get locationPathSnapshot;

  @BuiltValueField(wireName: r'unit_label')
  String get unitLabel;

  @BuiltValueField(wireName: r'created_at')
  DateTime get createdAt;

  @BuiltValueField(wireName: r'triage_status')
  String? get triageStatus;

  @BuiltValueField(wireName: r'category')
  String? get category;

  @BuiltValueField(wireName: r'photos')
  BuiltList<ReportPhoto> get photos;

  @BuiltValueField(wireName: r'cases')
  BuiltList<ReportCase> get cases;

  @BuiltValueField(wireName: r'ledger_entry_ids')
  BuiltList<int> get ledgerEntryIds;

  ReportDetail._();

  factory ReportDetail([void updates(ReportDetailBuilder b)]) = _$ReportDetail;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ReportDetailBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ReportDetail> get serializer => _$ReportDetailSerializer();
}

class _$ReportDetailSerializer implements PrimitiveSerializer<ReportDetail> {
  @override
  final Iterable<Type> types = const [ReportDetail, _$ReportDetail];

  @override
  final String wireName = r'ReportDetail';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ReportDetail object, {
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
    yield r'declined_reason';
    yield object.declinedReason == null ? null : serializers.serialize(
      object.declinedReason,
      specifiedType: const FullType.nullable(String),
    );
    yield r'is_private';
    yield serializers.serialize(
      object.isPrivate,
      specifiedType: const FullType(bool),
    );
    yield r'open_info_request';
    yield object.openInfoRequest == null ? null : serializers.serialize(
      object.openInfoRequest,
      specifiedType: const FullType.nullable(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
    );
    yield r'location_path_snapshot';
    yield serializers.serialize(
      object.locationPathSnapshot,
      specifiedType: const FullType(String),
    );
    yield r'unit_label';
    yield serializers.serialize(
      object.unitLabel,
      specifiedType: const FullType(String),
    );
    yield r'created_at';
    yield serializers.serialize(
      object.createdAt,
      specifiedType: const FullType(DateTime),
    );
    yield r'triage_status';
    yield object.triageStatus == null ? null : serializers.serialize(
      object.triageStatus,
      specifiedType: const FullType.nullable(String),
    );
    yield r'category';
    yield object.category == null ? null : serializers.serialize(
      object.category,
      specifiedType: const FullType.nullable(String),
    );
    yield r'photos';
    yield serializers.serialize(
      object.photos,
      specifiedType: const FullType(BuiltList, [FullType(ReportPhoto)]),
    );
    yield r'cases';
    yield serializers.serialize(
      object.cases,
      specifiedType: const FullType(BuiltList, [FullType(ReportCase)]),
    );
    yield r'ledger_entry_ids';
    yield serializers.serialize(
      object.ledgerEntryIds,
      specifiedType: const FullType(BuiltList, [FullType(int)]),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    ReportDetail object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ReportDetailBuilder result,
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
        case r'declined_reason':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.declinedReason = valueDes;
          break;
        case r'is_private':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.isPrivate = valueDes;
          break;
        case r'open_info_request':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
          ) as BuiltMap<String, JsonObject?>?;
          if (valueDes == null) continue;
          result.openInfoRequest.replace(valueDes);
          break;
        case r'location_path_snapshot':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.locationPathSnapshot = valueDes;
          break;
        case r'unit_label':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.unitLabel = valueDes;
          break;
        case r'created_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.createdAt = valueDes;
          break;
        case r'triage_status':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.triageStatus = valueDes;
          break;
        case r'category':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.category = valueDes;
          break;
        case r'photos':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(ReportPhoto)]),
          ) as BuiltList<ReportPhoto>;
          result.photos.replace(valueDes);
          break;
        case r'cases':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(ReportCase)]),
          ) as BuiltList<ReportCase>;
          result.cases.replace(valueDes);
          break;
        case r'ledger_entry_ids':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(int)]),
          ) as BuiltList<int>;
          result.ledgerEntryIds.replace(valueDes);
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  ReportDetail deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ReportDetailBuilder();
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
