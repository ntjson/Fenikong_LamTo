//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'fund_series_point.g.dart';

/// FundSeriesPoint
///
/// Properties:
/// * [periodStart]
/// * [inflowsVnd]
/// * [outflowsVnd] - Outflow-type amounts are stored negative; this is <= 0.
/// * [balanceVnd]
@BuiltValue()
abstract class FundSeriesPoint implements Built<FundSeriesPoint, FundSeriesPointBuilder> {
  @BuiltValueField(wireName: r'period_start')
  DateTime get periodStart;

  @BuiltValueField(wireName: r'inflows_vnd')
  int get inflowsVnd;

  /// Outflow-type amounts are stored negative; this is <= 0.
  @BuiltValueField(wireName: r'outflows_vnd')
  int get outflowsVnd;

  @BuiltValueField(wireName: r'balance_vnd')
  int get balanceVnd;

  FundSeriesPoint._();

  factory FundSeriesPoint([void updates(FundSeriesPointBuilder b)]) = _$FundSeriesPoint;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(FundSeriesPointBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<FundSeriesPoint> get serializer => _$FundSeriesPointSerializer();
}

class _$FundSeriesPointSerializer implements PrimitiveSerializer<FundSeriesPoint> {
  @override
  final Iterable<Type> types = const [FundSeriesPoint, _$FundSeriesPoint];

  @override
  final String wireName = r'FundSeriesPoint';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    FundSeriesPoint object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'period_start';
    yield serializers.serialize(
      object.periodStart,
      specifiedType: const FullType(DateTime),
    );
    yield r'inflows_vnd';
    yield serializers.serialize(
      object.inflowsVnd,
      specifiedType: const FullType(int),
    );
    yield r'outflows_vnd';
    yield serializers.serialize(
      object.outflowsVnd,
      specifiedType: const FullType(int),
    );
    yield r'balance_vnd';
    yield serializers.serialize(
      object.balanceVnd,
      specifiedType: const FullType(int),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    FundSeriesPoint object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required FundSeriesPointBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'period_start':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.periodStart = valueDes;
          break;
        case r'inflows_vnd':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.inflowsVnd = valueDes;
          break;
        case r'outflows_vnd':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.outflowsVnd = valueDes;
          break;
        case r'balance_vnd':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.balanceVnd = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  FundSeriesPoint deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = FundSeriesPointBuilder();
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
