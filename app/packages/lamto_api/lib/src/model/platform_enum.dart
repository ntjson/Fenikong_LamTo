//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'platform_enum.g.dart';

class PlatformEnum extends EnumClass {

  /// * `IOS` - IOS * `ANDROID` - ANDROID
  @BuiltValueEnumConst(wireName: r'IOS')
  static const PlatformEnum IOS = _$IOS;
  /// * `IOS` - IOS * `ANDROID` - ANDROID
  @BuiltValueEnumConst(wireName: r'ANDROID')
  static const PlatformEnum ANDROID = _$ANDROID;

  static Serializer<PlatformEnum> get serializer => _$platformEnumSerializer;

  const PlatformEnum._(String name): super(name);

  static BuiltSet<PlatformEnum> get values => _$values;
  static PlatformEnum valueOf(String name) => _$valueOf(name);
}

/// Optionally, enum_class can generate a mixin to go with your enum for use
/// with Angular. It exposes your enum constants as getters. So, if you mix it
/// in to your Dart component class, the values become available to the
/// corresponding Angular template.
///
/// Trigger mixin generation by writing a line like this one next to your enum.
abstract class PlatformEnumMixin = Object with _$PlatformEnumMixin;
