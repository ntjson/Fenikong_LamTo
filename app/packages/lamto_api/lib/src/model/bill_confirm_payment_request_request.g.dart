// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'bill_confirm_payment_request_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$BillConfirmPaymentRequestRequest
    extends BillConfirmPaymentRequestRequest {
  @override
  final String reference;

  factory _$BillConfirmPaymentRequestRequest(
          [void Function(BillConfirmPaymentRequestRequestBuilder)? updates]) =>
      (BillConfirmPaymentRequestRequestBuilder()..update(updates))._build();

  _$BillConfirmPaymentRequestRequest._({required this.reference}) : super._();
  @override
  BillConfirmPaymentRequestRequest rebuild(
          void Function(BillConfirmPaymentRequestRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  BillConfirmPaymentRequestRequestBuilder toBuilder() =>
      BillConfirmPaymentRequestRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is BillConfirmPaymentRequestRequest &&
        reference == other.reference;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, reference.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'BillConfirmPaymentRequestRequest')
          ..add('reference', reference))
        .toString();
  }
}

class BillConfirmPaymentRequestRequestBuilder
    implements
        Builder<BillConfirmPaymentRequestRequest,
            BillConfirmPaymentRequestRequestBuilder> {
  _$BillConfirmPaymentRequestRequest? _$v;

  String? _reference;
  String? get reference => _$this._reference;
  set reference(String? reference) => _$this._reference = reference;

  BillConfirmPaymentRequestRequestBuilder() {
    BillConfirmPaymentRequestRequest._defaults(this);
  }

  BillConfirmPaymentRequestRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _reference = $v.reference;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(BillConfirmPaymentRequestRequest other) {
    _$v = other as _$BillConfirmPaymentRequestRequest;
  }

  @override
  void update(void Function(BillConfirmPaymentRequestRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  BillConfirmPaymentRequestRequest build() => _build();

  _$BillConfirmPaymentRequestRequest _build() {
    final _$result = _$v ??
        _$BillConfirmPaymentRequestRequest._(
          reference: BuiltValueNullFieldError.checkNotNull(
              reference, r'BillConfirmPaymentRequestRequest', 'reference'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
