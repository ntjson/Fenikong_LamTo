//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:lamto_api/src/model/proposal_supporting_document.dart';
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'proposal_version.g.dart';

/// ProposalVersion
///
/// Properties:
/// * [number]
/// * [publishedAt]
/// * [evidenceLevel]
/// * [supportingDocuments]
@BuiltValue()
abstract class ProposalVersion implements Built<ProposalVersion, ProposalVersionBuilder> {
  @BuiltValueField(wireName: r'number')
  int get number;

  @BuiltValueField(wireName: r'published_at')
  DateTime get publishedAt;

  @BuiltValueField(wireName: r'evidence_level')
  String get evidenceLevel;

  @BuiltValueField(wireName: r'supporting_documents')
  BuiltList<ProposalSupportingDocument> get supportingDocuments;

  ProposalVersion._();

  factory ProposalVersion([void updates(ProposalVersionBuilder b)]) = _$ProposalVersion;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ProposalVersionBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ProposalVersion> get serializer => _$ProposalVersionSerializer();
}

class _$ProposalVersionSerializer implements PrimitiveSerializer<ProposalVersion> {
  @override
  final Iterable<Type> types = const [ProposalVersion, _$ProposalVersion];

  @override
  final String wireName = r'ProposalVersion';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ProposalVersion object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'number';
    yield serializers.serialize(
      object.number,
      specifiedType: const FullType(int),
    );
    yield r'published_at';
    yield serializers.serialize(
      object.publishedAt,
      specifiedType: const FullType(DateTime),
    );
    yield r'evidence_level';
    yield serializers.serialize(
      object.evidenceLevel,
      specifiedType: const FullType(String),
    );
    yield r'supporting_documents';
    yield serializers.serialize(
      object.supportingDocuments,
      specifiedType: const FullType(BuiltList, [FullType(ProposalSupportingDocument)]),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    ProposalVersion object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ProposalVersionBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'number':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.number = valueDes;
          break;
        case r'published_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.publishedAt = valueDes;
          break;
        case r'evidence_level':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.evidenceLevel = valueDes;
          break;
        case r'supporting_documents':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(ProposalSupportingDocument)]),
          ) as BuiltList<ProposalSupportingDocument>;
          result.supportingDocuments.replace(valueDes);
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  ProposalVersion deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ProposalVersionBuilder();
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
