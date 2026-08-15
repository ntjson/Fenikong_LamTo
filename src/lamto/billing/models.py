import secrets

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from lamto.accounts.models import Building
from lamto.documents.models import DocumentVersion


def new_reference() -> str:
    """Unguessable per-bill reference; also the payload of the LamTo bill QR."""
    return secrets.token_urlsafe(12)


class Bill(models.Model):
    class Status(models.TextChoices):
        ISSUED = "ISSUED", _("Issued")
        PAID = "PAID", _("Paid")
        VOID = "VOID", _("Void")

    class PaymentSource(models.TextChoices):
        SELF_ATTESTED_DEMO = "SELF_ATTESTED_DEMO", "Resident self-attested (demo)"
        BANK_WEBHOOK = "BANK_WEBHOOK", "Bank webhook"
        MANAGEMENT_MANUAL = "MANAGEMENT_MANUAL", "Management manual"

    building = models.ForeignKey(Building, on_delete=models.PROTECT, related_name="bills")
    resident = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="bills"
    )
    title = models.CharField(max_length=160)
    note = models.TextField(max_length=500, blank=True)
    period = models.CharField(max_length=64, blank=True)
    due_date = models.DateField(null=True, blank=True)
    amount_vnd = models.PositiveBigIntegerField()
    document = models.ForeignKey(
        DocumentVersion, on_delete=models.PROTECT, related_name="bills"
    )
    reference = models.CharField(max_length=64, default=new_reference, editable=False)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ISSUED)
    payment_source = models.CharField(
        max_length=32, choices=PaymentSource.choices, blank=True
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="issued_bills"
    )
    issued_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    paid_confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="confirmed_bills",
    )
    void_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="voided_bills",
    )
    void_at = models.DateTimeField(null=True, blank=True)
    void_reason = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount_vnd__gt=0), name="bill_amount_positive"
            ),
        ]
