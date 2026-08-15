// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'face_enrollment.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$FaceEnrollment extends FaceEnrollment {
  @override
  final String status;
  @override
  final DateTime submittedAt;
  @override
  final String reviewNote;

  factory _$FaceEnrollment([void Function(FaceEnrollmentBuilder)? updates]) =>
      (FaceEnrollmentBuilder()..update(updates))._build();

  _$FaceEnrollment._(
      {required this.status,
      required this.submittedAt,
      required this.reviewNote})
      : super._();
  @override
  FaceEnrollment rebuild(void Function(FaceEnrollmentBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  FaceEnrollmentBuilder toBuilder() => FaceEnrollmentBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is FaceEnrollment &&
        status == other.status &&
        submittedAt == other.submittedAt &&
        reviewNote == other.reviewNote;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, status.hashCode);
    _$hash = $jc(_$hash, submittedAt.hashCode);
    _$hash = $jc(_$hash, reviewNote.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'FaceEnrollment')
          ..add('status', status)
          ..add('submittedAt', submittedAt)
          ..add('reviewNote', reviewNote))
        .toString();
  }
}

class FaceEnrollmentBuilder
    implements Builder<FaceEnrollment, FaceEnrollmentBuilder> {
  _$FaceEnrollment? _$v;

  String? _status;
  String? get status => _$this._status;
  set status(String? status) => _$this._status = status;

  DateTime? _submittedAt;
  DateTime? get submittedAt => _$this._submittedAt;
  set submittedAt(DateTime? submittedAt) => _$this._submittedAt = submittedAt;

  String? _reviewNote;
  String? get reviewNote => _$this._reviewNote;
  set reviewNote(String? reviewNote) => _$this._reviewNote = reviewNote;

  FaceEnrollmentBuilder() {
    FaceEnrollment._defaults(this);
  }

  FaceEnrollmentBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _status = $v.status;
      _submittedAt = $v.submittedAt;
      _reviewNote = $v.reviewNote;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(FaceEnrollment other) {
    _$v = other as _$FaceEnrollment;
  }

  @override
  void update(void Function(FaceEnrollmentBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  FaceEnrollment build() => _build();

  _$FaceEnrollment _build() {
    final _$result = _$v ??
        _$FaceEnrollment._(
          status: BuiltValueNullFieldError.checkNotNull(
              status, r'FaceEnrollment', 'status'),
          submittedAt: BuiltValueNullFieldError.checkNotNull(
              submittedAt, r'FaceEnrollment', 'submittedAt'),
          reviewNote: BuiltValueNullFieldError.checkNotNull(
              reviewNote, r'FaceEnrollment', 'reviewNote'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
