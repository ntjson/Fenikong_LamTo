// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'proposal_settlement.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ProposalSettlement extends ProposalSettlement {
  @override
  final int amountVnd;
  @override
  final String payeeName;
  @override
  final DateTime transferRecordedAt;
  @override
  final DateTime? acknowledgedAt;
  @override
  final DateTime? settledAt;

  factory _$ProposalSettlement(
          [void Function(ProposalSettlementBuilder)? updates]) =>
      (ProposalSettlementBuilder()..update(updates))._build();

  _$ProposalSettlement._(
      {required this.amountVnd,
      required this.payeeName,
      required this.transferRecordedAt,
      this.acknowledgedAt,
      this.settledAt})
      : super._();
  @override
  ProposalSettlement rebuild(
          void Function(ProposalSettlementBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ProposalSettlementBuilder toBuilder() =>
      ProposalSettlementBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ProposalSettlement &&
        amountVnd == other.amountVnd &&
        payeeName == other.payeeName &&
        transferRecordedAt == other.transferRecordedAt &&
        acknowledgedAt == other.acknowledgedAt &&
        settledAt == other.settledAt;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, amountVnd.hashCode);
    _$hash = $jc(_$hash, payeeName.hashCode);
    _$hash = $jc(_$hash, transferRecordedAt.hashCode);
    _$hash = $jc(_$hash, acknowledgedAt.hashCode);
    _$hash = $jc(_$hash, settledAt.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ProposalSettlement')
          ..add('amountVnd', amountVnd)
          ..add('payeeName', payeeName)
          ..add('transferRecordedAt', transferRecordedAt)
          ..add('acknowledgedAt', acknowledgedAt)
          ..add('settledAt', settledAt))
        .toString();
  }
}

class ProposalSettlementBuilder
    implements Builder<ProposalSettlement, ProposalSettlementBuilder> {
  _$ProposalSettlement? _$v;

  int? _amountVnd;
  int? get amountVnd => _$this._amountVnd;
  set amountVnd(int? amountVnd) => _$this._amountVnd = amountVnd;

  String? _payeeName;
  String? get payeeName => _$this._payeeName;
  set payeeName(String? payeeName) => _$this._payeeName = payeeName;

  DateTime? _transferRecordedAt;
  DateTime? get transferRecordedAt => _$this._transferRecordedAt;
  set transferRecordedAt(DateTime? transferRecordedAt) =>
      _$this._transferRecordedAt = transferRecordedAt;

  DateTime? _acknowledgedAt;
  DateTime? get acknowledgedAt => _$this._acknowledgedAt;
  set acknowledgedAt(DateTime? acknowledgedAt) =>
      _$this._acknowledgedAt = acknowledgedAt;

  DateTime? _settledAt;
  DateTime? get settledAt => _$this._settledAt;
  set settledAt(DateTime? settledAt) => _$this._settledAt = settledAt;

  ProposalSettlementBuilder() {
    ProposalSettlement._defaults(this);
  }

  ProposalSettlementBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _amountVnd = $v.amountVnd;
      _payeeName = $v.payeeName;
      _transferRecordedAt = $v.transferRecordedAt;
      _acknowledgedAt = $v.acknowledgedAt;
      _settledAt = $v.settledAt;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ProposalSettlement other) {
    _$v = other as _$ProposalSettlement;
  }

  @override
  void update(void Function(ProposalSettlementBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ProposalSettlement build() => _build();

  _$ProposalSettlement _build() {
    final _$result = _$v ??
        _$ProposalSettlement._(
          amountVnd: BuiltValueNullFieldError.checkNotNull(
              amountVnd, r'ProposalSettlement', 'amountVnd'),
          payeeName: BuiltValueNullFieldError.checkNotNull(
              payeeName, r'ProposalSettlement', 'payeeName'),
          transferRecordedAt: BuiltValueNullFieldError.checkNotNull(
              transferRecordedAt, r'ProposalSettlement', 'transferRecordedAt'),
          acknowledgedAt: acknowledgedAt,
          settledAt: settledAt,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
