//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:lamto_api/src/model/ledger_entry_list.dart';
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'paginated_ledger_entry_list_list.g.dart';

/// PaginatedLedgerEntryListList
///
/// Properties:
/// * [next]
/// * [previous]
/// * [results]
@BuiltValue()
abstract class PaginatedLedgerEntryListList implements Built<PaginatedLedgerEntryListList, PaginatedLedgerEntryListListBuilder> {
  @BuiltValueField(wireName: r'next')
  String? get next;

  @BuiltValueField(wireName: r'previous')
  String? get previous;

  @BuiltValueField(wireName: r'results')
  BuiltList<LedgerEntryList> get results;

  PaginatedLedgerEntryListList._();

  factory PaginatedLedgerEntryListList([void updates(PaginatedLedgerEntryListListBuilder b)]) = _$PaginatedLedgerEntryListList;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(PaginatedLedgerEntryListListBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<PaginatedLedgerEntryListList> get serializer => _$PaginatedLedgerEntryListListSerializer();
}

class _$PaginatedLedgerEntryListListSerializer implements PrimitiveSerializer<PaginatedLedgerEntryListList> {
  @override
  final Iterable<Type> types = const [PaginatedLedgerEntryListList, _$PaginatedLedgerEntryListList];

  @override
  final String wireName = r'PaginatedLedgerEntryListList';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    PaginatedLedgerEntryListList object, {
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
      specifiedType: const FullType(BuiltList, [FullType(LedgerEntryList)]),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    PaginatedLedgerEntryListList object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required PaginatedLedgerEntryListListBuilder result,
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
            specifiedType: const FullType(BuiltList, [FullType(LedgerEntryList)]),
          ) as BuiltList<LedgerEntryList>;
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
  PaginatedLedgerEntryListList deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = PaginatedLedgerEntryListListBuilder();
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
