import datetime
import secrets

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Max
from django.utils import timezone

from lamto.accounts.services import require_management
from lamto.audit.services import record_audit
from lamto.documents.models import DocumentVersion
from lamto.evidence.canonical import payload_hash
from lamto.evidence.models import EvidenceType
from lamto.evidence.services import queue_platform_event
from lamto.maintenance.cases import TERMINAL_STATUSES
from lamto.maintenance.models import CaseReport, IssueReport, MaintenanceCase
from django.utils.translation import gettext_lazy as _

from .models import PricePrediction, Proposal, ProposalDocument, ProposalVersion


def new_public_token() -> str:
    """Opaque, unguessable identity of a proposal's Evidence explorer URL."""
    return secrets.token_urlsafe(32)


def spending_proposal_cases():
    """Cases still on outcome D: public, active, and not already started as outcome C."""
    return (
        MaintenanceCase.objects.filter(active=True, completed_at__isnull=True)
        .exclude(reports__is_private=True)
        .exclude(reports__status=IssueReport.Status.IN_PROGRESS)
        .distinct()
    )


ZERO_HASH = "0x" + "00" * 32


def _resolve_schedule_and_dates(expected_start=None, expected_end=None, expected_schedule=None):
    if isinstance(expected_start, str) and expected_start.strip():
        expected_start = datetime.date.fromisoformat(expected_start.strip())
    elif not expected_start:
        expected_start = None

    if isinstance(expected_end, str) and expected_end.strip():
        expected_end = datetime.date.fromisoformat(expected_end.strip())
    elif not expected_end:
        expected_end = None

    if bool(expected_start) != bool(expected_end):
        raise ValidationError(_("Expected start and end dates must be provided together."))

    if expected_start and expected_end:
        if expected_end < expected_start:
            raise ValidationError(_("Expected end date cannot precede expected start date."))
        resolved_schedule = f"{expected_start.strftime('%d/%m/%Y')} \u2013 {expected_end.strftime('%d/%m/%Y')}"
    elif expected_schedule and str(expected_schedule).strip():
        resolved_schedule = str(expected_schedule).strip()
    else:
        resolved_schedule = "To be scheduled"

    return expected_start, expected_end, resolved_schedule


def _quotation_versions(building_id, quotation_versions, *, lock=False):
    supplied = list(quotation_versions or [])
    ids = [getattr(version, "pk", None) for version in supplied]
    if not ids or any(value is None for value in ids) or len(set(ids)) != len(ids):
        raise ValidationError(_("At least one distinct quotation is required."))
    queryset = DocumentVersion.objects.select_related("document").filter(pk__in=ids)
    if lock:
        queryset = queryset.select_for_update()
    versions = {version.pk: version for version in queryset}
    if len(versions) != len(ids):
        raise ValidationError(_("Every quotation version must still exist."))

    resolved = []
    for version_id in ids:
        version = versions[version_id]
        if (
            version.document.kind != version.document.Kind.QUOTATION
            or version.document.building_id != building_id
            or version.scan_status != DocumentVersion.ScanStatus.CLEAN
        ):
            raise ValidationError(
                _("Quotations must be clean, safe, and in the work-order building.")
            )
        resolved.append(version)
    return resolved


def _submission_snapshot(
    proposal,
    amount_vnd,
    contractor_name,
    purpose,
    proposed_action,
    expected_schedule,
    versions,
    number,
    expected_start=None,
    expected_end=None,
):
    case = proposal.case
    quotation_snapshot = [
        {
            "version_id": version.pk,
            "sha256": version.sha256,
        }
        for version in versions
    ]
    snapshot = {
        "proposal_id": proposal.pk,
        "proposal_version": number,
        "case_id": case.pk if case else None,
        "building_id": proposal.building_id,
        "amount_vnd": amount_vnd,
        "contractor_name": contractor_name,
        "purpose": purpose,
        "proposed_action": proposed_action,
        "expected_start": expected_start.isoformat() if hasattr(expected_start, "isoformat") else (expected_start or None),
        "expected_end": expected_end.isoformat() if hasattr(expected_end, "isoformat") else (expected_end or None),
        "expected_schedule": expected_schedule,
        "quotation_versions": quotation_snapshot,
    }
    evidence_payload = {
        "proposal_id": proposal.pk,
        "proposal_version": number,
        "record_id": proposal.pk,
        "building_id": proposal.building_id,
        "amount_vnd": amount_vnd,
        "proposal_snapshot_hash": payload_hash(snapshot),
        "quotation_hash": payload_hash([version.sha256 for version in versions]),
    }
    if case:
        evidence_payload.update(
            case_id=case.pk,
            case_snapshot_hash=payload_hash(
                {
                    "case_id": case.pk,
                    "category": case.category,
                    "management_queue": case.management_queue,
                    "location_id": case.location_id,
                }
            ),
        )
    return snapshot, evidence_payload


