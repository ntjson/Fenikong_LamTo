//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:lamto_api/src/model/verification.dart';
import 'package:built_collection/built_collection.dart';
import 'package:lamto_api/src/model/proof.dart';
import 'package:built_value/json_object.dart';
import 'package:lamto_api/src/model/ledger_document.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'ledger_entry_detail.g.dart';

/// LedgerEntryDetail
///
/// Properties:
/// * [id]
/// * [contractorName]
/// * [actualCostVnd]
/// * [publishedAt]
/// * [proposedAmountVnd]
/// * [integrityStatus]
/// * [whatWasFixed] - Resident-visible narrative of work completed.
/// * [why] - Resident-visible rationale (cause or purpose).
/// * [payload]
/// * [verification]
/// * [approvers]
/// * [corrections]
/// * [documents]
/// * [proof]
@BuiltValue()
abstract class LedgerEntryDetail implements Built<LedgerEntryDetail, LedgerEntryDetailBuilder> {
  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'contractor_name')
  String get contractorName;

  @BuiltValueField(wireName: r'actual_cost_vnd')
  int get actualCostVnd;

  @BuiltValueField(wireName: r'published_at')
  DateTime get publishedAt;

  @BuiltValueField(wireName: r'proposed_amount_vnd')
  int? get proposedAmountVnd;

  @BuiltValueField(wireName: r'integrity_status')
  String get integrityStatus;

  /// Resident-visible narrative of work completed.
  @BuiltValueField(wireName: r'what_was_fixed')
  String get whatWasFixed;

  /// Resident-visible rationale (cause or purpose).
  @BuiltValueField(wireName: r'why')
  String get why;

  @BuiltValueField(wireName: r'payload')
  JsonObject? get payload;

  @BuiltValueField(wireName: r'verification')
  Verification? get verification;

  @BuiltValueField(wireName: r'approvers')
  BuiltList<JsonObject?> get approvers;

  @BuiltValueField(wireName: r'corrections')
  BuiltList<JsonObject?> get corrections;

  @BuiltValueField(wireName: r'documents')
  BuiltList<LedgerDocument> get documents;

  @BuiltValueField(wireName: r'proof')
  Proof get proof;

  LedgerEntryDetail._();

  factory LedgerEntryDetail([void updates(LedgerEntryDetailBuilder b)]) = _$LedgerEntryDetail;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(LedgerEntryDetailBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<LedgerEntryDetail> get serializer => _$LedgerEntryDetailSerializer();
}

class _$LedgerEntryDetailSerializer implements PrimitiveSerializer<LedgerEntryDetail> {
  @override
  final Iterable<Type> types = const [LedgerEntryDetail, _$LedgerEntryDetail];

  @override
  final String wireName = r'LedgerEntryDetail';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    LedgerEntryDetail object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(int),
    );
    yield r'contractor_name';
    yield serializers.serialize(
      object.contractorName,
      specifiedType: const FullType(String),
    );
    yield r'actual_cost_vnd';
    yield serializers.serialize(
      object.actualCostVnd,
      specifiedType: const FullType(int),
    );
    yield r'published_at';
    yield serializers.serialize(
      object.publishedAt,
      specifiedType: const FullType(DateTime),
    );
    yield r'proposed_amount_vnd';
    yield object.proposedAmountVnd == null ? null : serializers.serialize(
      object.proposedAmountVnd,
      specifiedType: const FullType.nullable(int),
    );
    yield r'integrity_status';
    yield serializers.serialize(
      object.integrityStatus,
      specifiedType: const FullType(String),
    );
    yield r'what_was_fixed';
    yield serializers.serialize(
      object.whatWasFixed,
      specifiedType: const FullType(String),
    );
    yield r'why';
    yield serializers.serialize(
      object.why,
      specifiedType: const FullType(String),
    );
    yield r'payload';
    yield object.payload == null ? null : serializers.serialize(
      object.payload,
      specifiedType: const FullType.nullable(JsonObject),
    );
    yield r'verification';
    yield object.verification == null ? null : serializers.serialize(
      object.verification,
      specifiedType: const FullType.nullable(Verification),
    );
    yield r'approvers';
    yield serializers.serialize(
      object.approvers,
      specifiedType: const FullType(BuiltList, [FullType.nullable(JsonObject)]),
    );
    yield r'corrections';
    yield serializers.serialize(
      object.corrections,
      specifiedType: const FullType(BuiltList, [FullType.nullable(JsonObject)]),
    );
    yield r'documents';
    yield serializers.serialize(
      object.documents,
      specifiedType: const FullType(BuiltList, [FullType(LedgerDocument)]),
    );
    yield r'proof';
    yield serializers.serialize(
      object.proof,
      specifiedType: const FullType(Proof),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    LedgerEntryDetail object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required LedgerEntryDetailBuilder result,
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
        case r'contractor_name':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.contractorName = valueDes;
          break;
        case r'actual_cost_vnd':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.actualCostVnd = valueDes;
          break;
        case r'published_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.publishedAt = valueDes;
          break;
        case r'proposed_amount_vnd':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(int),
          ) as int?;
          if (valueDes == null) continue;
          result.proposedAmountVnd = valueDes;
          break;
        case r'integrity_status':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.integrityStatus = valueDes;
          break;
        case r'what_was_fixed':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.whatWasFixed = valueDes;
          break;
        case r'why':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.why = valueDes;
          break;
        case r'payload':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(JsonObject),
          ) as JsonObject?;
          if (valueDes == null) continue;
          result.payload = valueDes;
          break;
        case r'verification':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(Verification),
          ) as Verification?;
          if (valueDes == null) continue;
          result.verification.replace(valueDes);
          break;
        case r'approvers':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType.nullable(JsonObject)]),
          ) as BuiltList<JsonObject?>;
          result.approvers.replace(valueDes);
          break;
        case r'corrections':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType.nullable(JsonObject)]),
          ) as BuiltList<JsonObject?>;
          result.corrections.replace(valueDes);
          break;
        case r'documents':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(LedgerDocument)]),
          ) as BuiltList<LedgerDocument>;
          result.documents.replace(valueDes);
          break;
        case r'proof':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(Proof),
          ) as Proof;
          result.proof.replace(valueDes);
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  LedgerEntryDetail deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = LedgerEntryDetailBuilder();
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
