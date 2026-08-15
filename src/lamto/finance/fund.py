from django.core.exceptions import ValidationError
from django.db import connection, models, transaction
from django.db.models import Q, Sum
from django.utils import timezone

from lamto.accounts.models import Building
from lamto.accounts.services import require_management
from lamto.audit.services import record_audit
from lamto.documents.models import DocumentVersion
from django.utils.translation import gettext_lazy as _

from .models import (
    FundEntryVerification,
    MaintenanceFund,
    MaintenanceFundEntry,
    PublishedLedgerEntry,
)

SOURCE_ENTRY_TYPES = frozenset(
    {
        MaintenanceFundEntry.EntryType.OPENING_BALANCE,
        MaintenanceFundEntry.EntryType.INFLOW,
    }
)

FINALIZED_ENTRY_TYPES = frozenset(
    {
        MaintenanceFundEntry.EntryType.OUTFLOW,
        MaintenanceFundEntry.EntryType.REVERSAL,
        MaintenanceFundEntry.EntryType.REPLACEMENT,
    }
)


def _allocate_pk(model):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT nextval(pg_get_serial_sequence(%s, 'id'))",
            [model._meta.db_table],
        )
        return cursor.fetchone()[0]


def allocate_fund_entry_id() -> int:
    """Reserve a MaintenanceFundEntry primary key for sign-before-write."""
    return int(_allocate_pk(MaintenanceFundEntry))


def get_or_create_fund(building) -> MaintenanceFund:
    building_id = getattr(building, "pk", building)
    fund, _ = MaintenanceFund.objects.get_or_create(building_id=building_id)
    return fund


def _require_evidence(evidence, building_id, *, lock=False):
    evidence_id = getattr(evidence, "pk", None)
    if evidence_id is None:
        raise ValidationError(_("Fund source evidence document is required."))
    queryset = DocumentVersion.objects.select_related("document").filter(pk=evidence_id)
    if lock:
        queryset = queryset.select_for_update()
    version = queryset.first()
    if version is None:
        raise ValidationError(_("Fund source evidence versions must still exist."))
    if (
        version.document.building_id != building_id
        or version.scan_status != DocumentVersion.ScanStatus.CLEAN
    ):
        raise ValidationError(
            _("Fund evidence must be clean, safe, and in the fund building.")
        )
    return version


def _validate_source_amount(entry_type, amount_vnd):
    if entry_type not in SOURCE_ENTRY_TYPES:
        raise ValidationError(_("Only opening balance and inflow sources may be recorded."))
    if type(amount_vnd) is not int or amount_vnd <= 0:
        raise ValidationError(_("Fund source amount must be a positive integer VND amount."))


def _source_key(entry_type, fund_id, original_hash):
    return f"{entry_type}:{fund_id}:{original_hash}"


def _locked_fund(fund):
    locked = (
        MaintenanceFund.objects.select_for_update()
        .select_related("building")
        .filter(pk=getattr(fund, "pk", None))
        .first()
    )
    if locked is None:
        raise ValidationError(_("Maintenance fund does not exist."))
    return locked


def _locked_entry(entry):
    locked_id = (
        MaintenanceFundEntry.objects.select_for_update()
        .filter(pk=getattr(entry, "pk", None))
        .values_list("pk", flat=True)
        .first()
    )
    if locked_id is None:
        raise ValidationError(_("Fund entry does not exist."))
    return (
        MaintenanceFundEntry.objects.select_related(
            "fund__building",
            "recorder__user",
            "evidence",
        ).get(pk=locked_id)
    )


