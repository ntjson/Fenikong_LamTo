//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:lamto_api/src/model/status_enum.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'info_reply_result.g.dart';

/// InfoReplyResult
///
/// Properties:
/// * [reportId]
/// * [status]
@BuiltValue()
abstract class InfoReplyResult implements Built<InfoReplyResult, InfoReplyResultBuilder> {
  @BuiltValueField(wireName: r'report_id')
  int get reportId;

  @BuiltValueField(wireName: r'status')
  StatusEnum get status;
  // enum statusEnum {  SUBMITTED,  IN_REVIEW,  NEEDS_INFO,  DECLINED,  IN_PROGRESS,  PROPOSED,  COMPLETED,  CLOSED,  };

  InfoReplyResult._();

  factory InfoReplyResult([void updates(InfoReplyResultBuilder b)]) = _$InfoReplyResult;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(InfoReplyResultBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<InfoReplyResult> get serializer => _$InfoReplyResultSerializer();
}

class _$InfoReplyResultSerializer implements PrimitiveSerializer<InfoReplyResult> {
  @override
  final Iterable<Type> types = const [InfoReplyResult, _$InfoReplyResult];

  @override
  final String wireName = r'InfoReplyResult';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    InfoReplyResult object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'report_id';
    yield serializers.serialize(
      object.reportId,
      specifiedType: const FullType(int),
    );
    yield r'status';
    yield serializers.serialize(
      object.status,
      specifiedType: const FullType(StatusEnum),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    InfoReplyResult object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required InfoReplyResultBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'report_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.reportId = valueDes;
          break;
        case r'status':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(StatusEnum),
          ) as StatusEnum;
          result.status = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  InfoReplyResult deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = InfoReplyResultBuilder();
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
