from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from lamto.accounts.models import Building, ManagementMembership
from lamto.documents.models import DocumentVersion
from lamto.maintenance.models import MaintenanceCase

from .execution import Settlement
from .proposals import InsertOnlyModel, Proposal


class MaintenanceFund(models.Model):
    building = models.OneToOneField(
        Building, on_delete=models.PROTECT, related_name="maintenance_fund"
    )
    created_at = models.DateTimeField(auto_now_add=True)


class MaintenanceFundEntry(InsertOnlyModel):
    class EntryType(models.TextChoices):
        OPENING_BALANCE = "OPENING_BALANCE", _("Opening balance")
        INFLOW = "INFLOW", _("Inflow")
        OUTFLOW = "OUTFLOW", _("Outflow")
        REVERSAL = "REVERSAL", _("Reversal")
        REPLACEMENT = "REPLACEMENT", _("Replacement")

    fund = models.ForeignKey(
        MaintenanceFund, on_delete=models.PROTECT, related_name="entries"
    )
    entry_type = models.CharField(max_length=32, choices=EntryType.choices)
    amount_vnd = models.BigIntegerField()
    evidence = models.ForeignKey(
        DocumentVersion,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    evidence_hash = models.CharField(max_length=64, blank=True)
    recorder = models.ForeignKey(
        ManagementMembership,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="recorded_fund_entries",
    )
    proposal = models.ForeignKey(
        Proposal,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="fund_entries",
    )
    source_key = models.CharField(max_length=128, unique=True)
    recorded_at = models.DateTimeField()

    @property
    def created_at(self):
        return self.recorded_at

    def save(self, *args, **kwargs):
        if self.recorded_at > timezone.now():
            raise ValidationError(
                {"recorded_at": _("Fund entries cannot be future-dated.")}
            )
        return super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        entry_type__in=["OPENING_BALANCE", "INFLOW"],
                        amount_vnd__gt=0,
                    )
                    | models.Q(entry_type="OUTFLOW", amount_vnd__lt=0)
                    | (
                        models.Q(entry_type__in=["REVERSAL", "REPLACEMENT"])
                        & ~models.Q(amount_vnd=0)
                    )
                ),
                name="fund_entry_amount_sign",
            ),
        ]


class FundEntryVerification(InsertOnlyModel):
    entry = models.OneToOneField(
        MaintenanceFundEntry, on_delete=models.PROTECT, related_name="verification"
    )
    membership = models.ForeignKey(
        ManagementMembership,
        on_delete=models.PROTECT,
        related_name="fund_verifications",
    )
    verified_at = models.DateTimeField()

    @property
    def created_at(self):
        return self.verified_at

    @property
    def verifier(self):
        return self.membership


class VerificationObservation(InsertOnlyModel):
    class Result(models.TextChoices):
        VERIFIED = "VERIFIED", _("Verified")
        MISMATCH = "MISMATCH", _("Mismatch")
        UNAVAILABLE = "UNAVAILABLE", _("Unavailable")

    published_entry = models.ForeignKey(
        "PublishedLedgerEntry",
        on_delete=models.PROTECT,
        related_name="verification_observations",
    )
    result = models.CharField(max_length=16, choices=Result.choices)
    checked_document_hashes = models.JSONField(default=list)
    checked_chain_event_ids = models.JSONField(default=list)
    details = models.JSONField(default=dict)
    observed_at = models.DateTimeField()

    @property
    def created_at(self):
        return self.observed_at


class PublishedLedgerEntry(InsertOnlyModel):
    resident_payload = models.JSONField(default=dict)
    case = models.ForeignKey(MaintenanceCase, null=True, blank=True, on_delete=models.PROTECT)
    proposal = models.OneToOneField(
        Proposal, on_delete=models.PROTECT, related_name="published_ledger_entry"
    )
    settlement = models.OneToOneField(Settlement, on_delete=models.PROTECT, related_name="ledger_entry")
    actual_cost_vnd = models.BigIntegerField()
    contractor_name = models.CharField(max_length=255)
    published_at = models.DateTimeField()

    @property
    def created_at(self):
        return self.published_at

    @property
    def effective_integrity_status(self):
        latest = (
            self.verification_observations.order_by("-observed_at", "-pk").first()
        )
        if latest is None:
            return "UNCHECKED"
        return latest.result

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(actual_cost_vnd__gt=0),
                name="published_ledger_actual_cost_positive",
            ),
        ]
