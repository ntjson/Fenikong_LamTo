// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'proposal_version.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ProposalVersion extends ProposalVersion {
  @override
  final int number;
  @override
  final DateTime publishedAt;
  @override
  final String evidenceLevel;
  @override
  final BuiltList<ProposalSupportingDocument> supportingDocuments;

  factory _$ProposalVersion([void Function(ProposalVersionBuilder)? updates]) =>
      (ProposalVersionBuilder()..update(updates))._build();

  _$ProposalVersion._(
      {required this.number,
      required this.publishedAt,
      required this.evidenceLevel,
      required this.supportingDocuments})
      : super._();
  @override
  ProposalVersion rebuild(void Function(ProposalVersionBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ProposalVersionBuilder toBuilder() => ProposalVersionBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ProposalVersion &&
        number == other.number &&
        publishedAt == other.publishedAt &&
        evidenceLevel == other.evidenceLevel &&
        supportingDocuments == other.supportingDocuments;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, number.hashCode);
    _$hash = $jc(_$hash, publishedAt.hashCode);
    _$hash = $jc(_$hash, evidenceLevel.hashCode);
    _$hash = $jc(_$hash, supportingDocuments.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ProposalVersion')
          ..add('number', number)
          ..add('publishedAt', publishedAt)
          ..add('evidenceLevel', evidenceLevel)
          ..add('supportingDocuments', supportingDocuments))
        .toString();
  }
}

class ProposalVersionBuilder
    implements Builder<ProposalVersion, ProposalVersionBuilder> {
  _$ProposalVersion? _$v;

  int? _number;
  int? get number => _$this._number;
  set number(int? number) => _$this._number = number;

  DateTime? _publishedAt;
  DateTime? get publishedAt => _$this._publishedAt;
  set publishedAt(DateTime? publishedAt) => _$this._publishedAt = publishedAt;

  String? _evidenceLevel;
  String? get evidenceLevel => _$this._evidenceLevel;
  set evidenceLevel(String? evidenceLevel) =>
      _$this._evidenceLevel = evidenceLevel;

  ListBuilder<ProposalSupportingDocument>? _supportingDocuments;
  ListBuilder<ProposalSupportingDocument> get supportingDocuments =>
      _$this._supportingDocuments ??= ListBuilder<ProposalSupportingDocument>();
  set supportingDocuments(
          ListBuilder<ProposalSupportingDocument>? supportingDocuments) =>
      _$this._supportingDocuments = supportingDocuments;

  ProposalVersionBuilder() {
    ProposalVersion._defaults(this);
  }

  ProposalVersionBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _number = $v.number;
      _publishedAt = $v.publishedAt;
      _evidenceLevel = $v.evidenceLevel;
      _supportingDocuments = $v.supportingDocuments.toBuilder();
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ProposalVersion other) {
    _$v = other as _$ProposalVersion;
  }

  @override
  void update(void Function(ProposalVersionBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ProposalVersion build() => _build();

  _$ProposalVersion _build() {
    _$ProposalVersion _$result;
    try {
      _$result = _$v ??
          _$ProposalVersion._(
            number: BuiltValueNullFieldError.checkNotNull(
                number, r'ProposalVersion', 'number'),
            publishedAt: BuiltValueNullFieldError.checkNotNull(
                publishedAt, r'ProposalVersion', 'publishedAt'),
            evidenceLevel: BuiltValueNullFieldError.checkNotNull(
                evidenceLevel, r'ProposalVersion', 'evidenceLevel'),
            supportingDocuments: supportingDocuments.build(),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'supportingDocuments';
        supportingDocuments.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ProposalVersion', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
