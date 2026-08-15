//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:lamto_api/src/model/kind_enum.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'report_work_update_photo.g.dart';

/// ReportWorkUpdatePhoto
///
/// Properties:
/// * [id]
/// * [filename]
/// * [kind]
/// * [downloadUrl]
@BuiltValue()
abstract class ReportWorkUpdatePhoto implements Built<ReportWorkUpdatePhoto, ReportWorkUpdatePhotoBuilder> {
  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'filename')
  String get filename;

  @BuiltValueField(wireName: r'kind')
  KindEnum get kind;
  // enum kindEnum {  BEFORE,  AFTER,  };

  @BuiltValueField(wireName: r'download_url')
  String get downloadUrl;

  ReportWorkUpdatePhoto._();

  factory ReportWorkUpdatePhoto([void updates(ReportWorkUpdatePhotoBuilder b)]) = _$ReportWorkUpdatePhoto;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ReportWorkUpdatePhotoBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ReportWorkUpdatePhoto> get serializer => _$ReportWorkUpdatePhotoSerializer();
}

class _$ReportWorkUpdatePhotoSerializer implements PrimitiveSerializer<ReportWorkUpdatePhoto> {
  @override
  final Iterable<Type> types = const [ReportWorkUpdatePhoto, _$ReportWorkUpdatePhoto];

  @override
  final String wireName = r'ReportWorkUpdatePhoto';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ReportWorkUpdatePhoto object, {
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
    yield r'kind';
    yield serializers.serialize(
      object.kind,
      specifiedType: const FullType(KindEnum),
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
    ReportWorkUpdatePhoto object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ReportWorkUpdatePhotoBuilder result,
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
        case r'kind':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(KindEnum),
          ) as KindEnum;
          result.kind = valueDes;
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
  ReportWorkUpdatePhoto deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ReportWorkUpdatePhotoBuilder();
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