def build_proposal_evidence_payload(
    proposal,
    amount_vnd,
    contractor_name,
    quotation_versions,
    purpose=None,
    proposed_action="",
    expected_start=None,
    expected_end=None,
    expected_schedule="",
):
    """Build the exact signed payload callers must use before submission."""
    if type(amount_vnd) is not int or amount_vnd <= 0:
        raise ValidationError(_("Proposal amount must be a positive integer."))
    if not isinstance(contractor_name, str) or not contractor_name.strip():
        raise ValidationError(_("Contractor name is required."))
    purpose = (
        proposal.case.get_category_display()
        if purpose is None and proposal.case_id
        else (purpose or "")
    )
    expected_start, expected_end, resolved_schedule = _resolve_schedule_and_dates(
        expected_start, expected_end, expected_schedule
    )
    versions = _quotation_versions(
        proposal.building_id or proposal.case.building_id, quotation_versions
    )
    number = (
        ProposalVersion.objects.filter(proposal=proposal).aggregate(Max("number"))[
            "number__max"
        ]
        or 0
    ) + 1
    _, evidence_payload = _submission_snapshot(
        proposal,
        amount_vnd,
        contractor_name.strip(),
        purpose,
        proposed_action,
        resolved_schedule,
        versions,
        number,
        expected_start=expected_start,
        expected_end=expected_end,
    )
    return evidence_payload


@transaction.atomic
def create_proposal(case, creator_membership) -> Proposal:
    locked_case = (
        MaintenanceCase.objects.select_for_update()
        .filter(pk=getattr(case, "pk", None))
        .first()
    )
    if (
        locked_case is None
        or not locked_case.active
        or locked_case.completed_at is not None
    ):
        raise ValidationError(_("An active uncompleted case is required."))
    membership = require_management(creator_membership.user, locked_case.building_id)
    links = CaseReport.objects.filter(case=locked_case).select_related("report")
    if any(link.report.is_private for link in links):
        raise ValidationError(_("Private requests cannot become community proposals."))
    if any(link.report.status == IssueReport.Status.IN_PROGRESS for link in links):
        raise ValidationError(
            _("Cases already proceeding without spending cannot add a proposal.")
        )
    try:
        proposal = Proposal.objects.create(
            case=locked_case,
            building=locked_case.building,
            creator_membership=membership,
        )
    except IntegrityError as exc:
        raise ValidationError(_("A proposal already exists for this case.")) from exc
    IssueReport.objects.filter(case_reports__case=locked_case).exclude(
        status__in=TERMINAL_STATUSES
    ).update(status=IssueReport.Status.PROPOSED)
    record_audit(
        membership.user,
        membership,
        "proposal.create",
        "Proposal",
        str(proposal.pk),
        "accepted",
        {"case_id": locked_case.pk},
    )
    return proposal


@transaction.atomic
def create_standalone_proposal(building, creator_membership) -> Proposal:
    membership = require_management(
        creator_membership.user, getattr(building, "pk", None)
    )
    proposal = Proposal.objects.create(building=building, creator_membership=membership)
    record_audit(
        membership.user,
        membership,
        "proposal.create",
        "Proposal",
        str(proposal.pk),
        "accepted",
        {"case_id": None},
    )
    return proposal


@transaction.atomic
def decide_proposal(proposal, manager, proceed: bool, note="") -> Proposal:
    locked = Proposal.objects.select_for_update().get(pk=getattr(proposal, "pk", None))
    membership = require_management(manager, locked.building_id)
    if locked.status != Proposal.Status.PUBLISHED:
        raise ValidationError(_("Only published proposals can be decided."))
    if type(proceed) is not bool:
        raise ValidationError(_("Proceed must be a boolean."))
    now = timezone.now()
    locked.status = (
        Proposal.Status.IN_PROGRESS if proceed else Proposal.Status.NOT_PROCEEDING
    )
    locked.decided_by = membership
    locked.decided_at = now
    locked.decision_note = (note or "").strip()
    locked.closed_at = None if proceed else now
    locked.save(
        update_fields=[
            "status",
            "decided_by",
            "decided_at",
            "decision_note",
            "closed_at",
        ]
    )
    record_audit(
        manager,
        membership,
        "proposal.decided",
        "Proposal",
        str(locked.pk),
        "accepted",
        {"proceed": proceed},
    )
    return locked


