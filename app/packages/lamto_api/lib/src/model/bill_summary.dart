//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:lamto_api/src/model/bill_status_enum.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'bill_summary.g.dart';

/// BillSummary
///
/// Properties:
/// * [id]
/// * [title]
/// * [amountVnd]
/// * [status]
/// * [period]
/// * [dueDate]
/// * [issuedAt]
/// * [paidAt]
@BuiltValue()
abstract class BillSummary implements Built<BillSummary, BillSummaryBuilder> {
  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'title')
  String get title;

  @BuiltValueField(wireName: r'amount_vnd')
  int get amountVnd;

  @BuiltValueField(wireName: r'status')
  BillStatusEnum get status;
  // enum statusEnum {  ISSUED,  PAID,  VOID,  };

  @BuiltValueField(wireName: r'period')
  String get period;

  @BuiltValueField(wireName: r'due_date')
  DateTime? get dueDate;

  @BuiltValueField(wireName: r'issued_at')
  DateTime get issuedAt;

  @BuiltValueField(wireName: r'paid_at')
  DateTime? get paidAt;

  BillSummary._();

  factory BillSummary([void updates(BillSummaryBuilder b)]) = _$BillSummary;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(BillSummaryBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<BillSummary> get serializer => _$BillSummarySerializer();
}

class _$BillSummarySerializer implements PrimitiveSerializer<BillSummary> {
  @override
  final Iterable<Type> types = const [BillSummary, _$BillSummary];

  @override
  final String wireName = r'BillSummary';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    BillSummary object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(int),
    );
    yield r'title';
    yield serializers.serialize(
      object.title,
      specifiedType: const FullType(String),
    );
    yield r'amount_vnd';
    yield serializers.serialize(
      object.amountVnd,
      specifiedType: const FullType(int),
    );
    yield r'status';
    yield serializers.serialize(
      object.status,
      specifiedType: const FullType(BillStatusEnum),
    );
    yield r'period';
    yield serializers.serialize(
      object.period,
      specifiedType: const FullType(String),
    );
    yield r'due_date';
    yield object.dueDate == null ? null : serializers.serialize(
      object.dueDate,
      specifiedType: const FullType.nullable(DateTime),
    );
    yield r'issued_at';
    yield serializers.serialize(
      object.issuedAt,
      specifiedType: const FullType(DateTime),
    );
    yield r'paid_at';
    yield object.paidAt == null ? null : serializers.serialize(
      object.paidAt,
      specifiedType: const FullType.nullable(DateTime),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    BillSummary object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required BillSummaryBuilder result,
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
        case r'title':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.title = valueDes;
          break;
        case r'amount_vnd':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.amountVnd = valueDes;
          break;
        case r'status':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BillStatusEnum),
          ) as BillStatusEnum;
          result.status = valueDes;
          break;
        case r'period':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.period = valueDes;
          break;
        case r'due_date':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.dueDate = valueDes;
          break;
        case r'issued_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.issuedAt = valueDes;
          break;
        case r'paid_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.paidAt = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  BillSummary deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = BillSummaryBuilder();
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
