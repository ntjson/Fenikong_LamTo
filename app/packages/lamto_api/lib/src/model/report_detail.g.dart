// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'report_detail.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ReportDetail extends ReportDetail {
  @override
  final int id;
  @override
  final String text;
  @override
  final StatusEnum status;
  @override
  final String? declinedReason;
  @override
  final bool isPrivate;
  @override
  final BuiltMap<String, JsonObject?>? openInfoRequest;
  @override
  final String locationPathSnapshot;
  @override
  final String unitLabel;
  @override
  final DateTime createdAt;
  @override
  final String? triageStatus;
  @override
  final String? category;
  @override
  final BuiltList<ReportPhoto> photos;
  @override
  final BuiltList<ReportCase> cases;
  @override
  final BuiltList<int> ledgerEntryIds;

  factory _$ReportDetail([void Function(ReportDetailBuilder)? updates]) =>
      (ReportDetailBuilder()..update(updates))._build();

  _$ReportDetail._(
      {required this.id,
      required this.text,
      required this.status,
      this.declinedReason,
      required this.isPrivate,
      this.openInfoRequest,
      required this.locationPathSnapshot,
      required this.unitLabel,
      required this.createdAt,
      this.triageStatus,
      this.category,
      required this.photos,
      required this.cases,
      required this.ledgerEntryIds})
      : super._();
  @override
  ReportDetail rebuild(void Function(ReportDetailBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ReportDetailBuilder toBuilder() => ReportDetailBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ReportDetail &&
        id == other.id &&
        text == other.text &&
        status == other.status &&
        declinedReason == other.declinedReason &&
        isPrivate == other.isPrivate &&
        openInfoRequest == other.openInfoRequest &&
        locationPathSnapshot == other.locationPathSnapshot &&
        unitLabel == other.unitLabel &&
        createdAt == other.createdAt &&
        triageStatus == other.triageStatus &&
        category == other.category &&
        photos == other.photos &&
        cases == other.cases &&
        ledgerEntryIds == other.ledgerEntryIds;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, text.hashCode);
    _$hash = $jc(_$hash, status.hashCode);
    _$hash = $jc(_$hash, declinedReason.hashCode);
    _$hash = $jc(_$hash, isPrivate.hashCode);
    _$hash = $jc(_$hash, openInfoRequest.hashCode);
    _$hash = $jc(_$hash, locationPathSnapshot.hashCode);
    _$hash = $jc(_$hash, unitLabel.hashCode);
    _$hash = $jc(_$hash, createdAt.hashCode);
    _$hash = $jc(_$hash, triageStatus.hashCode);
    _$hash = $jc(_$hash, category.hashCode);
    _$hash = $jc(_$hash, photos.hashCode);
    _$hash = $jc(_$hash, cases.hashCode);
    _$hash = $jc(_$hash, ledgerEntryIds.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ReportDetail')
          ..add('id', id)
          ..add('text', text)
          ..add('status', status)
          ..add('declinedReason', declinedReason)
          ..add('isPrivate', isPrivate)
          ..add('openInfoRequest', openInfoRequest)
          ..add('locationPathSnapshot', locationPathSnapshot)
          ..add('unitLabel', unitLabel)
          ..add('createdAt', createdAt)
          ..add('triageStatus', triageStatus)
          ..add('category', category)
          ..add('photos', photos)
          ..add('cases', cases)
          ..add('ledgerEntryIds', ledgerEntryIds))
        .toString();
  }
}

