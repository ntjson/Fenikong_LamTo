//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'report_create_request.g.dart';

/// ReportCreateRequest
///
/// Properties:
/// * [clientRef] - Client-generated UUID, unique per user (spec 3.5).
/// * [text]
/// * [isPrivate]
/// * [locationId] - Active BuildingLocation id in the resolved occupancy building.
@BuiltValue()
abstract class ReportCreateRequest implements Built<ReportCreateRequest, ReportCreateRequestBuilder> {
  /// Client-generated UUID, unique per user (spec 3.5).
  @BuiltValueField(wireName: r'client_ref')
  String get clientRef;

  @BuiltValueField(wireName: r'text')
  String get text;

  @BuiltValueField(wireName: r'is_private')
  bool? get isPrivate;

  /// Active BuildingLocation id in the resolved occupancy building.
  @BuiltValueField(wireName: r'location_id')
  int get locationId;

  ReportCreateRequest._();

  factory ReportCreateRequest([void updates(ReportCreateRequestBuilder b)]) = _$ReportCreateRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ReportCreateRequestBuilder b) => b
      ..isPrivate = false;

  @BuiltValueSerializer(custom: true)
  static Serializer<ReportCreateRequest> get serializer => _$ReportCreateRequestSerializer();
}

class _$ReportCreateRequestSerializer implements PrimitiveSerializer<ReportCreateRequest> {
  @override
  final Iterable<Type> types = const [ReportCreateRequest, _$ReportCreateRequest];

  @override
  final String wireName = r'ReportCreateRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ReportCreateRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'client_ref';
    yield serializers.serialize(
      object.clientRef,
      specifiedType: const FullType(String),
    );
    yield r'text';
    yield serializers.serialize(
      object.text,
      specifiedType: const FullType(String),
    );
    if (object.isPrivate != null) {
      yield r'is_private';
      yield serializers.serialize(
        object.isPrivate,
        specifiedType: const FullType(bool),
      );
    }
    yield r'location_id';
    yield serializers.serialize(
      object.locationId,
      specifiedType: const FullType(int),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    ReportCreateRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ReportCreateRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'client_ref':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.clientRef = valueDes;
          break;
        case r'text':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.text = valueDes;
          break;
        case r'is_private':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.isPrivate = valueDes;
          break;
        case r'location_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.locationId = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  ReportCreateRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ReportCreateRequestBuilder();
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
