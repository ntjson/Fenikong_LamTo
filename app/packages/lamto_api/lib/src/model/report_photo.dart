//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'report_photo.g.dart';

/// ReportPhoto
///
/// Properties:
/// * [id]
/// * [filename]
/// * [sha256]
/// * [downloadUrl]
@BuiltValue()
abstract class ReportPhoto implements Built<ReportPhoto, ReportPhotoBuilder> {
  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'filename')
  String get filename;

  @BuiltValueField(wireName: r'sha256')
  String get sha256;

  @BuiltValueField(wireName: r'download_url')
  String get downloadUrl;

  ReportPhoto._();

  factory ReportPhoto([void updates(ReportPhotoBuilder b)]) = _$ReportPhoto;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ReportPhotoBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ReportPhoto> get serializer => _$ReportPhotoSerializer();
}

class _$ReportPhotoSerializer implements PrimitiveSerializer<ReportPhoto> {
  @override
  final Iterable<Type> types = const [ReportPhoto, _$ReportPhoto];

  @override
  final String wireName = r'ReportPhoto';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ReportPhoto object, {
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
    ReportPhoto object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ReportPhotoBuilder result,
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
  ReportPhoto deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ReportPhotoBuilder();
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
