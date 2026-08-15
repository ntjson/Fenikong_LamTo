// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'info_reply_result.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$InfoReplyResult extends InfoReplyResult {
  @override
  final int reportId;
  @override
  final StatusEnum status;

  factory _$InfoReplyResult([void Function(InfoReplyResultBuilder)? updates]) =>
      (InfoReplyResultBuilder()..update(updates))._build();

  _$InfoReplyResult._({required this.reportId, required this.status})
      : super._();
  @override
  InfoReplyResult rebuild(void Function(InfoReplyResultBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  InfoReplyResultBuilder toBuilder() => InfoReplyResultBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is InfoReplyResult &&
        reportId == other.reportId &&
        status == other.status;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, reportId.hashCode);
    _$hash = $jc(_$hash, status.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'InfoReplyResult')
          ..add('reportId', reportId)
          ..add('status', status))
        .toString();
  }
}

class InfoReplyResultBuilder
    implements Builder<InfoReplyResult, InfoReplyResultBuilder> {
  _$InfoReplyResult? _$v;

  int? _reportId;
  int? get reportId => _$this._reportId;
  set reportId(int? reportId) => _$this._reportId = reportId;

  StatusEnum? _status;
  StatusEnum? get status => _$this._status;
  set status(StatusEnum? status) => _$this._status = status;

  InfoReplyResultBuilder() {
    InfoReplyResult._defaults(this);
  }

  InfoReplyResultBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _reportId = $v.reportId;
      _status = $v.status;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(InfoReplyResult other) {
    _$v = other as _$InfoReplyResult;
  }

  @override
  void update(void Function(InfoReplyResultBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  InfoReplyResult build() => _build();

  _$InfoReplyResult _build() {
    final _$result = _$v ??
        _$InfoReplyResult._(
          reportId: BuiltValueNullFieldError.checkNotNull(
              reportId, r'InfoReplyResult', 'reportId'),
          status: BuiltValueNullFieldError.checkNotNull(
              status, r'InfoReplyResult', 'status'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
