//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'proposal_supporting_document.g.dart';

/// ProposalSupportingDocument
///
/// Properties:
/// * [id]
/// * [filename]
/// * [sha256]
/// * [downloadUrl]
@BuiltValue()
abstract class ProposalSupportingDocument implements Built<ProposalSupportingDocument, ProposalSupportingDocumentBuilder> {
  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'filename')
  String get filename;

  @BuiltValueField(wireName: r'sha256')
  String get sha256;

  @BuiltValueField(wireName: r'download_url')
  String get downloadUrl;

  ProposalSupportingDocument._();

  factory ProposalSupportingDocument([void updates(ProposalSupportingDocumentBuilder b)]) = _$ProposalSupportingDocument;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ProposalSupportingDocumentBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ProposalSupportingDocument> get serializer => _$ProposalSupportingDocumentSerializer();
}

class _$ProposalSupportingDocumentSerializer implements PrimitiveSerializer<ProposalSupportingDocument> {
  @override
  final Iterable<Type> types = const [ProposalSupportingDocument, _$ProposalSupportingDocument];

  @override
  final String wireName = r'ProposalSupportingDocument';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ProposalSupportingDocument object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(int),
    );
    yield r'filename';
    yield serializers.serialize(
      object.filename,
      specifiedType: const FullType(String),
    );
    yield r'sha256';
    yield serializers.serialize(
      object.sha256,
      specifiedType: const FullType(String),
    );
    yield r'download_url';
    yield serializers.serialize(
      object.downloadUrl,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    ProposalSupportingDocument object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ProposalSupportingDocumentBuilder result,
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
        case r'filename':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.filename = valueDes;
          break;
        case r'sha256':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.sha256 = valueDes;
          break;
        case r'download_url':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.downloadUrl = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  ProposalSupportingDocument deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ProposalSupportingDocumentBuilder();
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
