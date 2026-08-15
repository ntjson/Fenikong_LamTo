//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:lamto_api/src/model/proposal_version.dart';
import 'package:built_collection/built_collection.dart';
import 'package:lamto_api/src/model/proposal_progress.dart';
import 'package:lamto_api/src/model/proposal_settlement.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'proposal.g.dart';

/// Proposal
///
/// Properties:
/// * [id]
/// * [caseId]
/// * [buildingId]
/// * [status]
/// * [completedAt]
/// * [closedAt]
/// * [purpose]
/// * [proposedAction]
/// * [amountVnd]
/// * [fundCode]
/// * [contractorName]
/// * [expectedSchedule]
/// * [versions]
/// * [progress]
/// * [settlement]
/// * [canRate]
@BuiltValue()
abstract class Proposal implements Built<Proposal, ProposalBuilder> {
  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'case_id')
  int? get caseId;

  @BuiltValueField(wireName: r'building_id')
  int get buildingId;

  @BuiltValueField(wireName: r'status')
  String get status;

  @BuiltValueField(wireName: r'completed_at')
  DateTime? get completedAt;

  @BuiltValueField(wireName: r'closed_at')
  DateTime? get closedAt;

  @BuiltValueField(wireName: r'purpose')
  String get purpose;

  @BuiltValueField(wireName: r'proposed_action')
  String get proposedAction;

  @BuiltValueField(wireName: r'amount_vnd')
  int get amountVnd;

  @BuiltValueField(wireName: r'fund_code')
  String get fundCode;

  @BuiltValueField(wireName: r'contractor_name')
  String get contractorName;

  @BuiltValueField(wireName: r'expected_schedule')
  String get expectedSchedule;

  @BuiltValueField(wireName: r'versions')
  BuiltList<ProposalVersion> get versions;

  @BuiltValueField(wireName: r'progress')
  BuiltList<ProposalProgress> get progress;

  @BuiltValueField(wireName: r'settlement')
  ProposalSettlement? get settlement;

  @BuiltValueField(wireName: r'can_rate')
  bool get canRate;

  Proposal._();

  factory Proposal([void updates(ProposalBuilder b)]) = _$Proposal;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ProposalBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<Proposal> get serializer => _$ProposalSerializer();
}

class _$ProposalSerializer implements PrimitiveSerializer<Proposal> {
  @override
  final Iterable<Type> types = const [Proposal, _$Proposal];

  @override
  final String wireName = r'Proposal';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    Proposal object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(int),
    );
    yield r'case_id';
    yield object.caseId == null ? null : serializers.serialize(
      object.caseId,
      specifiedType: const FullType.nullable(int),
    );
    yield r'building_id';
    yield serializers.serialize(
      object.buildingId,
      specifiedType: const FullType(int),
    );
    yield r'status';
    yield serializers.serialize(
      object.status,
      specifiedType: const FullType(String),
    );
    yield r'completed_at';
    yield object.completedAt == null ? null : serializers.serialize(
      object.completedAt,
      specifiedType: const FullType.nullable(DateTime),
    );
    yield r'closed_at';
    yield object.closedAt == null ? null : serializers.serialize(
      object.closedAt,
      specifiedType: const FullType.nullable(DateTime),
    );
    yield r'purpose';
    yield serializers.serialize(
      object.purpose,
      specifiedType: const FullType(String),
    );
    yield r'proposed_action';
    yield serializers.serialize(
      object.proposedAction,
      specifiedType: const FullType(String),
    );
    yield r'amount_vnd';
    yield serializers.serialize(
      object.amountVnd,
      specifiedType: const FullType(int),
    );
    yield r'fund_code';
    yield serializers.serialize(
      object.fundCode,
      specifiedType: const FullType(String),
    );
    yield r'contractor_name';
    yield serializers.serialize(
      object.contractorName,
      specifiedType: const FullType(String),
    );
    yield r'expected_schedule';
    yield serializers.serialize(
      object.expectedSchedule,
      specifiedType: const FullType(String),
    );
    yield r'versions';
    yield serializers.serialize(
      object.versions,
      specifiedType: const FullType(BuiltList, [FullType(ProposalVersion)]),
    );
    yield r'progress';
    yield serializers.serialize(
      object.progress,
      specifiedType: const FullType(BuiltList, [FullType(ProposalProgress)]),
    );
    yield r'settlement';
    yield object.settlement == null ? null : serializers.serialize(
      object.settlement,
      specifiedType: const FullType.nullable(ProposalSettlement),
    );
    yield r'can_rate';
    yield serializers.serialize(
      object.canRate,
      specifiedType: const FullType(bool),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    Proposal object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ProposalBuilder result,
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
        case r'case_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(int),
          ) as int?;
          if (valueDes == null) continue;
          result.caseId = valueDes;
          break;
        case r'building_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.buildingId = valueDes;
          break;
        case r'status':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.status = valueDes;
          break;
        case r'completed_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.completedAt = valueDes;
          break;
        case r'closed_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.closedAt = valueDes;
          break;
        case r'purpose':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.purpose = valueDes;
          break;
        case r'proposed_action':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.proposedAction = valueDes;
          break;
        case r'amount_vnd':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.amountVnd = valueDes;
          break;
        case r'fund_code':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.fundCode = valueDes;
          break;
        case r'contractor_name':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.contractorName = valueDes;
          break;
        case r'expected_schedule':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.expectedSchedule = valueDes;
          break;
        case r'versions':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(ProposalVersion)]),
          ) as BuiltList<ProposalVersion>;
          result.versions.replace(valueDes);
          break;
        case r'progress':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(ProposalProgress)]),
          ) as BuiltList<ProposalProgress>;
          result.progress.replace(valueDes);
          break;
        case r'settlement':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(ProposalSettlement),
          ) as ProposalSettlement?;
          if (valueDes == null) continue;
          result.settlement.replace(valueDes);
          break;
        case r'can_rate':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.canRate = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  Proposal deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ProposalBuilder();
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
