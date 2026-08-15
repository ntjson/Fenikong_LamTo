//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'info_reply_request.g.dart';

/// InfoReplyRequest
///
/// Properties:
/// * [text]
@BuiltValue()
abstract class InfoReplyRequest implements Built<InfoReplyRequest, InfoReplyRequestBuilder> {
  @BuiltValueField(wireName: r'text')
  String get text;

  InfoReplyRequest._();

  factory InfoReplyRequest([void updates(InfoReplyRequestBuilder b)]) = _$InfoReplyRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(InfoReplyRequestBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<InfoReplyRequest> get serializer => _$InfoReplyRequestSerializer();
}

class _$InfoReplyRequestSerializer implements PrimitiveSerializer<InfoReplyRequest> {
  @override
  final Iterable<Type> types = const [InfoReplyRequest, _$InfoReplyRequest];

  @override
  final String wireName = r'InfoReplyRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    InfoReplyRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'text';
    yield serializers.serialize(
      object.text,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    InfoReplyRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required InfoReplyRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'text':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.text = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  InfoReplyRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = InfoReplyRequestBuilder();
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
