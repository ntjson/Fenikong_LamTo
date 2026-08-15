// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'proposal.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$Proposal extends Proposal {
  @override
  final int id;
  @override
  final int? caseId;
  @override
  final int buildingId;
  @override
  final String status;
  @override
  final DateTime? completedAt;
  @override
  final DateTime? closedAt;
  @override
  final String purpose;
  @override
  final String proposedAction;
  @override
  final int amountVnd;
  @override
  final String fundCode;
  @override
  final String contractorName;
  @override
  final String expectedSchedule;
  @override
  final BuiltList<ProposalVersion> versions;
  @override
  final BuiltList<ProposalProgress> progress;
  @override
  final ProposalSettlement? settlement;
  @override
  final bool canRate;

  factory _$Proposal([void Function(ProposalBuilder)? updates]) =>
      (ProposalBuilder()..update(updates))._build();

  _$Proposal._(
      {required this.id,
      this.caseId,
      required this.buildingId,
      required this.status,
      this.completedAt,
      this.closedAt,
      required this.purpose,
      required this.proposedAction,
      required this.amountVnd,
      required this.fundCode,
      required this.contractorName,
      required this.expectedSchedule,
      required this.versions,
      required this.progress,
      this.settlement,
      required this.canRate})
      : super._();
  @override
  Proposal rebuild(void Function(ProposalBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ProposalBuilder toBuilder() => ProposalBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is Proposal &&
        id == other.id &&
        caseId == other.caseId &&
        buildingId == other.buildingId &&
        status == other.status &&
        completedAt == other.completedAt &&
        closedAt == other.closedAt &&
        purpose == other.purpose &&
        proposedAction == other.proposedAction &&
        amountVnd == other.amountVnd &&
        fundCode == other.fundCode &&
        contractorName == other.contractorName &&
        expectedSchedule == other.expectedSchedule &&
        versions == other.versions &&
        progress == other.progress &&
        settlement == other.settlement &&
        canRate == other.canRate;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, caseId.hashCode);
    _$hash = $jc(_$hash, buildingId.hashCode);
    _$hash = $jc(_$hash, status.hashCode);
    _$hash = $jc(_$hash, completedAt.hashCode);
    _$hash = $jc(_$hash, closedAt.hashCode);
    _$hash = $jc(_$hash, purpose.hashCode);
    _$hash = $jc(_$hash, proposedAction.hashCode);
    _$hash = $jc(_$hash, amountVnd.hashCode);
    _$hash = $jc(_$hash, fundCode.hashCode);
    _$hash = $jc(_$hash, contractorName.hashCode);
    _$hash = $jc(_$hash, expectedSchedule.hashCode);
    _$hash = $jc(_$hash, versions.hashCode);
    _$hash = $jc(_$hash, progress.hashCode);
    _$hash = $jc(_$hash, settlement.hashCode);
    _$hash = $jc(_$hash, canRate.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'Proposal')
          ..add('id', id)
          ..add('caseId', caseId)
          ..add('buildingId', buildingId)
          ..add('status', status)
          ..add('completedAt', completedAt)
          ..add('closedAt', closedAt)
          ..add('purpose', purpose)
          ..add('proposedAction', proposedAction)
          ..add('amountVnd', amountVnd)
          ..add('fundCode', fundCode)
          ..add('contractorName', contractorName)
          ..add('expectedSchedule', expectedSchedule)
          ..add('versions', versions)
          ..add('progress', progress)
          ..add('settlement', settlement)
          ..add('canRate', canRate))
        .toString();
  }
}

class ProposalBuilder implements Builder<Proposal, ProposalBuilder> {
  _$Proposal? _$v;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  int? _caseId;
  int? get caseId => _$this._caseId;
  set caseId(int? caseId) => _$this._caseId = caseId;

  int? _buildingId;
  int? get buildingId => _$this._buildingId;
  set buildingId(int? buildingId) => _$this._buildingId = buildingId;

  String? _status;
  String? get status => _$this._status;
  set status(String? status) => _$this._status = status;

  DateTime? _completedAt;
  DateTime? get completedAt => _$this._completedAt;
  set completedAt(DateTime? completedAt) => _$this._completedAt = completedAt;

  DateTime? _closedAt;
  DateTime? get closedAt => _$this._closedAt;
  set closedAt(DateTime? closedAt) => _$this._closedAt = closedAt;