@transaction.atomic
def record_fund_source(
    fund,
    entry_type,
    amount_vnd,
    evidence,
    recorder,
    fund_entry_id=None,
    timestamp=None,
    source_key=None,
) -> MaintenanceFundEntry:
    fund = _locked_fund(fund)
    actor = require_management(recorder.user, fund.building_id)
    _validate_source_amount(entry_type, amount_vnd)
    evidence = _require_evidence(evidence, fund.building_id, lock=True)
    if fund_entry_id is None:
        fund_entry_id = allocate_fund_entry_id()
    if type(fund_entry_id) is not int or fund_entry_id <= 0:
        raise ValidationError(_("Fund entry id must be a positive integer."))
    if MaintenanceFundEntry.objects.filter(pk=fund_entry_id).exists():
        raise ValidationError(_("Fund entry id is already used."))
    entry_timestamp = timestamp or timezone.now()
    if not isinstance(entry_timestamp, type(timezone.now())) or entry_timestamp.tzinfo is None:
        raise ValidationError(_("Fund entry timestamp must be timezone-aware."))
    key = source_key or _source_key(entry_type, fund.pk, evidence.sha256)
    if MaintenanceFundEntry.objects.filter(source_key=key).exists():
        raise ValidationError(_("Fund source key already exists."))
    entry = MaintenanceFundEntry(
        pk=fund_entry_id,
        fund=fund,
        entry_type=entry_type,
        amount_vnd=amount_vnd,
        evidence=evidence,
        evidence_hash=evidence.sha256,
        recorder=actor,
        source_key=key,
        recorded_at=timezone.now(),
    )
    entry.save(force_insert=True)
    record_audit(
        actor.user,
        actor,
        "fund.record",
        "MaintenanceFundEntry",
        str(entry.pk),
        "accepted",
        {
            "entry_type": entry_type,
            "amount_vnd": amount_vnd,
        },
    )
    return entry


@transaction.atomic
def verify_fund_source(
    entry,
    verifier,
    timestamp=None,
) -> FundEntryVerification:
    entry = _locked_entry(entry)
    actor = require_management(verifier.user, entry.fund.building_id)
    if entry.entry_type not in SOURCE_ENTRY_TYPES:
        raise ValidationError(_("Only opening balance and inflow sources may be verified."))
    if entry.recorder is None:
        raise ValidationError(_("Fund source has no recorder."))
    if FundEntryVerification.objects.filter(entry=entry).exists():
        raise ValidationError(_("Fund source has already been verified."))
    verification = FundEntryVerification.objects.create(
        entry=entry,
        membership=actor,
        verified_at=timezone.now(),
    )
    record_audit(
        actor.user,
        actor,
        "fund.verify",
        "FundEntryVerification",
        str(verification.pk),
        "accepted",
        {
            "entry_id": entry.pk,
        },
    )
    return verification


def _source_verified_q():
    return Q(
        entry_type__in=SOURCE_ENTRY_TYPES,
        verification__isnull=False,
    )


def _finalized_posting_q():
    return Q(
        entry_type__in=FINALIZED_ENTRY_TYPES,
        proposal__published_ledger_entry__isnull=False,
    )


def fund_balance(building_id, verified_only=True) -> int:
    if type(building_id) is not int or building_id <= 0:
        building_id = getattr(building_id, "pk", None)
    if building_id is None:
        raise ValidationError(_("Building is required."))
    if not Building.objects.filter(pk=building_id).exists():
        raise ValidationError(_("Building does not exist."))
    fund = MaintenanceFund.objects.filter(building_id=building_id).first()
    if fund is None:
        return 0
    entries = MaintenanceFundEntry.objects.filter(fund=fund)
    if verified_only:
        entries = entries.filter(_source_verified_q() | _finalized_posting_q())
    else:
        entries = entries.filter(
            Q(entry_type__in=SOURCE_ENTRY_TYPES) | _finalized_posting_q()
        )
    total = entries.aggregate(total=Sum("amount_vnd"))["total"]
    return int(total or 0)


def create_settlement_outflow(settlement) -> MaintenanceFundEntry:
    entry, _ = MaintenanceFundEntry.objects.get_or_create(
        source_key=f"OUTFLOW:proposal:{settlement.proposal_id}",
        defaults={
            "fund": get_or_create_fund(settlement.proposal.building),
            "entry_type": MaintenanceFundEntry.EntryType.OUTFLOW,
            "amount_vnd": -settlement.amount_vnd,
            "proposal": settlement.proposal,
            "recorded_at": settlement.settled_at,
        },
    )
    return entry
