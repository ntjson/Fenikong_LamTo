// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'report_case.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ReportCase extends ReportCase {
  @override
  final int id;
  @override
  final String category;
  @override
  final String urgency;
  @override
  final DateTime deadlineAt;
  @override
  final bool active;
  @override
  final DateTime? completedAt;
  @override
  final DateTime? closedAt;
  @override
  final BuiltList<ReportWorkUpdate> updates;
  @override
  final bool canRate;

  factory _$ReportCase([void Function(ReportCaseBuilder)? updates]) =>
      (ReportCaseBuilder()..update(updates))._build();

  _$ReportCase._(
      {required this.id,
      required this.category,
      required this.urgency,
      required this.deadlineAt,
      required this.active,
      this.completedAt,
      this.closedAt,
      required this.updates,
      required this.canRate})
      : super._();
  @override
  ReportCase rebuild(void Function(ReportCaseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ReportCaseBuilder toBuilder() => ReportCaseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ReportCase &&
        id == other.id &&
        category == other.category &&
        urgency == other.urgency &&
        deadlineAt == other.deadlineAt &&
        active == other.active &&
        completedAt == other.completedAt &&
        closedAt == other.closedAt &&
        updates == other.updates &&
        canRate == other.canRate;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, category.hashCode);
    _$hash = $jc(_$hash, urgency.hashCode);
    _$hash = $jc(_$hash, deadlineAt.hashCode);
    _$hash = $jc(_$hash, active.hashCode);
    _$hash = $jc(_$hash, completedAt.hashCode);
    _$hash = $jc(_$hash, closedAt.hashCode);
    _$hash = $jc(_$hash, updates.hashCode);
    _$hash = $jc(_$hash, canRate.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ReportCase')
          ..add('id', id)
          ..add('category', category)
          ..add('urgency', urgency)
          ..add('deadlineAt', deadlineAt)
          ..add('active', active)
          ..add('completedAt', completedAt)
          ..add('closedAt', closedAt)
          ..add('updates', updates)
          ..add('canRate', canRate))
        .toString();
  }
}

class ReportCaseBuilder implements Builder<ReportCase, ReportCaseBuilder> {
  _$ReportCase? _$v;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  String? _category;
  String? get category => _$this._category;
  set category(String? category) => _$this._category = category;

  String? _urgency;
  String? get urgency => _$this._urgency;
  set urgency(String? urgency) => _$this._urgency = urgency;

  DateTime? _deadlineAt;
  DateTime? get deadlineAt => _$this._deadlineAt;
  set deadlineAt(DateTime? deadlineAt) => _$this._deadlineAt = deadlineAt;

  bool? _active;
  bool? get active => _$this._active;
  set active(bool? active) => _$this._active = active;

  DateTime? _completedAt;
  DateTime? get completedAt => _$this._completedAt;
  set completedAt(DateTime? completedAt) => _$this._completedAt = completedAt;

  DateTime? _closedAt;
  DateTime? get closedAt => _$this._closedAt;
  set closedAt(DateTime? closedAt) => _$this._closedAt = closedAt;

  ListBuilder<ReportWorkUpdate>? _updates;
  ListBuilder<ReportWorkUpdate> get updates =>
      _$this._updates ??= ListBuilder<ReportWorkUpdate>();
  set updates(ListBuilder<ReportWorkUpdate>? updates) =>
      _$this._updates = updates;

  bool? _canRate;
  bool? get canRate => _$this._canRate;
  set canRate(bool? canRate) => _$this._canRate = canRate;

  ReportCaseBuilder() {
    ReportCase._defaults(this);
  }

  ReportCaseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _id = $v.id;
      _category = $v.category;
      _urgency = $v.urgency;
      _deadlineAt = $v.deadlineAt;
      _active = $v.active;
      _completedAt = $v.completedAt;
      _closedAt = $v.closedAt;
      _updates = $v.updates.toBuilder();
      _canRate = $v.canRate;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ReportCase other) {
    _$v = other as _$ReportCase;
  }

  @override
  void update(void Function(ReportCaseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ReportCase build() => _build();

  _$ReportCase _build() {
    _$ReportCase _$result;
    try {
      _$result = _$v ??
          _$ReportCase._(
            id: BuiltValueNullFieldError.checkNotNull(id, r'ReportCase', 'id'),
            category: BuiltValueNullFieldError.checkNotNull(
                category, r'ReportCase', 'category'),
            urgency: BuiltValueNullFieldError.checkNotNull(
                urgency, r'ReportCase', 'urgency'),
            deadlineAt: BuiltValueNullFieldError.checkNotNull(
                deadlineAt, r'ReportCase', 'deadlineAt'),
            active: BuiltValueNullFieldError.checkNotNull(
                active, r'ReportCase', 'active'),
            completedAt: completedAt,
            closedAt: closedAt,
            updates: updates.build(),
            canRate: BuiltValueNullFieldError.checkNotNull(
                canRate, r'ReportCase', 'canRate'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'updates';
        updates.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ReportCase', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
