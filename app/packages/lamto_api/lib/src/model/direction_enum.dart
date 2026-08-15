//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'direction_enum.g.dart';

class DirectionEnum extends EnumClass {

  /// * `ENTRY` - ENTRY * `EXIT` - EXIT
  @BuiltValueEnumConst(wireName: r'ENTRY')
  static const DirectionEnum ENTRY = _$ENTRY;
  /// * `ENTRY` - ENTRY * `EXIT` - EXIT
  @BuiltValueEnumConst(wireName: r'EXIT')
  static const DirectionEnum EXIT = _$EXIT;

  static Serializer<DirectionEnum> get serializer => _$directionEnumSerializer;

  const DirectionEnum._(String name): super(name);

  static BuiltSet<DirectionEnum> get values => _$values;
  static DirectionEnum valueOf(String name) => _$valueOf(name);
}

/// Optionally, enum_class can generate a mixin to go with your enum for use
/// with Angular. It exposes your enum constants as getters. So, if you mix it
/// in to your Dart component class, the values become available to the
/// corresponding Angular template.
///
/// Trigger mixin generation by writing a line like this one next to your enum.
abstract class DirectionEnumMixin = Object with _$DirectionEnumMixin;
