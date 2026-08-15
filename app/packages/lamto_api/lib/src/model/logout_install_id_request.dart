//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'logout_install_id_request.g.dart';

/// Optional body field for logout Device deactivation (spec 7.2).
///
/// Properties:
/// * [installId] - Deactivate this install's FCM Device on logout (also accepted via X-Install-Id).
@BuiltValue()
abstract class LogoutInstallIdRequest implements Built<LogoutInstallIdRequest, LogoutInstallIdRequestBuilder> {
  /// Deactivate this install's FCM Device on logout (also accepted via X-Install-Id).
  @BuiltValueField(wireName: r'install_id')
  String? get installId;

  LogoutInstallIdRequest._();

  factory LogoutInstallIdRequest([void updates(LogoutInstallIdRequestBuilder b)]) = _$LogoutInstallIdRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(LogoutInstallIdRequestBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<LogoutInstallIdRequest> get serializer => _$LogoutInstallIdRequestSerializer();
}

class _$LogoutInstallIdRequestSerializer implements PrimitiveSerializer<LogoutInstallIdRequest> {
  @override
  final Iterable<Type> types = const [LogoutInstallIdRequest, _$LogoutInstallIdRequest];

  @override
  final String wireName = r'LogoutInstallIdRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    LogoutInstallIdRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.installId != null) {
      yield r'install_id';
      yield serializers.serialize(
        object.installId,
        specifiedType: const FullType(String),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    LogoutInstallIdRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required LogoutInstallIdRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'install_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.installId = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  LogoutInstallIdRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = LogoutInstallIdRequestBuilder();
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
