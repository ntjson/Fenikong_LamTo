// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ledger_document.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$LedgerDocument extends LedgerDocument {
  @override
  final String kind;
  @override
  final String contentType;
  @override
  final String filename;
  @override
  final String sha256;
  @override
  final String downloadUrl;

  factory _$LedgerDocument([void Function(LedgerDocumentBuilder)? updates]) =>
      (LedgerDocumentBuilder()..update(updates))._build();

  _$LedgerDocument._(
      {required this.kind,
      required this.contentType,
      required this.filename,
      required this.sha256,
      required this.downloadUrl})
      : super._();
  @override
  LedgerDocument rebuild(void Function(LedgerDocumentBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  LedgerDocumentBuilder toBuilder() => LedgerDocumentBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is LedgerDocument &&
        kind == other.kind &&
        contentType == other.contentType &&
        filename == other.filename &&
        sha256 == other.sha256 &&
        downloadUrl == other.downloadUrl;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, kind.hashCode);
    _$hash = $jc(_$hash, contentType.hashCode);
    _$hash = $jc(_$hash, filename.hashCode);
    _$hash = $jc(_$hash, sha256.hashCode);
    _$hash = $jc(_$hash, downloadUrl.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'LedgerDocument')
          ..add('kind', kind)
          ..add('contentType', contentType)
          ..add('filename', filename)
          ..add('sha256', sha256)
          ..add('downloadUrl', downloadUrl))
        .toString();
  }
}

class LedgerDocumentBuilder
    implements Builder<LedgerDocument, LedgerDocumentBuilder> {
  _$LedgerDocument? _$v;

  String? _kind;
  String? get kind => _$this._kind;
  set kind(String? kind) => _$this._kind = kind;

  String? _contentType;
  String? get contentType => _$this._contentType;
  set contentType(String? contentType) => _$this._contentType = contentType;

  String? _filename;
  String? get filename => _$this._filename;
  set filename(String? filename) => _$this._filename = filename;

  String? _sha256;
  String? get sha256 => _$this._sha256;
  set sha256(String? sha256) => _$this._sha256 = sha256;

  String? _downloadUrl;
  String? get downloadUrl => _$this._downloadUrl;
  set downloadUrl(String? downloadUrl) => _$this._downloadUrl = downloadUrl;

  LedgerDocumentBuilder() {
    LedgerDocument._defaults(this);
  }

  LedgerDocumentBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _kind = $v.kind;
      _contentType = $v.contentType;
      _filename = $v.filename;
      _sha256 = $v.sha256;
      _downloadUrl = $v.downloadUrl;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(LedgerDocument other) {
    _$v = other as _$LedgerDocument;
  }

  @override
  void update(void Function(LedgerDocumentBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  LedgerDocument build() => _build();

  _$LedgerDocument _build() {
    final _$result = _$v ??
        _$LedgerDocument._(
          kind: BuiltValueNullFieldError.checkNotNull(
              kind, r'LedgerDocument', 'kind'),
          contentType: BuiltValueNullFieldError.checkNotNull(
              contentType, r'LedgerDocument', 'contentType'),
          filename: BuiltValueNullFieldError.checkNotNull(
              filename, r'LedgerDocument', 'filename'),
          sha256: BuiltValueNullFieldError.checkNotNull(
              sha256, r'LedgerDocument', 'sha256'),
          downloadUrl: BuiltValueNullFieldError.checkNotNull(
              downloadUrl, r'LedgerDocument', 'downloadUrl'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
