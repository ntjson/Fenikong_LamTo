// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'bill_detail.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$BillDetail extends BillDetail {
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
  @override
  final String note;
  @override
  final String documentFilename;
  @override
  final String documentDownloadUrl;

  factory _$BillDetail([void Function(BillDetailBuilder)? updates]) =>
      (BillDetailBuilder()..update(updates))._build();

  _$BillDetail._(
      {required this.id,
      required this.title,
      required this.amountVnd,
      required this.status,
      required this.period,
      this.dueDate,
      required this.issuedAt,
      this.paidAt,
      required this.note,
      required this.documentFilename,
      required this.documentDownloadUrl})
      : super._();
  @override
  BillDetail rebuild(void Function(BillDetailBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  BillDetailBuilder toBuilder() => BillDetailBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is BillDetail &&
        id == other.id &&
        title == other.title &&
        amountVnd == other.amountVnd &&
        status == other.status &&
        period == other.period &&
        dueDate == other.dueDate &&
        issuedAt == other.issuedAt &&
        paidAt == other.paidAt &&
        note == other.note &&
        documentFilename == other.documentFilename &&
        documentDownloadUrl == other.documentDownloadUrl;
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
    _$hash = $jc(_$hash, note.hashCode);
    _$hash = $jc(_$hash, documentFilename.hashCode);
    _$hash = $jc(_$hash, documentDownloadUrl.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'BillDetail')
          ..add('id', id)
          ..add('title', title)
          ..add('amountVnd', amountVnd)
          ..add('status', status)
          ..add('period', period)
          ..add('dueDate', dueDate)
          ..add('issuedAt', issuedAt)
          ..add('paidAt', paidAt)
          ..add('note', note)
          ..add('documentFilename', documentFilename)
          ..add('documentDownloadUrl', documentDownloadUrl))
        .toString();
  }
}

class BillDetailBuilder implements Builder<BillDetail, BillDetailBuilder> {
  _$BillDetail? _$v;

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

  String? _note;
  String? get note => _$this._note;
  set note(String? note) => _$this._note = note;

  String? _documentFilename;
  String? get documentFilename => _$this._documentFilename;
  set documentFilename(String? documentFilename) =>
      _$this._documentFilename = documentFilename;

  String? _documentDownloadUrl;
  String? get documentDownloadUrl => _$this._documentDownloadUrl;
  set documentDownloadUrl(String? documentDownloadUrl) =>
      _$this._documentDownloadUrl = documentDownloadUrl;

  BillDetailBuilder() {
    BillDetail._defaults(this);
  }

  BillDetailBuilder get _$this {
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
      _note = $v.note;
      _documentFilename = $v.documentFilename;
      _documentDownloadUrl = $v.documentDownloadUrl;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(BillDetail other) {
    _$v = other as _$BillDetail;
  }

  @override
  void update(void Function(BillDetailBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  BillDetail build() => _build();

  _$BillDetail _build() {
    final _$result = _$v ??
        _$BillDetail._(
          id: BuiltValueNullFieldError.checkNotNull(id, r'BillDetail', 'id'),
          title: BuiltValueNullFieldError.checkNotNull(
              title, r'BillDetail', 'title'),
          amountVnd: BuiltValueNullFieldError.checkNotNull(
              amountVnd, r'BillDetail', 'amountVnd'),
          status: BuiltValueNullFieldError.checkNotNull(
              status, r'BillDetail', 'status'),
          period: BuiltValueNullFieldError.checkNotNull(
              period, r'BillDetail', 'period'),
          dueDate: dueDate,
          issuedAt: BuiltValueNullFieldError.checkNotNull(
              issuedAt, r'BillDetail', 'issuedAt'),
          paidAt: paidAt,
          note: BuiltValueNullFieldError.checkNotNull(
              note, r'BillDetail', 'note'),
          documentFilename: BuiltValueNullFieldError.checkNotNull(
              documentFilename, r'BillDetail', 'documentFilename'),
          documentDownloadUrl: BuiltValueNullFieldError.checkNotNull(
              documentDownloadUrl, r'BillDetail', 'documentDownloadUrl'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
