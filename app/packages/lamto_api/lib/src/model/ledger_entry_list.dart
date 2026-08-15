//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'ledger_entry_list.g.dart';

/// LedgerEntryList
///
/// Properties:
/// * [id]
/// * [contractorName]
/// * [actualCostVnd]
/// * [publishedAt]
/// * [integrityStatus]
/// * [evidenceLevel]
/// * [whatWasFixed] - Resident-visible narrative of work completed.
@BuiltValue()
abstract class LedgerEntryList implements Built<LedgerEntryList, LedgerEntryListBuilder> {
  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'contractor_name')
  String get contractorName;

  @BuiltValueField(wireName: r'actual_cost_vnd')
  int get actualCostVnd;

  @BuiltValueField(wireName: r'published_at')
  DateTime get publishedAt;

  @BuiltValueField(wireName: r'integrity_status')
  String get integrityStatus;

  @BuiltValueField(wireName: r'evidence_level')
  String get evidenceLevel;

  /// Resident-visible narrative of work completed.
  @BuiltValueField(wireName: r'what_was_fixed')
  String get whatWasFixed;

  LedgerEntryList._();

  factory LedgerEntryList([void updates(LedgerEntryListBuilder b)]) = _$LedgerEntryList;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(LedgerEntryListBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<LedgerEntryList> get serializer => _$LedgerEntryListSerializer();
}

class _$LedgerEntryListSerializer implements PrimitiveSerializer<LedgerEntryList> {
  @override
  final Iterable<Type> types = const [LedgerEntryList, _$LedgerEntryList];

  @override
  final String wireName = r'LedgerEntryList';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    LedgerEntryList object, {
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
    yield r'integrity_status';
    yield serializers.serialize(
      object.integrityStatus,
      specifiedType: const FullType(String),
    );
    yield r'evidence_level';
    yield serializers.serialize(
      object.evidenceLevel,
      specifiedType: const FullType(String),
    );
    yield r'what_was_fixed';
    yield serializers.serialize(
      object.whatWasFixed,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    LedgerEntryList object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required LedgerEntryListBuilder result,
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
        case r'integrity_status':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.integrityStatus = valueDes;
          break;
        case r'evidence_level':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.evidenceLevel = valueDes;
          break;
        case r'what_was_fixed':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.whatWasFixed = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  LedgerEntryList deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = LedgerEntryListBuilder();
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
