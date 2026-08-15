//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'bill_status_enum.g.dart';

class BillStatusEnum extends EnumClass {

  /// * `ISSUED` - Đã phát hành * `PAID` - Đã thanh toán * `VOID` - Đã hủy
  @BuiltValueEnumConst(wireName: r'ISSUED')
  static const BillStatusEnum ISSUED = _$ISSUED;
  /// * `ISSUED` - Đã phát hành * `PAID` - Đã thanh toán * `VOID` - Đã hủy
  @BuiltValueEnumConst(wireName: r'PAID')
  static const BillStatusEnum PAID = _$PAID;
  /// * `ISSUED` - Đã phát hành * `PAID` - Đã thanh toán * `VOID` - Đã hủy
  @BuiltValueEnumConst(wireName: r'VOID')
  static const BillStatusEnum VOID = _$VOID;

  static Serializer<BillStatusEnum> get serializer => _$billStatusEnumSerializer;

  const BillStatusEnum._(String name): super(name);

  static BuiltSet<BillStatusEnum> get values => _$values;
  static BillStatusEnum valueOf(String name) => _$valueOf(name);
}

/// Optionally, enum_class can generate a mixin to go with your enum for use
/// with Angular. It exposes your enum constants as getters. So, if you mix it
/// in to your Dart component class, the values become available to the
/// corresponding Angular template.
///
/// Trigger mixin generation by writing a line like this one next to your enum.
abstract class BillStatusEnumMixin = Object with _$BillStatusEnumMixin;
