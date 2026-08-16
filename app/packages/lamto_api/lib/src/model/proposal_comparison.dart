//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'proposal_comparison.g.dart';

/// ProposalComparison
///
/// Properties:
/// * [direction] - Direction of comparison: above, below, or equal.
/// * [percentage] - Difference percentage against the predicted price band.
/// * [range] - Formatted range string of the predicted price band.
/// * [reasoning] - One-sentence Vietnamese reasoning explaining the band.
/// * [source_] - Source of the prediction: predicted or fallback.
@BuiltValue()
abstract class ProposalComparison implements Built<ProposalComparison, ProposalComparisonBuilder> {
  /// Direction of comparison: above, below, or equal.
  @BuiltValueField(wireName: r'direction')
  String get direction;

  /// Difference percentage against the predicted price band.
  @BuiltValueField(wireName: r'percentage')
  int get percentage;

  /// Formatted range string of the predicted price band.
  @BuiltValueField(wireName: r'range')
  String get range;

  /// One-sentence Vietnamese reasoning explaining the band.
  @BuiltValueField(wireName: r'reasoning')
  String get reasoning;

  /// Source of the prediction: predicted or fallback.
  @BuiltValueField(wireName: r'source')
  String get source_;

  ProposalComparison._();

  factory ProposalComparison([void updates(ProposalComparisonBuilder b)]) = _$ProposalComparison;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ProposalComparisonBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ProposalComparison> get serializer => _$ProposalComparisonSerializer();
}

class _$ProposalComparisonSerializer implements PrimitiveSerializer<ProposalComparison> {
  @override
  final Iterable<Type> types = const [ProposalComparison, _$ProposalComparison];

  @override
  final String wireName = r'ProposalComparison';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ProposalComparison object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'direction';
    yield serializers.serialize(
      object.direction,
      specifiedType: const FullType(String),
    );
    yield r'percentage';
    yield serializers.serialize(
      object.percentage,
      specifiedType: const FullType(int),
    );
    yield r'range';
    yield serializers.serialize(
      object.range,
      specifiedType: const FullType(String),
    );
    yield r'reasoning';
    yield serializers.serialize(
      object.reasoning,
      specifiedType: const FullType(String),
    );
    yield r'source';
    yield serializers.serialize(
      object.source_,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    ProposalComparison object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ProposalComparisonBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'direction':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.direction = valueDes;
          break;
        case r'percentage':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.percentage = valueDes;
          break;
        case r'range':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.range = valueDes;
          break;
        case r'reasoning':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.reasoning = valueDes;
          break;
        case r'source':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.source_ = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  ProposalComparison deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ProposalComparisonBuilder();
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