  String? _purpose;
  String? get purpose => _$this._purpose;
  set purpose(String? purpose) => _$this._purpose = purpose;

  String? _proposedAction;
  String? get proposedAction => _$this._proposedAction;
  set proposedAction(String? proposedAction) =>
      _$this._proposedAction = proposedAction;

  int? _amountVnd;
  int? get amountVnd => _$this._amountVnd;
  set amountVnd(int? amountVnd) => _$this._amountVnd = amountVnd;

  String? _fundCode;
  String? get fundCode => _$this._fundCode;
  set fundCode(String? fundCode) => _$this._fundCode = fundCode;

  String? _contractorName;
  String? get contractorName => _$this._contractorName;
  set contractorName(String? contractorName) =>
      _$this._contractorName = contractorName;

  String? _expectedSchedule;
  String? get expectedSchedule => _$this._expectedSchedule;
  set expectedSchedule(String? expectedSchedule) =>
      _$this._expectedSchedule = expectedSchedule;

  ListBuilder<ProposalVersion>? _versions;
  ListBuilder<ProposalVersion> get versions =>
      _$this._versions ??= ListBuilder<ProposalVersion>();
  set versions(ListBuilder<ProposalVersion>? versions) =>
      _$this._versions = versions;

  ListBuilder<ProposalProgress>? _progress;
  ListBuilder<ProposalProgress> get progress =>
      _$this._progress ??= ListBuilder<ProposalProgress>();
  set progress(ListBuilder<ProposalProgress>? progress) =>
      _$this._progress = progress;

  ProposalSettlementBuilder? _settlement;
  ProposalSettlementBuilder get settlement =>
      _$this._settlement ??= ProposalSettlementBuilder();
  set settlement(ProposalSettlementBuilder? settlement) =>
      _$this._settlement = settlement;

  bool? _canRate;
  bool? get canRate => _$this._canRate;
  set canRate(bool? canRate) => _$this._canRate = canRate;

  ProposalBuilder() {
    Proposal._defaults(this);
  }

  ProposalBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _id = $v.id;
      _caseId = $v.caseId;
      _buildingId = $v.buildingId;
      _status = $v.status;
      _completedAt = $v.completedAt;
      _closedAt = $v.closedAt;
      _purpose = $v.purpose;
      _proposedAction = $v.proposedAction;
      _amountVnd = $v.amountVnd;
      _fundCode = $v.fundCode;
      _contractorName = $v.contractorName;
      _expectedSchedule = $v.expectedSchedule;
      _versions = $v.versions.toBuilder();
      _progress = $v.progress.toBuilder();
      _settlement = $v.settlement?.toBuilder();
      _canRate = $v.canRate;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(Proposal other) {
    _$v = other as _$Proposal;
  }

  @override
  void update(void Function(ProposalBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  Proposal build() => _build();

  _$Proposal _build() {
    _$Proposal _$result;
    try {
      _$result = _$v ??
          _$Proposal._(
            id: BuiltValueNullFieldError.checkNotNull(id, r'Proposal', 'id'),
            caseId: caseId,
            buildingId: BuiltValueNullFieldError.checkNotNull(
                buildingId, r'Proposal', 'buildingId'),
            status: BuiltValueNullFieldError.checkNotNull(
                status, r'Proposal', 'status'),
            completedAt: completedAt,
            closedAt: closedAt,
            purpose: BuiltValueNullFieldError.checkNotNull(
                purpose, r'Proposal', 'purpose'),
            proposedAction: BuiltValueNullFieldError.checkNotNull(
                proposedAction, r'Proposal', 'proposedAction'),
            amountVnd: BuiltValueNullFieldError.checkNotNull(
                amountVnd, r'Proposal', 'amountVnd'),
            fundCode: BuiltValueNullFieldError.checkNotNull(
                fundCode, r'Proposal', 'fundCode'),
            contractorName: BuiltValueNullFieldError.checkNotNull(
                contractorName, r'Proposal', 'contractorName'),
            expectedSchedule: BuiltValueNullFieldError.checkNotNull(
                expectedSchedule, r'Proposal', 'expectedSchedule'),
            versions: versions.build(),
            progress: progress.build(),
            settlement: _settlement?.build(),
            canRate: BuiltValueNullFieldError.checkNotNull(
                canRate, r'Proposal', 'canRate'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'versions';
        versions.build();
        _$failedField = 'progress';
        progress.build();
        _$failedField = 'settlement';
        _settlement?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'Proposal', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
