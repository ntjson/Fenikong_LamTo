// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'proof.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$Proof extends Proof {
  @override
  final String evidenceLevel;
  @override
  final String anchoringBackend;
  @override
  final String payloadHash;
  @override
  final BuiltList<ProofEvent> events;
  @override
  final JsonObject? proposalVersion;
  @override
  final JsonObject? settlement;

  factory _$Proof([void Function(ProofBuilder)? updates]) =>
      (ProofBuilder()..update(updates))._build();

  _$Proof._(
      {required this.evidenceLevel,
      required this.anchoringBackend,
      required this.payloadHash,
      required this.events,
      this.proposalVersion,
      this.settlement})
      : super._();
  @override
  Proof rebuild(void Function(ProofBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ProofBuilder toBuilder() => ProofBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is Proof &&
        evidenceLevel == other.evidenceLevel &&
        anchoringBackend == other.anchoringBackend &&
        payloadHash == other.payloadHash &&
        events == other.events &&
        proposalVersion == other.proposalVersion &&
        settlement == other.settlement;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, evidenceLevel.hashCode);
    _$hash = $jc(_$hash, anchoringBackend.hashCode);
    _$hash = $jc(_$hash, payloadHash.hashCode);
    _$hash = $jc(_$hash, events.hashCode);
    _$hash = $jc(_$hash, proposalVersion.hashCode);
    _$hash = $jc(_$hash, settlement.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'Proof')
          ..add('evidenceLevel', evidenceLevel)
          ..add('anchoringBackend', anchoringBackend)
          ..add('payloadHash', payloadHash)
          ..add('events', events)
          ..add('proposalVersion', proposalVersion)
          ..add('settlement', settlement))
        .toString();
  }
}

class ProofBuilder implements Builder<Proof, ProofBuilder> {
  _$Proof? _$v;

  String? _evidenceLevel;
  String? get evidenceLevel => _$this._evidenceLevel;
  set evidenceLevel(String? evidenceLevel) =>
      _$this._evidenceLevel = evidenceLevel;

  String? _anchoringBackend;
  String? get anchoringBackend => _$this._anchoringBackend;
  set anchoringBackend(String? anchoringBackend) =>
      _$this._anchoringBackend = anchoringBackend;

  String? _payloadHash;
  String? get payloadHash => _$this._payloadHash;
  set payloadHash(String? payloadHash) => _$this._payloadHash = payloadHash;

  ListBuilder<ProofEvent>? _events;
  ListBuilder<ProofEvent> get events =>
      _$this._events ??= ListBuilder<ProofEvent>();
  set events(ListBuilder<ProofEvent>? events) => _$this._events = events;

  JsonObject? _proposalVersion;
  JsonObject? get proposalVersion => _$this._proposalVersion;
  set proposalVersion(JsonObject? proposalVersion) =>
      _$this._proposalVersion = proposalVersion;

  JsonObject? _settlement;
  JsonObject? get settlement => _$this._settlement;
  set settlement(JsonObject? settlement) => _$this._settlement = settlement;

  ProofBuilder() {
    Proof._defaults(this);
  }

  ProofBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _evidenceLevel = $v.evidenceLevel;
      _anchoringBackend = $v.anchoringBackend;
      _payloadHash = $v.payloadHash;
      _events = $v.events.toBuilder();
      _proposalVersion = $v.proposalVersion;
      _settlement = $v.settlement;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(Proof other) {
    _$v = other as _$Proof;
  }

  @override
  void update(void Function(ProofBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  Proof build() => _build();

  _$Proof _build() {
    _$Proof _$result;
    try {
      _$result = _$v ??
          _$Proof._(
            evidenceLevel: BuiltValueNullFieldError.checkNotNull(
                evidenceLevel, r'Proof', 'evidenceLevel'),
            anchoringBackend: BuiltValueNullFieldError.checkNotNull(
                anchoringBackend, r'Proof', 'anchoringBackend'),
            payloadHash: BuiltValueNullFieldError.checkNotNull(
                payloadHash, r'Proof', 'payloadHash'),
            events: events.build(),
            proposalVersion: proposalVersion,
            settlement: settlement,
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'events';
        events.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(r'Proof', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
