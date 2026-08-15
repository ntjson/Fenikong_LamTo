//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'fund_summary.g.dart';

/// FundSummary
///
/// Properties:
/// * [balanceVnd]
/// * [periodDays]
/// * [periodInflowsVnd]
/// * [periodOutflowsVnd]
@BuiltValue()
abstract class FundSummary implements Built<FundSummary, FundSummaryBuilder> {
  @BuiltValueField(wireName: r'balance_vnd')
  int get balanceVnd;

  @BuiltValueField(wireName: r'period_days')
  int get periodDays;

  @BuiltValueField(wireName: r'period_inflows_vnd')
  int get periodInflowsVnd;

  @BuiltValueField(wireName: r'period_outflows_vnd')
  int get periodOutflowsVnd;

  FundSummary._();

  factory FundSummary([void updates(FundSummaryBuilder b)]) = _$FundSummary;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(FundSummaryBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<FundSummary> get serializer => _$FundSummarySerializer();
}

class _$FundSummarySerializer implements PrimitiveSerializer<FundSummary> {
  @override
  final Iterable<Type> types = const [FundSummary, _$FundSummary];

  @override
  final String wireName = r'FundSummary';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    FundSummary object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'balance_vnd';
    yield serializers.serialize(
      object.balanceVnd,
      specifiedType: const FullType(int),
    );
    yield r'period_days';
    yield serializers.serialize(
      object.periodDays,
      specifiedType: const FullType(int),
    );
    yield r'period_inflows_vnd';
    yield serializers.serialize(
      object.periodInflowsVnd,
      specifiedType: const FullType(int),
    );
    yield r'period_outflows_vnd';
    yield serializers.serialize(
      object.periodOutflowsVnd,
      specifiedType: const FullType(int),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    FundSummary object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required FundSummaryBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'balance_vnd':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.balanceVnd = valueDes;
          break;
        case r'period_days':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.periodDays = valueDes;
          break;
        case r'period_inflows_vnd':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.periodInflowsVnd = valueDes;
          break;
        case r'period_outflows_vnd':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.periodOutflowsVnd = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  FundSummary deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = FundSummaryBuilder();
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
