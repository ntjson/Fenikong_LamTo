//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:lamto_api/src/model/proposal.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'paginated_proposal_list.g.dart';

/// PaginatedProposalList
///
/// Properties:
/// * [next]
/// * [previous]
/// * [results]
@BuiltValue()
abstract class PaginatedProposalList implements Built<PaginatedProposalList, PaginatedProposalListBuilder> {
  @BuiltValueField(wireName: r'next')
  String? get next;

  @BuiltValueField(wireName: r'previous')
  String? get previous;

  @BuiltValueField(wireName: r'results')
  BuiltList<Proposal> get results;

  PaginatedProposalList._();

  factory PaginatedProposalList([void updates(PaginatedProposalListBuilder b)]) = _$PaginatedProposalList;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(PaginatedProposalListBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<PaginatedProposalList> get serializer => _$PaginatedProposalListSerializer();
}

class _$PaginatedProposalListSerializer implements PrimitiveSerializer<PaginatedProposalList> {
  @override
  final Iterable<Type> types = const [PaginatedProposalList, _$PaginatedProposalList];

  @override
  final String wireName = r'PaginatedProposalList';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    PaginatedProposalList object, {
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
      specifiedType: const FullType(BuiltList, [FullType(Proposal)]),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    PaginatedProposalList object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required PaginatedProposalListBuilder result,
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
            specifiedType: const FullType(BuiltList, [FullType(Proposal)]),
          ) as BuiltList<Proposal>;
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
  PaginatedProposalList deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = PaginatedProposalListBuilder();
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
