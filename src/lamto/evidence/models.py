from django.db import models
from django.utils.translation import gettext_lazy as _

class EvidenceType(models.IntegerChoices):
    PROPOSAL_CREATED = 1, "Proposal created"
    RESERVED_2 = 2, "Reserved"
    RESERVED_3 = 3, "Reserved"
    RESERVED_4 = 4, "Reserved"
    RESERVED_5 = 5, "Reserved"
    SETTLEMENT = 10, "Settlement"


class EvidenceLevel(models.TextChoices):
    """Explicit verification state — replaces any boolean notion of verified (spec 5.1)."""

    PENDING = "PENDING", _("Pending")
    LOCAL_SIGNED = "LOCAL_SIGNED", _("Locally signed")
    CHAIN_CONFIRMED = "CHAIN_CONFIRMED", _("Chain confirmed")
    MISMATCH = "MISMATCH", _("Mismatch")


class BlockchainOutboxEvent(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        SUBMITTED = "SUBMITTED", _("Submitted")
        CONFIRMED = "CONFIRMED", _("Confirmed")
        LOCAL = "LOCAL", _("Locally settled")
        FAILED = "FAILED", _("Failed")
        MISMATCH = "MISMATCH", _("Mismatch")

    event_id = models.CharField(max_length=66, unique=True)
    event_type = models.PositiveSmallIntegerField(choices=EvidenceType)
    payload = models.JSONField()
    payload_hash = models.CharField(max_length=64)
    previous_hash = models.CharField(max_length=66)
    signature = models.CharField(max_length=132)
    signer_address = models.CharField(max_length=42)
    building = models.ForeignKey(
        "accounts.Building",
        on_delete=models.PROTECT,
        related_name="outbox_events",
        editable=False,
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    attempts = models.PositiveIntegerField(default=0)
    next_attempt_at = models.DateTimeField(null=True, blank=True)
    lease_expires_at = models.DateTimeField(null=True, blank=True)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    transaction_hash = models.CharField(max_length=66, blank=True)
    receipt_status = models.IntegerField(null=True, blank=True)
    receipt = models.JSONField(default=dict, blank=True)
    last_error = models.TextField(blank=True)
    chain_confirmed_block = models.BigIntegerField(null=True, blank=True)
    chain_block_timestamp = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def evidence_level(self) -> str:
        return evidence_level(self.status)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(signer_address=""),
                name="outbox_signer_address_required",
            ),
            models.CheckConstraint(
                condition=models.Q(event_id__regex=r"^0x[0-9a-f]{64}$"),
                name="outbox_event_id_bytes32",
            ),
            models.CheckConstraint(
                condition=models.Q(payload_hash__regex=r"^[0-9a-f]{64}$"),
                name="outbox_payload_hash_sha256",
            ),
            models.CheckConstraint(
                condition=models.Q(previous_hash__regex=r"^0x[0-9a-f]{64}$"),
                name="outbox_previous_hash_bytes32",
            ),
            models.CheckConstraint(
                condition=models.Q(event_type__gte=1, event_type__lte=11),
                name="outbox_known_event_type",
            ),
        ]


SETTLED_STATUSES = (
    BlockchainOutboxEvent.Status.LOCAL,
    BlockchainOutboxEvent.Status.CONFIRMED,
)


def evidence_level(status) -> str:
    """Map an outbox delivery status to the explicit evidence level (spec 5.1)."""
    if status == BlockchainOutboxEvent.Status.LOCAL:
        return EvidenceLevel.LOCAL_SIGNED
    if status == BlockchainOutboxEvent.Status.CONFIRMED:
        return EvidenceLevel.CHAIN_CONFIRMED
    if status == BlockchainOutboxEvent.Status.MISMATCH:
        return EvidenceLevel.MISMATCH
    return EvidenceLevel.PENDING


def is_settled(status) -> bool:
    """Settled = evidence durably recorded: locally signed or chain-confirmed."""
    return status in SETTLED_STATUSES
