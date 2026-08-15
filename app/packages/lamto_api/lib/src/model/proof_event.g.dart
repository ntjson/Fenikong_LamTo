// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'proof_event.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ProofEvent extends ProofEvent {
  @override
  final String eventId;
  @override
  final int eventType;
  @override
  final String status;
  @override
  final String evidenceLevel;
  @override
  final String transactionHash;

  factory _$ProofEvent([void Function(ProofEventBuilder)? updates]) =>
      (ProofEventBuilder()..update(updates))._build();

  _$ProofEvent._(
      {required this.eventId,
      required this.eventType,
      required this.status,
      required this.evidenceLevel,
      required this.transactionHash})
      : super._();
  @override
  ProofEvent rebuild(void Function(ProofEventBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ProofEventBuilder toBuilder() => ProofEventBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ProofEvent &&
        eventId == other.eventId &&
        eventType == other.eventType &&
        status == other.status &&
        evidenceLevel == other.evidenceLevel &&
        transactionHash == other.transactionHash;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, eventId.hashCode);
    _$hash = $jc(_$hash, eventType.hashCode);
    _$hash = $jc(_$hash, status.hashCode);
    _$hash = $jc(_$hash, evidenceLevel.hashCode);
    _$hash = $jc(_$hash, transactionHash.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ProofEvent')
          ..add('eventId', eventId)
          ..add('eventType', eventType)
          ..add('status', status)
          ..add('evidenceLevel', evidenceLevel)
          ..add('transactionHash', transactionHash))
        .toString();
  }
}

class ProofEventBuilder implements Builder<ProofEvent, ProofEventBuilder> {
  _$ProofEvent? _$v;

  String? _eventId;
  String? get eventId => _$this._eventId;
  set eventId(String? eventId) => _$this._eventId = eventId;

  int? _eventType;
  int? get eventType => _$this._eventType;
  set eventType(int? eventType) => _$this._eventType = eventType;

  String? _status;
  String? get status => _$this._status;
  set status(String? status) => _$this._status = status;

  String? _evidenceLevel;
  String? get evidenceLevel => _$this._evidenceLevel;
  set evidenceLevel(String? evidenceLevel) =>
      _$this._evidenceLevel = evidenceLevel;

  String? _transactionHash;
  String? get transactionHash => _$this._transactionHash;
  set transactionHash(String? transactionHash) =>
      _$this._transactionHash = transactionHash;

  ProofEventBuilder() {
    ProofEvent._defaults(this);
  }

  ProofEventBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _eventId = $v.eventId;
      _eventType = $v.eventType;
      _status = $v.status;
      _evidenceLevel = $v.evidenceLevel;
      _transactionHash = $v.transactionHash;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ProofEvent other) {
    _$v = other as _$ProofEvent;
  }

  @override
  void update(void Function(ProofEventBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ProofEvent build() => _build();

  _$ProofEvent _build() {
    final _$result = _$v ??
        _$ProofEvent._(
          eventId: BuiltValueNullFieldError.checkNotNull(
              eventId, r'ProofEvent', 'eventId'),
          eventType: BuiltValueNullFieldError.checkNotNull(
              eventType, r'ProofEvent', 'eventType'),
          status: BuiltValueNullFieldError.checkNotNull(
              status, r'ProofEvent', 'status'),
          evidenceLevel: BuiltValueNullFieldError.checkNotNull(
              evidenceLevel, r'ProofEvent', 'evidenceLevel'),
          transactionHash: BuiltValueNullFieldError.checkNotNull(
              transactionHash, r'ProofEvent', 'transactionHash'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
