from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from lamto.accounts.models import ManagementMembership
from lamto.documents.models import DocumentVersion
from lamto.evidence.models import BlockchainOutboxEvent
from lamto.maintenance.models import MaintenanceCase


class InsertOnlyModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Proposal versions are append-only.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Proposal versions are append-only.")


class Proposal(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", _("Draft")
        PUBLISHED = "PUBLISHED", _("Published")
        NOT_PROCEEDING = "NOT_PROCEEDING", _("Not proceeding")
        IN_PROGRESS = "IN_PROGRESS", _("In progress")
        COMPLETED = "COMPLETED", _("Completed")
        CLOSED = "CLOSED", _("Closed")

    case = models.OneToOneField(MaintenanceCase, null=True, blank=True, on_delete=models.PROTECT, related_name="proposal")
    building = models.ForeignKey("accounts.Building", on_delete=models.PROTECT, related_name="proposals")
    creator_membership = models.ForeignKey(ManagementMembership, on_delete=models.PROTECT)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.DRAFT)
    current_version = models.ForeignKey(
        "ProposalVersion", null=True, blank=True, on_delete=models.PROTECT, related_name="+"
    )
    decided_by = models.ForeignKey(ManagementMembership, null=True, blank=True, on_delete=models.PROTECT, related_name="decided_proposals")
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_note = models.TextField(blank=True)
    public_token = models.CharField(
        max_length=64, unique=True, null=True, blank=True, editable=False
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.building_id is None and self.case_id:
            self.building_id = self.case.building_id
        return super().save(*args, **kwargs)

class ProposalVersion(InsertOnlyModel):
    proposal = models.ForeignKey(Proposal, on_delete=models.PROTECT, related_name="versions")
    number = models.PositiveIntegerField()
    amount_vnd = models.BigIntegerField()
    contractor_name = models.CharField(max_length=255)
    fund_code = models.CharField(max_length=32, default="GENERAL")
    purpose = models.TextField()
    proposed_action = models.TextField()
    expected_schedule = models.CharField(max_length=200)
    snapshot = models.JSONField()
    snapshot_hash = models.CharField(max_length=64)
    creator_membership = models.ForeignKey(ManagementMembership, on_delete=models.PROTECT)
    creator_signature = models.CharField(max_length=132, blank=True)
    outbox_event = models.OneToOneField(
        BlockchainOutboxEvent, on_delete=models.PROTECT, related_name="proposal_version"
    )
    quotations = models.ManyToManyField(
        DocumentVersion, through="ProposalDocument", related_name="proposal_versions"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def verification_label(self):
        # Evidence vocabulary is fixed: pending / locally signed / chain confirmed / mismatch.
        labels = {
            "CONFIRMED": _("Chain confirmed"),
            "LOCAL": _("Locally signed (anchoring disabled)"),
            "MISMATCH": _("Mismatch detected"),
        }
        return labels.get(self.outbox_event.status, _("Pending anchoring"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["proposal", "number"], name="proposal_version_once"),
            models.CheckConstraint(condition=models.Q(amount_vnd__gt=0), name="proposal_amount_positive"),
        ]


class ProposalDocument(models.Model):
    proposal_version = models.ForeignKey(ProposalVersion, on_delete=models.PROTECT)
    document_version = models.ForeignKey(DocumentVersion, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Proposal quotation links are append-only.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Proposal quotation links are append-only.")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["proposal_version", "document_version"], name="proposal_document_once"
            )
        ]
