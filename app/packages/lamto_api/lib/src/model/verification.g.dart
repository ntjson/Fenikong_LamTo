// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'verification.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$Verification extends Verification {
  @override
  final String decision;
  @override
  final String verifiedBy;
  @override
  final DateTime verifiedAt;

  factory _$Verification([void Function(VerificationBuilder)? updates]) =>
      (VerificationBuilder()..update(updates))._build();

  _$Verification._(
      {required this.decision,
      required this.verifiedBy,
      required this.verifiedAt})
      : super._();
  @override
  Verification rebuild(void Function(VerificationBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  VerificationBuilder toBuilder() => VerificationBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is Verification &&
        decision == other.decision &&
        verifiedBy == other.verifiedBy &&
        verifiedAt == other.verifiedAt;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, decision.hashCode);
    _$hash = $jc(_$hash, verifiedBy.hashCode);
    _$hash = $jc(_$hash, verifiedAt.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'Verification')
          ..add('decision', decision)
          ..add('verifiedBy', verifiedBy)
          ..add('verifiedAt', verifiedAt))
        .toString();
  }
}

class VerificationBuilder
    implements Builder<Verification, VerificationBuilder> {
  _$Verification? _$v;

  String? _decision;
  String? get decision => _$this._decision;
  set decision(String? decision) => _$this._decision = decision;

  String? _verifiedBy;
  String? get verifiedBy => _$this._verifiedBy;
  set verifiedBy(String? verifiedBy) => _$this._verifiedBy = verifiedBy;

  DateTime? _verifiedAt;
  DateTime? get verifiedAt => _$this._verifiedAt;
  set verifiedAt(DateTime? verifiedAt) => _$this._verifiedAt = verifiedAt;

  VerificationBuilder() {
    Verification._defaults(this);
  }

  VerificationBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _decision = $v.decision;
      _verifiedBy = $v.verifiedBy;
      _verifiedAt = $v.verifiedAt;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(Verification other) {
    _$v = other as _$Verification;
  }

  @override
  void update(void Function(VerificationBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  Verification build() => _build();

  _$Verification _build() {
    final _$result = _$v ??
        _$Verification._(
          decision: BuiltValueNullFieldError.checkNotNull(
              decision, r'Verification', 'decision'),
          verifiedBy: BuiltValueNullFieldError.checkNotNull(
              verifiedBy, r'Verification', 'verifiedBy'),
          verifiedAt: BuiltValueNullFieldError.checkNotNull(
              verifiedAt, r'Verification', 'verifiedAt'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
