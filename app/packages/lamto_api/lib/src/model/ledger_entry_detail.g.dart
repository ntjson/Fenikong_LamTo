// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ledger_entry_detail.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$LedgerEntryDetail extends LedgerEntryDetail {
  @override
  final int id;
  @override
  final String contractorName;
  @override
  final int actualCostVnd;
  @override
  final DateTime publishedAt;
  @override
  final int? proposedAmountVnd;
  @override
  final String integrityStatus;
  @override
  final String whatWasFixed;
  @override
  final String why;
  @override
  final JsonObject? payload;
  @override
  final Verification? verification;
  @override
  final BuiltList<JsonObject?> approvers;
  @override
  final BuiltList<JsonObject?> corrections;
  @override
  final BuiltList<LedgerDocument> documents;
  @override
  final Proof proof;

  factory _$LedgerEntryDetail(
          [void Function(LedgerEntryDetailBuilder)? updates]) =>
      (LedgerEntryDetailBuilder()..update(updates))._build();

  _$LedgerEntryDetail._(
      {required this.id,
      required this.contractorName,
      required this.actualCostVnd,
      required this.publishedAt,
      this.proposedAmountVnd,
      required this.integrityStatus,
      required this.whatWasFixed,
      required this.why,
      this.payload,
      this.verification,
      required this.approvers,
      required this.corrections,
      required this.documents,
      required this.proof})
      : super._();
  @override
  LedgerEntryDetail rebuild(void Function(LedgerEntryDetailBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  LedgerEntryDetailBuilder toBuilder() =>
      LedgerEntryDetailBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is LedgerEntryDetail &&
        id == other.id &&
        contractorName == other.contractorName &&
        actualCostVnd == other.actualCostVnd &&
        publishedAt == other.publishedAt &&
        proposedAmountVnd == other.proposedAmountVnd &&
        integrityStatus == other.integrityStatus &&
        whatWasFixed == other.whatWasFixed &&
        why == other.why &&
        payload == other.payload &&
        verification == other.verification &&
        approvers == other.approvers &&
        corrections == other.corrections &&
        documents == other.documents &&
        proof == other.proof;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, contractorName.hashCode);
    _$hash = $jc(_$hash, actualCostVnd.hashCode);
    _$hash = $jc(_$hash, publishedAt.hashCode);
    _$hash = $jc(_$hash, proposedAmountVnd.hashCode);
    _$hash = $jc(_$hash, integrityStatus.hashCode);
    _$hash = $jc(_$hash, whatWasFixed.hashCode);
    _$hash = $jc(_$hash, why.hashCode);
    _$hash = $jc(_$hash, payload.hashCode);
    _$hash = $jc(_$hash, verification.hashCode);
    _$hash = $jc(_$hash, approvers.hashCode);
    _$hash = $jc(_$hash, corrections.hashCode);
    _$hash = $jc(_$hash, documents.hashCode);
    _$hash = $jc(_$hash, proof.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'LedgerEntryDetail')
          ..add('id', id)
          ..add('contractorName', contractorName)
          ..add('actualCostVnd', actualCostVnd)
          ..add('publishedAt', publishedAt)
          ..add('proposedAmountVnd', proposedAmountVnd)
          ..add('integrityStatus', integrityStatus)
          ..add('whatWasFixed', whatWasFixed)
          ..add('why', why)
          ..add('payload', payload)
          ..add('verification', verification)
          ..add('approvers', approvers)
          ..add('corrections', corrections)
          ..add('documents', documents)
          ..add('proof', proof))
        .toString();
  }
}