class ReportDetailBuilder
    implements Builder<ReportDetail, ReportDetailBuilder> {
  _$ReportDetail? _$v;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  String? _text;
  String? get text => _$this._text;
  set text(String? text) => _$this._text = text;

  StatusEnum? _status;
  StatusEnum? get status => _$this._status;
  set status(StatusEnum? status) => _$this._status = status;

  String? _declinedReason;
  String? get declinedReason => _$this._declinedReason;
  set declinedReason(String? declinedReason) =>
      _$this._declinedReason = declinedReason;

  bool? _isPrivate;
  bool? get isPrivate => _$this._isPrivate;
  set isPrivate(bool? isPrivate) => _$this._isPrivate = isPrivate;

  MapBuilder<String, JsonObject?>? _openInfoRequest;
  MapBuilder<String, JsonObject?> get openInfoRequest =>
      _$this._openInfoRequest ??= MapBuilder<String, JsonObject?>();
  set openInfoRequest(MapBuilder<String, JsonObject?>? openInfoRequest) =>
      _$this._openInfoRequest = openInfoRequest;

  String? _locationPathSnapshot;
  String? get locationPathSnapshot => _$this._locationPathSnapshot;
  set locationPathSnapshot(String? locationPathSnapshot) =>
      _$this._locationPathSnapshot = locationPathSnapshot;

  String? _unitLabel;
  String? get unitLabel => _$this._unitLabel;
  set unitLabel(String? unitLabel) => _$this._unitLabel = unitLabel;

  DateTime? _createdAt;
  DateTime? get createdAt => _$this._createdAt;
  set createdAt(DateTime? createdAt) => _$this._createdAt = createdAt;

  String? _triageStatus;
  String? get triageStatus => _$this._triageStatus;
  set triageStatus(String? triageStatus) => _$this._triageStatus = triageStatus;

  String? _category;
  String? get category => _$this._category;
  set category(String? category) => _$this._category = category;

  ListBuilder<ReportPhoto>? _photos;
  ListBuilder<ReportPhoto> get photos =>
      _$this._photos ??= ListBuilder<ReportPhoto>();
  set photos(ListBuilder<ReportPhoto>? photos) => _$this._photos = photos;

  ListBuilder<ReportCase>? _cases;
  ListBuilder<ReportCase> get cases =>
      _$this._cases ??= ListBuilder<ReportCase>();
  set cases(ListBuilder<ReportCase>? cases) => _$this._cases = cases;

  ListBuilder<int>? _ledgerEntryIds;
  ListBuilder<int> get ledgerEntryIds =>
      _$this._ledgerEntryIds ??= ListBuilder<int>();
  set ledgerEntryIds(ListBuilder<int>? ledgerEntryIds) =>
      _$this._ledgerEntryIds = ledgerEntryIds;

  ReportDetailBuilder() {
    ReportDetail._defaults(this);
  }

  ReportDetailBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _id = $v.id;
      _text = $v.text;
      _status = $v.status;
      _declinedReason = $v.declinedReason;
      _isPrivate = $v.isPrivate;
      _openInfoRequest = $v.openInfoRequest?.toBuilder();
      _locationPathSnapshot = $v.locationPathSnapshot;
      _unitLabel = $v.unitLabel;
      _createdAt = $v.createdAt;
      _triageStatus = $v.triageStatus;
      _category = $v.category;
      _photos = $v.photos.toBuilder();
      _cases = $v.cases.toBuilder();
      _ledgerEntryIds = $v.ledgerEntryIds.toBuilder();
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ReportDetail other) {
    _$v = other as _$ReportDetail;
  }

  @override
  void update(void Function(ReportDetailBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ReportDetail build() => _build();

  _$ReportDetail _build() {
    _$ReportDetail _$result;
    try {
      _$result = _$v ??
          _$ReportDetail._(
            id: BuiltValueNullFieldError.checkNotNull(
                id, r'ReportDetail', 'id'),
            text: BuiltValueNullFieldError.checkNotNull(
                text, r'ReportDetail', 'text'),
            status: BuiltValueNullFieldError.checkNotNull(
                status, r'ReportDetail', 'status'),
            declinedReason: declinedReason,
            isPrivate: BuiltValueNullFieldError.checkNotNull(
                isPrivate, r'ReportDetail', 'isPrivate'),
            openInfoRequest: _openInfoRequest?.build(),
            locationPathSnapshot: BuiltValueNullFieldError.checkNotNull(
                locationPathSnapshot, r'ReportDetail', 'locationPathSnapshot'),
            unitLabel: BuiltValueNullFieldError.checkNotNull(
                unitLabel, r'ReportDetail', 'unitLabel'),
            createdAt: BuiltValueNullFieldError.checkNotNull(
                createdAt, r'ReportDetail', 'createdAt'),
            triageStatus: triageStatus,
            category: category,
            photos: photos.build(),
            cases: cases.build(),
            ledgerEntryIds: ledgerEntryIds.build(),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'openInfoRequest';
        _openInfoRequest?.build();

        _$failedField = 'photos';
        photos.build();
        _$failedField = 'cases';
        cases.build();
        _$failedField = 'ledgerEntryIds';
        ledgerEntryIds.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ReportDetail', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
