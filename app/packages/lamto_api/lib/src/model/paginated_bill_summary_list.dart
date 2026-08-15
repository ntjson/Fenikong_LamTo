//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:lamto_api/src/model/bill_summary.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'paginated_bill_summary_list.g.dart';

/// PaginatedBillSummaryList
///
/// Properties:
/// * [next]
/// * [previous]
/// * [results]
@BuiltValue()
abstract class PaginatedBillSummaryList implements Built<PaginatedBillSummaryList, PaginatedBillSummaryListBuilder> {
  @BuiltValueField(wireName: r'next')
  String? get next;

  @BuiltValueField(wireName: r'previous')
  String? get previous;

  @BuiltValueField(wireName: r'results')
  BuiltList<BillSummary> get results;

  PaginatedBillSummaryList._();

  factory PaginatedBillSummaryList([void updates(PaginatedBillSummaryListBuilder b)]) = _$PaginatedBillSummaryList;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(PaginatedBillSummaryListBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<PaginatedBillSummaryList> get serializer => _$PaginatedBillSummaryListSerializer();
}

class _$PaginatedBillSummaryListSerializer implements PrimitiveSerializer<PaginatedBillSummaryList> {
  @override
  final Iterable<Type> types = const [PaginatedBillSummaryList, _$PaginatedBillSummaryList];

  @override
  final String wireName = r'PaginatedBillSummaryList';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    PaginatedBillSummaryList object, {
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
      specifiedType: const FullType(BuiltList, [FullType(BillSummary)]),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    PaginatedBillSummaryList object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required PaginatedBillSummaryListBuilder result,
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
            specifiedType: const FullType(BuiltList, [FullType(BillSummary)]),
          ) as BuiltList<BillSummary>;
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
  PaginatedBillSummaryList deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = PaginatedBillSummaryListBuilder();
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
