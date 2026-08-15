//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'kind_enum.g.dart';

class KindEnum extends EnumClass {

  /// * `BEFORE` - Trước * `AFTER` - Sau
  @BuiltValueEnumConst(wireName: r'BEFORE')
  static const KindEnum BEFORE = _$BEFORE;
  /// * `BEFORE` - Trước * `AFTER` - Sau
  @BuiltValueEnumConst(wireName: r'AFTER')
  static const KindEnum AFTER = _$AFTER;

  static Serializer<KindEnum> get serializer => _$kindEnumSerializer;

  const KindEnum._(String name): super(name);

  static BuiltSet<KindEnum> get values => _$values;
  static KindEnum valueOf(String name) => _$valueOf(name);
}

/// Optionally, enum_class can generate a mixin to go with your enum for use
/// with Angular. It exposes your enum constants as getters. So, if you mix it
/// in to your Dart component class, the values become available to the
/// corresponding Angular template.
///
/// Trigger mixin generation by writing a line like this one next to your enum.
abstract class KindEnumMixin = Object with _$KindEnumMixin;
