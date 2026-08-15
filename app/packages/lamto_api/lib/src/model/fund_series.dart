//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:lamto_api/src/model/fund_series_point.dart';
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'fund_series.g.dart';

/// FundSeries
///
/// Properties:
/// * [range]
/// * [points]
@BuiltValue()
abstract class FundSeries implements Built<FundSeries, FundSeriesBuilder> {
  @BuiltValueField(wireName: r'range')
  String get range;

  @BuiltValueField(wireName: r'points')
  BuiltList<FundSeriesPoint> get points;

  FundSeries._();

  factory FundSeries([void updates(FundSeriesBuilder b)]) = _$FundSeries;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(FundSeriesBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<FundSeries> get serializer => _$FundSeriesSerializer();
}

class _$FundSeriesSerializer implements PrimitiveSerializer<FundSeries> {
  @override
  final Iterable<Type> types = const [FundSeries, _$FundSeries];

  @override
  final String wireName = r'FundSeries';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    FundSeries object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'range';
    yield serializers.serialize(
      object.range,
      specifiedType: const FullType(String),
    );
    yield r'points';
    yield serializers.serialize(
      object.points,
      specifiedType: const FullType(BuiltList, [FullType(FundSeriesPoint)]),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    FundSeries object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required FundSeriesBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'range':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.range = valueDes;
          break;
        case r'points':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(FundSeriesPoint)]),
          ) as BuiltList<FundSeriesPoint>;
          result.points.replace(valueDes);
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  FundSeries deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = FundSeriesBuilder();
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