class LedgerEntryDetailBuilder
    implements Builder<LedgerEntryDetail, LedgerEntryDetailBuilder> {
  _$LedgerEntryDetail? _$v;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  String? _contractorName;
  String? get contractorName => _$this._contractorName;
  set contractorName(String? contractorName) =>
      _$this._contractorName = contractorName;

  int? _actualCostVnd;
  int? get actualCostVnd => _$this._actualCostVnd;
  set actualCostVnd(int? actualCostVnd) =>
      _$this._actualCostVnd = actualCostVnd;

  DateTime? _publishedAt;
  DateTime? get publishedAt => _$this._publishedAt;
  set publishedAt(DateTime? publishedAt) => _$this._publishedAt = publishedAt;

  int? _proposedAmountVnd;
  int? get proposedAmountVnd => _$this._proposedAmountVnd;
  set proposedAmountVnd(int? proposedAmountVnd) =>
      _$this._proposedAmountVnd = proposedAmountVnd;

  String? _integrityStatus;
  String? get integrityStatus => _$this._integrityStatus;
  set integrityStatus(String? integrityStatus) =>
      _$this._integrityStatus = integrityStatus;

  String? _whatWasFixed;
  String? get whatWasFixed => _$this._whatWasFixed;
  set whatWasFixed(String? whatWasFixed) => _$this._whatWasFixed = whatWasFixed;

  String? _why;
  String? get why => _$this._why;
  set why(String? why) => _$this._why = why;

  JsonObject? _payload;
  JsonObject? get payload => _$this._payload;
  set payload(JsonObject? payload) => _$this._payload = payload;

  VerificationBuilder? _verification;
  VerificationBuilder get verification =>
      _$this._verification ??= VerificationBuilder();
  set verification(VerificationBuilder? verification) =>
      _$this._verification = verification;

  ListBuilder<JsonObject?>? _approvers;
  ListBuilder<JsonObject?> get approvers =>
      _$this._approvers ??= ListBuilder<JsonObject?>();
  set approvers(ListBuilder<JsonObject?>? approvers) =>
      _$this._approvers = approvers;

  ListBuilder<JsonObject?>? _corrections;
  ListBuilder<JsonObject?> get corrections =>
      _$this._corrections ??= ListBuilder<JsonObject?>();
  set corrections(ListBuilder<JsonObject?>? corrections) =>
      _$this._corrections = corrections;

  ListBuilder<LedgerDocument>? _documents;
  ListBuilder<LedgerDocument> get documents =>
      _$this._documents ??= ListBuilder<LedgerDocument>();
  set documents(ListBuilder<LedgerDocument>? documents) =>
      _$this._documents = documents;

  ProofBuilder? _proof;
  ProofBuilder get proof => _$this._proof ??= ProofBuilder();
  set proof(ProofBuilder? proof) => _$this._proof = proof;

  LedgerEntryDetailBuilder() {
    LedgerEntryDetail._defaults(this);
  }

  LedgerEntryDetailBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _id = $v.id;
      _contractorName = $v.contractorName;
      _actualCostVnd = $v.actualCostVnd;
      _publishedAt = $v.publishedAt;
      _proposedAmountVnd = $v.proposedAmountVnd;
      _integrityStatus = $v.integrityStatus;
      _whatWasFixed = $v.whatWasFixed;
      _why = $v.why;
      _payload = $v.payload;
      _verification = $v.verification?.toBuilder();
      _approvers = $v.approvers.toBuilder();
      _corrections = $v.corrections.toBuilder();
      _documents = $v.documents.toBuilder();
      _proof = $v.proof.toBuilder();
      _$v = null;
    }
    return this;
  }

  @override
  void replace(LedgerEntryDetail other) {
    _$v = other as _$LedgerEntryDetail;
  }

  @override
  void update(void Function(LedgerEntryDetailBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  LedgerEntryDetail build() => _build();

  _$LedgerEntryDetail _build() {
    _$LedgerEntryDetail _$result;
    try {
      _$result = _$v ??
          _$LedgerEntryDetail._(
            id: BuiltValueNullFieldError.checkNotNull(
                id, r'LedgerEntryDetail', 'id'),
            contractorName: BuiltValueNullFieldError.checkNotNull(
                contractorName, r'LedgerEntryDetail', 'contractorName'),
            actualCostVnd: BuiltValueNullFieldError.checkNotNull(
                actualCostVnd, r'LedgerEntryDetail', 'actualCostVnd'),
            publishedAt: BuiltValueNullFieldError.checkNotNull(
                publishedAt, r'LedgerEntryDetail', 'publishedAt'),
            proposedAmountVnd: proposedAmountVnd,
            integrityStatus: BuiltValueNullFieldError.checkNotNull(
                integrityStatus, r'LedgerEntryDetail', 'integrityStatus'),
            whatWasFixed: BuiltValueNullFieldError.checkNotNull(
                whatWasFixed, r'LedgerEntryDetail', 'whatWasFixed'),
            why: BuiltValueNullFieldError.checkNotNull(
                why, r'LedgerEntryDetail', 'why'),
            payload: payload,
            verification: _verification?.build(),
            approvers: approvers.build(),
            corrections: corrections.build(),
            documents: documents.build(),
            proof: proof.build(),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'verification';
        _verification?.build();
        _$failedField = 'approvers';
        approvers.build();
        _$failedField = 'corrections';
        corrections.build();
        _$failedField = 'documents';
        documents.build();
        _$failedField = 'proof';
        proof.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'LedgerEntryDetail', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
