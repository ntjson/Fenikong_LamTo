//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'ledger_document.g.dart';

/// LedgerDocument
///
/// Properties:
/// * [label]
/// * [filename]
/// * [sha256]
/// * [downloadUrl]
@BuiltValue()
abstract class LedgerDocument implements Built<LedgerDocument, LedgerDocumentBuilder> {
  @BuiltValueField(wireName: r'label')
  String get label;

  @BuiltValueField(wireName: r'filename')
  String get filename;

  @BuiltValueField(wireName: r'sha256')
  String get sha256;

  @BuiltValueField(wireName: r'download_url')
  String get downloadUrl;

  LedgerDocument._();

  factory LedgerDocument([void updates(LedgerDocumentBuilder b)]) = _$LedgerDocument;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(LedgerDocumentBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<LedgerDocument> get serializer => _$LedgerDocumentSerializer();
}

class _$LedgerDocumentSerializer implements PrimitiveSerializer<LedgerDocument> {
  @override
  final Iterable<Type> types = const [LedgerDocument, _$LedgerDocument];

  @override
  final String wireName = r'LedgerDocument';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    LedgerDocument object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'label';
    yield serializers.serialize(
      object.label,
      specifiedType: const FullType(String),
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
    LedgerDocument object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required LedgerDocumentBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'label':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.label = valueDes;
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
  LedgerDocument deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = LedgerDocumentBuilder();
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
