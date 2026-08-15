// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'recognition_outcome.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$RecognitionOutcome extends RecognitionOutcome {
  @override
  final bool matched;
  @override
  final String displayName;
  @override
  final String unitLabel;
  @override
  final String direction;
  @override
  final double? score;

  factory _$RecognitionOutcome(
          [void Function(RecognitionOutcomeBuilder)? updates]) =>
      (RecognitionOutcomeBuilder()..update(updates))._build();

  _$RecognitionOutcome._(
      {required this.matched,
      required this.displayName,
      required this.unitLabel,
      required this.direction,
      this.score})
      : super._();
  @override
  RecognitionOutcome rebuild(
          void Function(RecognitionOutcomeBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  RecognitionOutcomeBuilder toBuilder() =>
      RecognitionOutcomeBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is RecognitionOutcome &&
        matched == other.matched &&
        displayName == other.displayName &&
        unitLabel == other.unitLabel &&
        direction == other.direction &&
        score == other.score;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, matched.hashCode);
    _$hash = $jc(_$hash, displayName.hashCode);
    _$hash = $jc(_$hash, unitLabel.hashCode);
    _$hash = $jc(_$hash, direction.hashCode);
    _$hash = $jc(_$hash, score.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'RecognitionOutcome')
          ..add('matched', matched)
          ..add('displayName', displayName)
          ..add('unitLabel', unitLabel)
          ..add('direction', direction)
          ..add('score', score))
        .toString();
  }
}

class RecognitionOutcomeBuilder
    implements Builder<RecognitionOutcome, RecognitionOutcomeBuilder> {
  _$RecognitionOutcome? _$v;

  bool? _matched;
  bool? get matched => _$this._matched;
  set matched(bool? matched) => _$this._matched = matched;

  String? _displayName;
  String? get displayName => _$this._displayName;
  set displayName(String? displayName) => _$this._displayName = displayName;

  String? _unitLabel;
  String? get unitLabel => _$this._unitLabel;
  set unitLabel(String? unitLabel) => _$this._unitLabel = unitLabel;

  String? _direction;
  String? get direction => _$this._direction;
  set direction(String? direction) => _$this._direction = direction;

  double? _score;
  double? get score => _$this._score;
  set score(double? score) => _$this._score = score;

  RecognitionOutcomeBuilder() {
    RecognitionOutcome._defaults(this);
  }

  RecognitionOutcomeBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _matched = $v.matched;
      _displayName = $v.displayName;
      _unitLabel = $v.unitLabel;
      _direction = $v.direction;
      _score = $v.score;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(RecognitionOutcome other) {
    _$v = other as _$RecognitionOutcome;
  }

  @override
  void update(void Function(RecognitionOutcomeBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  RecognitionOutcome build() => _build();

  _$RecognitionOutcome _build() {
    final _$result = _$v ??
        _$RecognitionOutcome._(
          matched: BuiltValueNullFieldError.checkNotNull(
              matched, r'RecognitionOutcome', 'matched'),
          displayName: BuiltValueNullFieldError.checkNotNull(
              displayName, r'RecognitionOutcome', 'displayName'),
          unitLabel: BuiltValueNullFieldError.checkNotNull(
              unitLabel, r'RecognitionOutcome', 'unitLabel'),
          direction: BuiltValueNullFieldError.checkNotNull(
              direction, r'RecognitionOutcome', 'direction'),
          score: score,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
