//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'bill_confirm_payment_request_request.g.dart';

/// BillConfirmPaymentRequestRequest
///
/// Properties:
/// * [reference]
@BuiltValue()
abstract class BillConfirmPaymentRequestRequest implements Built<BillConfirmPaymentRequestRequest, BillConfirmPaymentRequestRequestBuilder> {
  @BuiltValueField(wireName: r'reference')
  String get reference;

  BillConfirmPaymentRequestRequest._();

  factory BillConfirmPaymentRequestRequest([void updates(BillConfirmPaymentRequestRequestBuilder b)]) = _$BillConfirmPaymentRequestRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(BillConfirmPaymentRequestRequestBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<BillConfirmPaymentRequestRequest> get serializer => _$BillConfirmPaymentRequestRequestSerializer();
}

class _$BillConfirmPaymentRequestRequestSerializer implements PrimitiveSerializer<BillConfirmPaymentRequestRequest> {
  @override
  final Iterable<Type> types = const [BillConfirmPaymentRequestRequest, _$BillConfirmPaymentRequestRequest];

  @override
  final String wireName = r'BillConfirmPaymentRequestRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    BillConfirmPaymentRequestRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'reference';
    yield serializers.serialize(
      object.reference,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    BillConfirmPaymentRequestRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required BillConfirmPaymentRequestRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'reference':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.reference = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  BillConfirmPaymentRequestRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = BillConfirmPaymentRequestRequestBuilder();
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
