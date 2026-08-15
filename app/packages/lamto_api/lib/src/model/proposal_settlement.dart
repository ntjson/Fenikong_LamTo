//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'proposal_settlement.g.dart';

/// ProposalSettlement
///
/// Properties:
/// * [amountVnd]
/// * [payeeName]
/// * [transferRecordedAt]
/// * [acknowledgedAt]
/// * [settledAt]
@BuiltValue()
abstract class ProposalSettlement implements Built<ProposalSettlement, ProposalSettlementBuilder> {
  @BuiltValueField(wireName: r'amount_vnd')
  int get amountVnd;

  @BuiltValueField(wireName: r'payee_name')
  String get payeeName;

  @BuiltValueField(wireName: r'transfer_recorded_at')
  DateTime get transferRecordedAt;

  @BuiltValueField(wireName: r'acknowledged_at')
  DateTime? get acknowledgedAt;

  @BuiltValueField(wireName: r'settled_at')
  DateTime? get settledAt;

  ProposalSettlement._();

  factory ProposalSettlement([void updates(ProposalSettlementBuilder b)]) = _$ProposalSettlement;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ProposalSettlementBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ProposalSettlement> get serializer => _$ProposalSettlementSerializer();
}

class _$ProposalSettlementSerializer implements PrimitiveSerializer<ProposalSettlement> {
  @override
  final Iterable<Type> types = const [ProposalSettlement, _$ProposalSettlement];

  @override
  final String wireName = r'ProposalSettlement';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ProposalSettlement object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'amount_vnd';
    yield serializers.serialize(
      object.amountVnd,
      specifiedType: const FullType(int),
    );
    yield r'payee_name';
    yield serializers.serialize(
      object.payeeName,
      specifiedType: const FullType(String),
    );
    yield r'transfer_recorded_at';
    yield serializers.serialize(
      object.transferRecordedAt,
      specifiedType: const FullType(DateTime),
    );
    yield r'acknowledged_at';
    yield object.acknowledgedAt == null ? null : serializers.serialize(
      object.acknowledgedAt,
      specifiedType: const FullType.nullable(DateTime),
    );
    yield r'settled_at';
    yield object.settledAt == null ? null : serializers.serialize(
      object.settledAt,
      specifiedType: const FullType.nullable(DateTime),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    ProposalSettlement object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ProposalSettlementBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'amount_vnd':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.amountVnd = valueDes;
          break;
        case r'payee_name':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.payeeName = valueDes;
          break;
        case r'transfer_recorded_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.transferRecordedAt = valueDes;
          break;
        case r'acknowledged_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.acknowledgedAt = valueDes;
          break;
        case r'settled_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.settledAt = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  ProposalSettlement deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ProposalSettlementBuilder();
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