@transaction.atomic
def publish_proposal_version(
    proposal,
    creator_membership,
    *,
    amount_vnd,
    contractor_name,
    purpose,
    proposed_action,
    expected_start=None,
    expected_end=None,
    expected_schedule="",
    quotation_versions,
    event_id,
    price_prediction_id=None,
) -> ProposalVersion:
    locked_proposal = (
        Proposal.objects.select_for_update()
        .select_related("creator_membership__user", "building")
        .get(pk=getattr(proposal, "pk", None))
    )
    membership = require_management(
        creator_membership.user, locked_proposal.building_id
    )
    if type(amount_vnd) is not int or amount_vnd <= 0:
        raise ValidationError(_("Proposal amount must be a positive integer."))
    if not isinstance(contractor_name, str) or not contractor_name.strip():
        raise ValidationError(_("Contractor name is required."))
    if locked_proposal.status not in {
        Proposal.Status.DRAFT,
        Proposal.Status.PUBLISHED,
        Proposal.Status.IN_PROGRESS,
    }:
        raise ValidationError(_("This proposal cannot receive another version."))
    for value, message in (
        (purpose, _("Problem or need is required.")),
        (proposed_action, _("Proposed action is required.")),
    ):
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(message)

    expected_start, expected_end, resolved_schedule = _resolve_schedule_and_dates(
        expected_start, expected_end, expected_schedule
    )

    versions = _quotation_versions(
        locked_proposal.building_id, quotation_versions, lock=True
    )
    previous = locked_proposal.versions.order_by("-number").first()
    number = (previous.number if previous else 0) + 1
    if previous is None:
        locked_proposal.public_token = new_public_token()
    snapshot, evidence_payload = _submission_snapshot(
        locked_proposal,
        amount_vnd,
        contractor_name.strip(),
        purpose.strip(),
        proposed_action.strip(),
        resolved_schedule,
        versions,
        number,
        expected_start=expected_start,
        expected_end=expected_end,
    )
    previous_hash = "0x" + previous.outbox_event.payload_hash if previous else ZERO_HASH
    event = queue_platform_event(
        event_id,
        EvidenceType.PROPOSAL_CREATED,
        evidence_payload,
        previous_hash,
        locked_proposal.building,
    )
    version = ProposalVersion.objects.create(
        proposal=locked_proposal,
        number=number,
        amount_vnd=amount_vnd,
        contractor_name=contractor_name.strip(),
        purpose=purpose.strip(),
        proposed_action=proposed_action.strip(),
        expected_start=expected_start,
        expected_end=expected_end,
        expected_schedule=resolved_schedule,
        snapshot=snapshot,
        snapshot_hash=payload_hash(snapshot),
        creator_membership=membership,
        creator_signature="",
        outbox_event=event,
    )
    ProposalDocument.objects.bulk_create(
        [
            ProposalDocument(proposal_version=version, document_version=document)
            for document in versions
        ]
    )
    if price_prediction_id:
        try:
            prediction = (
                PricePrediction.objects.select_for_update()
                .filter(pk=price_prediction_id)
                .first()
            )
            if (
                prediction is not None
                and prediction.building_id == locked_proposal.building_id
                and prediction.case_id == locked_proposal.case_id
                and prediction.amount_vnd == amount_vnd
                and prediction.proposal_version_id is None
            ):
                prediction.proposal_version = version
                prediction.save(update_fields=["proposal_version"])
        except Exception:
            pass
    locked_proposal.current_version = version
    locked_proposal.status = Proposal.Status.PUBLISHED
    locked_proposal.save(update_fields=["current_version", "status", "public_token"])
    record_audit(
        membership.user,
        membership,
        "proposal.version.publish",
        "ProposalVersion",
        str(version.pk),
        "accepted",
        {
            "proposal_id": locked_proposal.pk,
            "number": number,
            "event_id": event.event_id,
        },
    )
    return version
