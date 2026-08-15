from django.db import models
from django.utils.translation import gettext_lazy as _

from lamto.accounts.models import ManagementMembership
from lamto.documents.models import DocumentVersion
from lamto.evidence.models import BlockchainOutboxEvent

from .proposals import Proposal


class Settlement(models.Model):
    class AckKind(models.TextChoices):
        MANAGEMENT_UPLOAD = "MANAGEMENT_UPLOAD", _("Management-uploaded evidence")
        PAYEE_LINK = "PAYEE_LINK", _("Payee link (reserved)")

    proposal = models.OneToOneField(Proposal, on_delete=models.PROTECT, related_name="settlement")
    amount_vnd = models.BigIntegerField()
    payee_name = models.CharField(max_length=255)
    bank_reference = models.CharField(max_length=64)
    transfer = models.ForeignKey(DocumentVersion, on_delete=models.PROTECT, related_name="+")
    transfer_recorded_by = models.ForeignKey(ManagementMembership, on_delete=models.PROTECT, related_name="+")
    transfer_recorded_at = models.DateTimeField()
    ack_kind = models.CharField(max_length=24, choices=AckKind.choices, default=AckKind.MANAGEMENT_UPLOAD)
    ack = models.ForeignKey(DocumentVersion, null=True, blank=True, on_delete=models.PROTECT, related_name="+")
    ack_recorded_by = models.ForeignKey(ManagementMembership, null=True, blank=True, on_delete=models.PROTECT, related_name="+")
    ack_recorded_at = models.DateTimeField(null=True, blank=True)
    settled_at = models.DateTimeField(null=True, blank=True)
    outbox_event = models.OneToOneField(BlockchainOutboxEvent, null=True, blank=True, on_delete=models.PROTECT, related_name="settlement")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(settled_at__isnull=True) | (models.Q(ack_recorded_at__isnull=False) & models.Q(outbox_event__isnull=False)), name="settlement_requires_both_evidence_sides"),
            models.CheckConstraint(condition=models.Q(amount_vnd__gt=0), name="settlement_amount_positive"),
        ]
