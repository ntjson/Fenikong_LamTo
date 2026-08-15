// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'report_create_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ReportCreateRequest extends ReportCreateRequest {
  @override
  final String clientRef;
  @override
  final String text;
  @override
  final bool? isPrivate;
  @override
  final int locationId;

  factory _$ReportCreateRequest(
          [void Function(ReportCreateRequestBuilder)? updates]) =>
      (ReportCreateRequestBuilder()..update(updates))._build();

  _$ReportCreateRequest._(
      {required this.clientRef,
      required this.text,
      this.isPrivate,
      required this.locationId})
      : super._();
  @override
  ReportCreateRequest rebuild(
          void Function(ReportCreateRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ReportCreateRequestBuilder toBuilder() =>
      ReportCreateRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ReportCreateRequest &&
        clientRef == other.clientRef &&
        text == other.text &&
        isPrivate == other.isPrivate &&
        locationId == other.locationId;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, clientRef.hashCode);
    _$hash = $jc(_$hash, text.hashCode);
    _$hash = $jc(_$hash, isPrivate.hashCode);
    _$hash = $jc(_$hash, locationId.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ReportCreateRequest')
          ..add('clientRef', clientRef)
          ..add('text', text)
          ..add('isPrivate', isPrivate)
          ..add('locationId', locationId))
        .toString();
  }
}

class ReportCreateRequestBuilder
    implements Builder<ReportCreateRequest, ReportCreateRequestBuilder> {
  _$ReportCreateRequest? _$v;

  String? _clientRef;
  String? get clientRef => _$this._clientRef;
  set clientRef(String? clientRef) => _$this._clientRef = clientRef;

  String? _text;
  String? get text => _$this._text;
  set text(String? text) => _$this._text = text;

  bool? _isPrivate;
  bool? get isPrivate => _$this._isPrivate;
  set isPrivate(bool? isPrivate) => _$this._isPrivate = isPrivate;

  int? _locationId;
  int? get locationId => _$this._locationId;
  set locationId(int? locationId) => _$this._locationId = locationId;

  ReportCreateRequestBuilder() {
    ReportCreateRequest._defaults(this);
  }

  ReportCreateRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _clientRef = $v.clientRef;
      _text = $v.text;
      _isPrivate = $v.isPrivate;
      _locationId = $v.locationId;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ReportCreateRequest other) {
    _$v = other as _$ReportCreateRequest;
  }

  @override
  void update(void Function(ReportCreateRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ReportCreateRequest build() => _build();

  _$ReportCreateRequest _build() {
    final _$result = _$v ??
        _$ReportCreateRequest._(
          clientRef: BuiltValueNullFieldError.checkNotNull(
              clientRef, r'ReportCreateRequest', 'clientRef'),
          text: BuiltValueNullFieldError.checkNotNull(
              text, r'ReportCreateRequest', 'text'),
          isPrivate: isPrivate,
          locationId: BuiltValueNullFieldError.checkNotNull(
              locationId, r'ReportCreateRequest', 'locationId'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
