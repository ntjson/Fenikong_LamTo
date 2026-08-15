//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'proof_event.g.dart';

/// ProofEvent
///
/// Properties:
/// * [eventId]
/// * [eventType]
/// * [status]
/// * [evidenceLevel]
/// * [transactionHash]
@BuiltValue()
abstract class ProofEvent implements Built<ProofEvent, ProofEventBuilder> {
  @BuiltValueField(wireName: r'event_id')
  String get eventId;

  @BuiltValueField(wireName: r'event_type')
  int get eventType;

  @BuiltValueField(wireName: r'status')
  String get status;

  @BuiltValueField(wireName: r'evidence_level')
  String get evidenceLevel;

  @BuiltValueField(wireName: r'transaction_hash')
  String get transactionHash;

  ProofEvent._();

  factory ProofEvent([void updates(ProofEventBuilder b)]) = _$ProofEvent;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ProofEventBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ProofEvent> get serializer => _$ProofEventSerializer();
}

class _$ProofEventSerializer implements PrimitiveSerializer<ProofEvent> {
  @override
  final Iterable<Type> types = const [ProofEvent, _$ProofEvent];

  @override
  final String wireName = r'ProofEvent';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ProofEvent object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'event_id';
    yield serializers.serialize(
      object.eventId,
      specifiedType: const FullType(String),
    );
    yield r'event_type';
    yield serializers.serialize(
      object.eventType,
      specifiedType: const FullType(int),
    );
    yield r'status';
    yield serializers.serialize(
      object.status,
      specifiedType: const FullType(String),
    );
    yield r'evidence_level';
    yield serializers.serialize(
      object.evidenceLevel,
      specifiedType: const FullType(String),
    );
    yield r'transaction_hash';
    yield serializers.serialize(
      object.transactionHash,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    ProofEvent object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ProofEventBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'event_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.eventId = valueDes;
          break;
        case r'event_type':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.eventType = valueDes;
          break;
        case r'status':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.status = valueDes;
          break;
        case r'evidence_level':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.evidenceLevel = valueDes;
          break;
        case r'transaction_hash':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.transactionHash = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  ProofEvent deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ProofEventBuilder();
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
