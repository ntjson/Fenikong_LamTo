// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'bill_summary.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$BillSummary extends BillSummary {
  @override
  final int id;
  @override
  final String title;
  @override
  final int amountVnd;
  @override
  final BillStatusEnum status;
  @override
  final String period;
  @override
  final DateTime? dueDate;
  @override
  final DateTime issuedAt;
  @override
  final DateTime? paidAt;

  factory _$BillSummary([void Function(BillSummaryBuilder)? updates]) =>
      (BillSummaryBuilder()..update(updates))._build();

  _$BillSummary._(
      {required this.id,
      required this.title,
      required this.amountVnd,
      required this.status,
      required this.period,
      this.dueDate,
      required this.issuedAt,
      this.paidAt})
      : super._();
  @override
  BillSummary rebuild(void Function(BillSummaryBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  BillSummaryBuilder toBuilder() => BillSummaryBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is BillSummary &&
        id == other.id &&
        title == other.title &&
        amountVnd == other.amountVnd &&
        status == other.status &&
        period == other.period &&
        dueDate == other.dueDate &&
        issuedAt == other.issuedAt &&
        paidAt == other.paidAt;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, title.hashCode);
    _$hash = $jc(_$hash, amountVnd.hashCode);
    _$hash = $jc(_$hash, status.hashCode);
    _$hash = $jc(_$hash, period.hashCode);
    _$hash = $jc(_$hash, dueDate.hashCode);
    _$hash = $jc(_$hash, issuedAt.hashCode);
    _$hash = $jc(_$hash, paidAt.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'BillSummary')
          ..add('id', id)
          ..add('title', title)
          ..add('amountVnd', amountVnd)
          ..add('status', status)
          ..add('period', period)
          ..add('dueDate', dueDate)
          ..add('issuedAt', issuedAt)
          ..add('paidAt', paidAt))
        .toString();
  }
}

class BillSummaryBuilder implements Builder<BillSummary, BillSummaryBuilder> {
  _$BillSummary? _$v;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  String? _title;
  String? get title => _$this._title;
  set title(String? title) => _$this._title = title;

  int? _amountVnd;
  int? get amountVnd => _$this._amountVnd;
  set amountVnd(int? amountVnd) => _$this._amountVnd = amountVnd;

  BillStatusEnum? _status;
  BillStatusEnum? get status => _$this._status;
  set status(BillStatusEnum? status) => _$this._status = status;

  String? _period;
  String? get period => _$this._period;
  set period(String? period) => _$this._period = period;

  DateTime? _dueDate;
  DateTime? get dueDate => _$this._dueDate;
  set dueDate(DateTime? dueDate) => _$this._dueDate = dueDate;

  DateTime? _issuedAt;
  DateTime? get issuedAt => _$this._issuedAt;
  set issuedAt(DateTime? issuedAt) => _$this._issuedAt = issuedAt;

  DateTime? _paidAt;
  DateTime? get paidAt => _$this._paidAt;
  set paidAt(DateTime? paidAt) => _$this._paidAt = paidAt;

  BillSummaryBuilder() {
    BillSummary._defaults(this);
  }

  BillSummaryBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _id = $v.id;
      _title = $v.title;
      _amountVnd = $v.amountVnd;
      _status = $v.status;
      _period = $v.period;
      _dueDate = $v.dueDate;
      _issuedAt = $v.issuedAt;
      _paidAt = $v.paidAt;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(BillSummary other) {
    _$v = other as _$BillSummary;
  }

  @override
  void update(void Function(BillSummaryBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  BillSummary build() => _build();

  _$BillSummary _build() {
    final _$result = _$v ??
        _$BillSummary._(
          id: BuiltValueNullFieldError.checkNotNull(id, r'BillSummary', 'id'),
          title: BuiltValueNullFieldError.checkNotNull(
              title, r'BillSummary', 'title'),
          amountVnd: BuiltValueNullFieldError.checkNotNull(
              amountVnd, r'BillSummary', 'amountVnd'),
          status: BuiltValueNullFieldError.checkNotNull(
              status, r'BillSummary', 'status'),
          period: BuiltValueNullFieldError.checkNotNull(
              period, r'BillSummary', 'period'),
          dueDate: dueDate,
          issuedAt: BuiltValueNullFieldError.checkNotNull(
              issuedAt, r'BillSummary', 'issuedAt'),
          paidAt: paidAt,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
