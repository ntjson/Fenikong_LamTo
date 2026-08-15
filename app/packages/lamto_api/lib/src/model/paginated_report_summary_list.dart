//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:lamto_api/src/model/report_summary.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'paginated_report_summary_list.g.dart';

/// PaginatedReportSummaryList
///
/// Properties:
/// * [next]
/// * [previous]
/// * [results]
@BuiltValue()
abstract class PaginatedReportSummaryList implements Built<PaginatedReportSummaryList, PaginatedReportSummaryListBuilder> {
  @BuiltValueField(wireName: r'next')
  String? get next;

  @BuiltValueField(wireName: r'previous')
  String? get previous;

  @BuiltValueField(wireName: r'results')
  BuiltList<ReportSummary> get results;

  PaginatedReportSummaryList._();

  factory PaginatedReportSummaryList([void updates(PaginatedReportSummaryListBuilder b)]) = _$PaginatedReportSummaryList;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(PaginatedReportSummaryListBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<PaginatedReportSummaryList> get serializer => _$PaginatedReportSummaryListSerializer();
}

class _$PaginatedReportSummaryListSerializer implements PrimitiveSerializer<PaginatedReportSummaryList> {
  @override
  final Iterable<Type> types = const [PaginatedReportSummaryList, _$PaginatedReportSummaryList];

  @override
  final String wireName = r'PaginatedReportSummaryList';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    PaginatedReportSummaryList object, {
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
      specifiedType: const FullType(BuiltList, [FullType(ReportSummary)]),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    PaginatedReportSummaryList object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required PaginatedReportSummaryListBuilder result,
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
            specifiedType: const FullType(BuiltList, [FullType(ReportSummary)]),
          ) as BuiltList<ReportSummary>;
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
  PaginatedReportSummaryList deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = PaginatedReportSummaryListBuilder();
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
