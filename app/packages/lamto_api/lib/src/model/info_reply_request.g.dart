// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'info_reply_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$InfoReplyRequest extends InfoReplyRequest {
  @override
  final String text;

  factory _$InfoReplyRequest(
          [void Function(InfoReplyRequestBuilder)? updates]) =>
      (InfoReplyRequestBuilder()..update(updates))._build();

  _$InfoReplyRequest._({required this.text}) : super._();
  @override
  InfoReplyRequest rebuild(void Function(InfoReplyRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  InfoReplyRequestBuilder toBuilder() =>
      InfoReplyRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is InfoReplyRequest && text == other.text;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, text.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'InfoReplyRequest')..add('text', text))
        .toString();
  }
}

class InfoReplyRequestBuilder
    implements Builder<InfoReplyRequest, InfoReplyRequestBuilder> {
  _$InfoReplyRequest? _$v;

  String? _text;
  String? get text => _$this._text;
  set text(String? text) => _$this._text = text;

  InfoReplyRequestBuilder() {
    InfoReplyRequest._defaults(this);
  }

  InfoReplyRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _text = $v.text;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(InfoReplyRequest other) {
    _$v = other as _$InfoReplyRequest;
  }

  @override
  void update(void Function(InfoReplyRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  InfoReplyRequest build() => _build();

  _$InfoReplyRequest _build() {
    final _$result = _$v ??
        _$InfoReplyRequest._(
          text: BuiltValueNullFieldError.checkNotNull(
              text, r'InfoReplyRequest', 'text'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
