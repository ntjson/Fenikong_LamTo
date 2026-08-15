// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'report_work_update_photo.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ReportWorkUpdatePhoto extends ReportWorkUpdatePhoto {
  @override
  final int id;
  @override
  final String filename;
  @override
  final KindEnum kind;
  @override
  final String downloadUrl;

  factory _$ReportWorkUpdatePhoto(
          [void Function(ReportWorkUpdatePhotoBuilder)? updates]) =>
      (ReportWorkUpdatePhotoBuilder()..update(updates))._build();

  _$ReportWorkUpdatePhoto._(
      {required this.id,
      required this.filename,
      required this.kind,
      required this.downloadUrl})
      : super._();
  @override
  ReportWorkUpdatePhoto rebuild(
          void Function(ReportWorkUpdatePhotoBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ReportWorkUpdatePhotoBuilder toBuilder() =>
      ReportWorkUpdatePhotoBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ReportWorkUpdatePhoto &&
        id == other.id &&
        filename == other.filename &&
        kind == other.kind &&
        downloadUrl == other.downloadUrl;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, filename.hashCode);
    _$hash = $jc(_$hash, kind.hashCode);
    _$hash = $jc(_$hash, downloadUrl.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ReportWorkUpdatePhoto')
          ..add('id', id)
          ..add('filename', filename)
          ..add('kind', kind)
          ..add('downloadUrl', downloadUrl))
        .toString();
  }
}

class ReportWorkUpdatePhotoBuilder
    implements Builder<ReportWorkUpdatePhoto, ReportWorkUpdatePhotoBuilder> {
  _$ReportWorkUpdatePhoto? _$v;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  String? _filename;
  String? get filename => _$this._filename;
  set filename(String? filename) => _$this._filename = filename;

  KindEnum? _kind;
  KindEnum? get kind => _$this._kind;
  set kind(KindEnum? kind) => _$this._kind = kind;

  String? _downloadUrl;
  String? get downloadUrl => _$this._downloadUrl;
  set downloadUrl(String? downloadUrl) => _$this._downloadUrl = downloadUrl;

  ReportWorkUpdatePhotoBuilder() {
    ReportWorkUpdatePhoto._defaults(this);
  }

  ReportWorkUpdatePhotoBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _id = $v.id;
      _filename = $v.filename;
      _kind = $v.kind;
      _downloadUrl = $v.downloadUrl;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ReportWorkUpdatePhoto other) {
    _$v = other as _$ReportWorkUpdatePhoto;
  }

  @override
  void update(void Function(ReportWorkUpdatePhotoBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ReportWorkUpdatePhoto build() => _build();

  _$ReportWorkUpdatePhoto _build() {
    final _$result = _$v ??
        _$ReportWorkUpdatePhoto._(
          id: BuiltValueNullFieldError.checkNotNull(
              id, r'ReportWorkUpdatePhoto', 'id'),
          filename: BuiltValueNullFieldError.checkNotNull(
              filename, r'ReportWorkUpdatePhoto', 'filename'),
          kind: BuiltValueNullFieldError.checkNotNull(
              kind, r'ReportWorkUpdatePhoto', 'kind'),
          downloadUrl: BuiltValueNullFieldError.checkNotNull(
              downloadUrl, r'ReportWorkUpdatePhoto', 'downloadUrl'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
