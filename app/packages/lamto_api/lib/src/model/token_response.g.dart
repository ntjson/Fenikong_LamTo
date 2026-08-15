// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'token_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$TokenResponse extends TokenResponse {
  @override
  final String token;
  @override
  final DateTime expiry;

  factory _$TokenResponse([void Function(TokenResponseBuilder)? updates]) =>
      (TokenResponseBuilder()..update(updates))._build();

  _$TokenResponse._({required this.token, required this.expiry}) : super._();
  @override
  TokenResponse rebuild(void Function(TokenResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  TokenResponseBuilder toBuilder() => TokenResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is TokenResponse &&
        token == other.token &&
        expiry == other.expiry;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, token.hashCode);
    _$hash = $jc(_$hash, expiry.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'TokenResponse')
          ..add('token', token)
          ..add('expiry', expiry))
        .toString();
  }
}

class TokenResponseBuilder
    implements Builder<TokenResponse, TokenResponseBuilder> {
  _$TokenResponse? _$v;

  String? _token;
  String? get token => _$this._token;
  set token(String? token) => _$this._token = token;

  DateTime? _expiry;
  DateTime? get expiry => _$this._expiry;
  set expiry(DateTime? expiry) => _$this._expiry = expiry;

  TokenResponseBuilder() {
    TokenResponse._defaults(this);
  }

  TokenResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _token = $v.token;
      _expiry = $v.expiry;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(TokenResponse other) {
    _$v = other as _$TokenResponse;
  }

  @override
  void update(void Function(TokenResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  TokenResponse build() => _build();

  _$TokenResponse _build() {
    final _$result = _$v ??
        _$TokenResponse._(
          token: BuiltValueNullFieldError.checkNotNull(
              token, r'TokenResponse', 'token'),
          expiry: BuiltValueNullFieldError.checkNotNull(
              expiry, r'TokenResponse', 'expiry'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
