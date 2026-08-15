//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:lamto_api/src/model/proof_event.dart';
import 'package:built_value/json_object.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'proof.g.dart';

/// Proof
///
/// Properties:
/// * [evidenceLevel]
/// * [anchoringBackend]
/// * [payloadHash]
/// * [events]
/// * [proposalVersion]
/// * [settlement]
@BuiltValue()
abstract class Proof implements Built<Proof, ProofBuilder> {
  @BuiltValueField(wireName: r'evidence_level')
  String get evidenceLevel;

  @BuiltValueField(wireName: r'anchoring_backend')
  String get anchoringBackend;

  @BuiltValueField(wireName: r'payload_hash')
  String get payloadHash;

  @BuiltValueField(wireName: r'events')
  BuiltList<ProofEvent> get events;

  @BuiltValueField(wireName: r'proposal_version')
  JsonObject? get proposalVersion;

  @BuiltValueField(wireName: r'settlement')
  JsonObject? get settlement;

  Proof._();

  factory Proof([void updates(ProofBuilder b)]) = _$Proof;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ProofBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<Proof> get serializer => _$ProofSerializer();
}

class _$ProofSerializer implements PrimitiveSerializer<Proof> {
  @override
  final Iterable<Type> types = const [Proof, _$Proof];

  @override
  final String wireName = r'Proof';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    Proof object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'evidence_level';
    yield serializers.serialize(
      object.evidenceLevel,
      specifiedType: const FullType(String),
    );
    yield r'anchoring_backend';
    yield serializers.serialize(
      object.anchoringBackend,
      specifiedType: const FullType(String),
    );
    yield r'payload_hash';
    yield serializers.serialize(
      object.payloadHash,
      specifiedType: const FullType(String),
    );
    yield r'events';
    yield serializers.serialize(
      object.events,
      specifiedType: const FullType(BuiltList, [FullType(ProofEvent)]),
    );
    yield r'proposal_version';
    yield object.proposalVersion == null ? null : serializers.serialize(
      object.proposalVersion,
      specifiedType: const FullType.nullable(JsonObject),
    );
    yield r'settlement';
    yield object.settlement == null ? null : serializers.serialize(
      object.settlement,
      specifiedType: const FullType.nullable(JsonObject),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    Proof object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ProofBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'evidence_level':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.evidenceLevel = valueDes;
          break;
        case r'anchoring_backend':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.anchoringBackend = valueDes;
          break;
        case r'payload_hash':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.payloadHash = valueDes;
          break;
        case r'events':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(ProofEvent)]),
          ) as BuiltList<ProofEvent>;
          result.events.replace(valueDes);
          break;
        case r'proposal_version':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(JsonObject),
          ) as JsonObject?;
          if (valueDes == null) continue;
          result.proposalVersion = valueDes;
          break;
        case r'settlement':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(JsonObject),
          ) as JsonObject?;
          if (valueDes == null) continue;
          result.settlement = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  Proof deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ProofBuilder();
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
