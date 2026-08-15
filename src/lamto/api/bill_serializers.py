from rest_framework import serializers

from lamto.billing.models import Bill


class BillSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    amount_vnd = serializers.IntegerField()
    status = serializers.ChoiceField(choices=Bill.Status.choices)
    period = serializers.CharField(allow_blank=True)
    due_date = serializers.DateField(allow_null=True)
    issued_at = serializers.DateTimeField()
    paid_at = serializers.DateTimeField(allow_null=True)


class BillDetailSerializer(BillSummarySerializer):
    note = serializers.CharField(allow_blank=True)
    document_filename = serializers.CharField()
    document_download_url = serializers.CharField()


class BillConfirmPaymentRequestSerializer(serializers.Serializer):
    reference = serializers.CharField(max_length=64, trim_whitespace=False)
