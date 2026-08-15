// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ledger_entry_list.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$LedgerEntryList extends LedgerEntryList {
  @override
  final int id;
  @override
  final String contractorName;
  @override
  final int actualCostVnd;
  @override
  final DateTime publishedAt;
  @override
  final String integrityStatus;
  @override
  final String evidenceLevel;
  @override
  final String whatWasFixed;

  factory _$LedgerEntryList([void Function(LedgerEntryListBuilder)? updates]) =>
      (LedgerEntryListBuilder()..update(updates))._build();

  _$LedgerEntryList._(
      {required this.id,
      required this.contractorName,
      required this.actualCostVnd,
      required this.publishedAt,
      required this.integrityStatus,
      required this.evidenceLevel,
      required this.whatWasFixed})
      : super._();
  @override
  LedgerEntryList rebuild(void Function(LedgerEntryListBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  LedgerEntryListBuilder toBuilder() => LedgerEntryListBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is LedgerEntryList &&
        id == other.id &&
        contractorName == other.contractorName &&
        actualCostVnd == other.actualCostVnd &&
        publishedAt == other.publishedAt &&
        integrityStatus == other.integrityStatus &&
        evidenceLevel == other.evidenceLevel &&
        whatWasFixed == other.whatWasFixed;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, contractorName.hashCode);
    _$hash = $jc(_$hash, actualCostVnd.hashCode);
    _$hash = $jc(_$hash, publishedAt.hashCode);
    _$hash = $jc(_$hash, integrityStatus.hashCode);
    _$hash = $jc(_$hash, evidenceLevel.hashCode);
    _$hash = $jc(_$hash, whatWasFixed.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'LedgerEntryList')
          ..add('id', id)
          ..add('contractorName', contractorName)
          ..add('actualCostVnd', actualCostVnd)
          ..add('publishedAt', publishedAt)
          ..add('integrityStatus', integrityStatus)
          ..add('evidenceLevel', evidenceLevel)
          ..add('whatWasFixed', whatWasFixed))
        .toString();
  }
}

class LedgerEntryListBuilder
    implements Builder<LedgerEntryList, LedgerEntryListBuilder> {
  _$LedgerEntryList? _$v;

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

  String? _integrityStatus;
  String? get integrityStatus => _$this._integrityStatus;
  set integrityStatus(String? integrityStatus) =>
      _$this._integrityStatus = integrityStatus;

  String? _evidenceLevel;
  String? get evidenceLevel => _$this._evidenceLevel;
  set evidenceLevel(String? evidenceLevel) =>
      _$this._evidenceLevel = evidenceLevel;

  String? _whatWasFixed;
  String? get whatWasFixed => _$this._whatWasFixed;
  set whatWasFixed(String? whatWasFixed) => _$this._whatWasFixed = whatWasFixed;

  LedgerEntryListBuilder() {
    LedgerEntryList._defaults(this);
  }

  LedgerEntryListBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _id = $v.id;
      _contractorName = $v.contractorName;
      _actualCostVnd = $v.actualCostVnd;
      _publishedAt = $v.publishedAt;
      _integrityStatus = $v.integrityStatus;
      _evidenceLevel = $v.evidenceLevel;
      _whatWasFixed = $v.whatWasFixed;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(LedgerEntryList other) {
    _$v = other as _$LedgerEntryList;
  }

  @override
  void update(void Function(LedgerEntryListBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  LedgerEntryList build() => _build();

  _$LedgerEntryList _build() {
    final _$result = _$v ??
        _$LedgerEntryList._(
          id: BuiltValueNullFieldError.checkNotNull(
              id, r'LedgerEntryList', 'id'),
          contractorName: BuiltValueNullFieldError.checkNotNull(
              contractorName, r'LedgerEntryList', 'contractorName'),
          actualCostVnd: BuiltValueNullFieldError.checkNotNull(
              actualCostVnd, r'LedgerEntryList', 'actualCostVnd'),
          publishedAt: BuiltValueNullFieldError.checkNotNull(
              publishedAt, r'LedgerEntryList', 'publishedAt'),
          integrityStatus: BuiltValueNullFieldError.checkNotNull(
              integrityStatus, r'LedgerEntryList', 'integrityStatus'),
          evidenceLevel: BuiltValueNullFieldError.checkNotNull(
              evidenceLevel, r'LedgerEntryList', 'evidenceLevel'),
          whatWasFixed: BuiltValueNullFieldError.checkNotNull(
              whatWasFixed, r'LedgerEntryList', 'whatWasFixed'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
