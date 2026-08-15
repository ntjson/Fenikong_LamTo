// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'report_photo.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ReportPhoto extends ReportPhoto {
  @override
  final int id;
  @override
  final String filename;
  @override
  final String sha256;
  @override
  final String downloadUrl;

  factory _$ReportPhoto([void Function(ReportPhotoBuilder)? updates]) =>
      (ReportPhotoBuilder()..update(updates))._build();

  _$ReportPhoto._(
      {required this.id,
      required this.filename,
      required this.sha256,
      required this.downloadUrl})
      : super._();
  @override
  ReportPhoto rebuild(void Function(ReportPhotoBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ReportPhotoBuilder toBuilder() => ReportPhotoBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ReportPhoto &&
        id == other.id &&
        filename == other.filename &&
        sha256 == other.sha256 &&
        downloadUrl == other.downloadUrl;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, filename.hashCode);
    _$hash = $jc(_$hash, sha256.hashCode);
    _$hash = $jc(_$hash, downloadUrl.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ReportPhoto')
          ..add('id', id)
          ..add('filename', filename)
          ..add('sha256', sha256)
          ..add('downloadUrl', downloadUrl))
        .toString();
  }
}

class ReportPhotoBuilder implements Builder<ReportPhoto, ReportPhotoBuilder> {
  _$ReportPhoto? _$v;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  String? _filename;
  String? get filename => _$this._filename;
  set filename(String? filename) => _$this._filename = filename;

  String? _sha256;
  String? get sha256 => _$this._sha256;
  set sha256(String? sha256) => _$this._sha256 = sha256;

  String? _downloadUrl;
  String? get downloadUrl => _$this._downloadUrl;
  set downloadUrl(String? downloadUrl) => _$this._downloadUrl = downloadUrl;

  ReportPhotoBuilder() {
    ReportPhoto._defaults(this);
  }

  ReportPhotoBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _id = $v.id;
      _filename = $v.filename;
      _sha256 = $v.sha256;
      _downloadUrl = $v.downloadUrl;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ReportPhoto other) {
    _$v = other as _$ReportPhoto;
  }

  @override
  void update(void Function(ReportPhotoBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ReportPhoto build() => _build();

  _$ReportPhoto _build() {
    final _$result = _$v ??
        _$ReportPhoto._(
          id: BuiltValueNullFieldError.checkNotNull(id, r'ReportPhoto', 'id'),
          filename: BuiltValueNullFieldError.checkNotNull(
              filename, r'ReportPhoto', 'filename'),
          sha256: BuiltValueNullFieldError.checkNotNull(
              sha256, r'ReportPhoto', 'sha256'),
          downloadUrl: BuiltValueNullFieldError.checkNotNull(
              downloadUrl, r'ReportPhoto', 'downloadUrl'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
