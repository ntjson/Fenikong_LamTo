from django.db import models
from django.utils.translation import gettext_lazy as _

from lamto.accounts.models import ManagementMembership
from lamto.documents.models import DocumentVersion
from lamto.evidence.models import BlockchainOutboxEvent

from .proposals import Proposal


class Settlement(models.Model):
    """Evidence that a published proposal was paid (ADR 0002).

    Single-sided: filing the transfer proof settles the proposal, so there is no
    state in which a Settlement row exists but is not yet settled. The recipient
    is not stored here — it is the contractor frozen on the proposal version.
    """

    proposal = models.OneToOneField(Proposal, on_delete=models.PROTECT, related_name="settlement")
    amount_vnd = models.BigIntegerField()
    transfer = models.ForeignKey(DocumentVersion, on_delete=models.PROTECT, related_name="+")
    settled_by = models.ForeignKey(ManagementMembership, on_delete=models.PROTECT, related_name="+")
    settled_at = models.DateTimeField()
    # Nullable only because the anchored payload carries settlement_id, so the
    # row must exist before its event does. record_settlement() sets this inside
    # the same transaction; a settled row with no event never becomes visible.
    outbox_event = models.OneToOneField(BlockchainOutboxEvent, null=True, blank=True, on_delete=models.PROTECT, related_name="settlement")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(amount_vnd__gt=0), name="settlement_amount_positive"),
        ]
