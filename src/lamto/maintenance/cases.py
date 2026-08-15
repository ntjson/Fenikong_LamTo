"""Request-outcome services on the report/case pair."""

from datetime import timedelta

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from lamto.accounts.models import ResidentOccupancy
from lamto.accounts.services import require_management
from lamto.audit.services import record_audit
from lamto.documents.models import Document, DocumentVersion
from django.utils.translation import gettext_lazy as _

from .models import (
    CaseReport, InfoRequest, IssueReport, MaintenanceCase, WorkUpdate, WorkUpdateEvidence,
)

TERMINAL_STATUSES = frozenset(
    {IssueReport.Status.DECLINED, IssueReport.Status.COMPLETED, IssueReport.Status.CLOSED}
)
RATING_WINDOW_DAYS = 14


def _locked_case(case):
    case = MaintenanceCase.objects.select_for_update().filter(pk=getattr(case, "pk", None)).first()
    if case is None or not case.active or case.completed_at is not None:
        raise ValidationError(_("An active, uncompleted case is required."))
    return case


def _evidence_versions(versions, kind, building_id, uploader):
    versions = list(versions)
    if not versions:
        return []
    ids = [getattr(version, "pk", None) for version in versions]
    if None in ids or len(ids) != len(set(ids)):
        raise ValidationError(_("Progress requires distinct evidence versions."))
    valid = list(DocumentVersion.objects.select_for_update().select_related("document").filter(
        pk__in=ids, document__building_id=building_id, document__kind=kind,
        scan_status=DocumentVersion.ScanStatus.CLEAN,
        uploader=uploader,
    ))
    if len(valid) != len(ids) or any(not v.content_type.lower().startswith("image/") for v in valid):
        raise ValidationError(_("Progress evidence must be clean original images from the case building."))
    return valid


def _append_update(case, manager, cause, result, before_versions, after_versions, proposal=None):
    if not (cause or "").strip() or not (result or "").strip():
        raise ValidationError(_("Progress updates need both a cause and a result."))
    building_id = case.building_id if case else proposal.building_id
    before = _evidence_versions(before_versions, Document.Kind.BEFORE_PHOTO, building_id, manager)
    after = _evidence_versions(after_versions, Document.Kind.AFTER_PHOTO, building_id, manager)
    update = WorkUpdate.objects.create(case=case, proposal=proposal, author=manager, cause=cause.strip(), result=result.strip())
    WorkUpdateEvidence.objects.bulk_create([
        *[WorkUpdateEvidence(update=update, version=v, kind=WorkUpdateEvidence.Kind.BEFORE) for v in before],
        *[WorkUpdateEvidence(update=update, version=v, kind=WorkUpdateEvidence.Kind.AFTER) for v in after],
    ])
    return update


@transaction.atomic
def start_case_work(case, manager) -> MaintenanceCase:
    case = _locked_case(case)
    membership = require_management(manager, case.building_id)
    for report in IssueReport.objects.filter(case_reports__case=case).exclude(status__in=TERMINAL_STATUSES):
        report.status = IssueReport.Status.IN_PROGRESS
        report.save(update_fields=["status"])
    record_audit(actor=manager, membership=membership, action="case.work_started",
                 target_type="MaintenanceCase", target_id=str(case.pk), result="accepted")
    return case


@transaction.atomic
def publish_progress(case=None, manager=None, cause="", result="", before_versions=(), after_versions=(), proposal=None) -> WorkUpdate:
    if (case is None) == (proposal is None):
        raise ValidationError(_("Progress requires exactly one case or proposal."))
    if case is not None:
        case = _locked_case(case)
        building_id = case.building_id
    else:
        from lamto.finance.models import Proposal
        proposal = Proposal.objects.select_for_update().filter(pk=getattr(proposal, "pk", None), case__isnull=True).first()
        if proposal is None or proposal.status != Proposal.Status.IN_PROGRESS:
            raise ValidationError(_("An in-progress standalone proposal is required."))
        building_id = proposal.building_id
    membership = require_management(manager, building_id)
    update = _append_update(case, manager, cause, result, before_versions, after_versions, proposal)
    record_audit(actor=manager, membership=membership, action="case.progress_published",
                 target_type="WorkUpdate", target_id=str(update.pk), result="accepted",
                 metadata={"case_id": case.pk if case else None, "proposal_id": proposal.pk if proposal else None})
    try:
        from lamto.notifications.hooks import notify_progress_update
        notify_progress_update(update)
    except Exception:
        pass
    return update


@transaction.atomic
def complete_proposal_work(proposal, manager, cause, result, before_versions=(), after_versions=()):
    from lamto.finance.models import Proposal
    proposal = Proposal.objects.select_for_update().filter(pk=getattr(proposal, "pk", None), case__isnull=True).first()
    if proposal is None or proposal.status != Proposal.Status.IN_PROGRESS:
        raise ValidationError(_("An in-progress standalone proposal is required."))
    membership = require_management(manager, proposal.building_id)
    update = _append_update(None, manager, cause, result, before_versions, after_versions, proposal)
    proposal.status = Proposal.Status.COMPLETED
    proposal.completed_at = timezone.now()
    proposal.save(update_fields=["status", "completed_at"])
    record_audit(manager, membership, "proposal.work_completed", "Proposal", str(proposal.pk),
                 "accepted", {"work_update_id": update.pk})
    return proposal


@transaction.atomic
def complete_case_work(case, manager, cause, result, before_versions=(), after_versions=()) -> MaintenanceCase:
    case = _locked_case(case)
    membership = require_management(manager, case.building_id)
    update = _append_update(case, manager, cause, result, before_versions, after_versions)
    case.completed_at = timezone.now()
    case.save(update_fields=["completed_at"])
    try:
        proposal = case.proposal
    except Exception:
        proposal = None
    if proposal is not None:
        from lamto.finance.models import Proposal
        proposal.status = Proposal.Status.COMPLETED
        proposal.completed_at = case.completed_at
        proposal.save(update_fields=["status", "completed_at"])
    for report in IssueReport.objects.filter(case_reports__case=case).exclude(status__in=TERMINAL_STATUSES):
        report.status = IssueReport.Status.COMPLETED
        report.save(update_fields=["status"])
    record_audit(actor=manager, membership=membership, action="case.work_completed",
                 target_type="MaintenanceCase", target_id=str(case.pk), result="accepted",
                 metadata={"work_update_id": update.pk})
    try:
        from lamto.notifications.hooks import notify_case_completed
        notify_case_completed(case)
    except Exception:
        pass
    return case


@transaction.atomic
def close_expired_completed_cases(now=None) -> int:
    now = now or timezone.now()
    cases = list(MaintenanceCase.objects.select_for_update().filter(
        completed_at__lte=now - timedelta(days=RATING_WINDOW_DAYS), closed_at__isnull=True
    ))
    for case in cases:
        IssueReport.objects.filter(case_reports__case=case, status=IssueReport.Status.COMPLETED).update(
            status=IssueReport.Status.CLOSED
        )
        case.active = False
        case.closed_at = now
        case.save(update_fields=["active", "closed_at"])
    from lamto.finance.models import Proposal
    proposals = list(Proposal.objects.select_for_update().filter(
        case__isnull=True, status=Proposal.Status.COMPLETED,
        completed_at__lte=now - timedelta(days=RATING_WINDOW_DAYS), closed_at__isnull=True,
    ))
    closed_proposals = 0
    for proposal in proposals:
        close_at = proposal.completed_at + timedelta(days=RATING_WINDOW_DAYS)
        settlement = getattr(proposal, "settlement", None)
        if settlement and settlement.settled_at and settlement.settled_at > close_at:
            close_at = settlement.settled_at
        if now < close_at:
            continue
        proposal.status = Proposal.Status.CLOSED
        proposal.closed_at = now
        proposal.save(update_fields=["status", "closed_at"])
        closed_proposals += 1
    return len(cases) + closed_proposals


def _locked_report(report):
    report = IssueReport.objects.select_for_update().select_related("unit").filter(
        pk=getattr(report, "pk", None)
    ).first()
    if report is None:
        raise ValidationError(_("Report is required."))
    return report


@transaction.atomic
def request_information(report, manager, message) -> InfoRequest:
    report = _locked_report(report)
    membership = require_management(manager, report.unit.building_id)
    if report.status in TERMINAL_STATUSES:
        raise ValidationError(_("Closed or declined requests cannot ask for information."))
    if not (message or "").strip():
        raise ValidationError(_("An information request needs a message."))
    if InfoRequest.objects.filter(report=report, resolved_at__isnull=True).exists():
        raise ValidationError(_("An information request is already open for this report."))
    info = InfoRequest.objects.create(report=report, message=message.strip(), created_by=manager)
    report.status = IssueReport.Status.NEEDS_INFO
    report.save(update_fields=["status"])
    record_audit(actor=manager, membership=membership, action="request.info_requested",
                 target_type="InfoRequest", target_id=str(info.pk), result="accepted",
                 metadata={"report_id": report.pk})
    try:
        from lamto.notifications.hooks import notify_info_requested
        notify_info_requested(info)
    except Exception:
        pass
    return info


@transaction.atomic
def reply_information(resident, report, text) -> InfoRequest:
    report = _locked_report(report)
    if report.reporter_id != getattr(resident, "pk", None):
        raise PermissionDenied("Only the reporter may reply to an information request.")
    info = InfoRequest.objects.select_for_update().filter(
        report=report, resolved_at__isnull=True
    ).first()
    if info is None:
        raise ValidationError(_("No open information request for this report."))
    if not (text or "").strip():
        raise ValidationError(_("A reply needs text (photos may be attached separately)."))
    occupancy = ResidentOccupancy.objects.filter(
        user=resident, active=True, unit__building_id=report.unit.building_id
    ).first()
    if occupancy is None:
        raise PermissionDenied("Active occupancy in the building is required.")
    info.reply_text = text.strip()
    info.resolved_at = timezone.now()
    info.save(update_fields=["reply_text", "resolved_at"])
    report.status = IssueReport.Status.IN_REVIEW
    report.save(update_fields=["status"])
    record_audit(actor=resident, membership=None, action="request.info_replied",
                 target_type="InfoRequest", target_id=str(info.pk), result="accepted",
                 metadata={"report_id": report.pk, "occupancy_id": occupancy.pk})
    return info


@transaction.atomic
def decline_report(report, manager, reason) -> IssueReport:
    report = _locked_report(report)
    membership = require_management(manager, report.unit.building_id)
    if report.status in TERMINAL_STATUSES:
        raise ValidationError(_("This request is already closed."))
    if not (reason or "").strip():
        raise ValidationError(_("Declining a request requires a reason the resident can read."))
    now = timezone.now()
    report.status = IssueReport.Status.DECLINED
    report.declined_reason = reason.strip()
    report.declined_by = manager
    report.declined_at = now
    report.save(update_fields=["status", "declined_reason", "declined_by", "declined_at"])
    for link in CaseReport.objects.filter(report=report).select_related("case"):
        case = link.case
        if (case.active and not CaseReport.objects.filter(case=case).exclude(report=report)
                .exclude(report__status__in=TERMINAL_STATUSES).exists()):
            case.active = False
            case.closed_at = now
            case.save(update_fields=["active", "closed_at"])
    record_audit(actor=manager, membership=membership, action="request.declined",
                 target_type="IssueReport", target_id=str(report.pk), result="accepted",
                 metadata={"reason_length": len(report.declined_reason)})
    try:
        from lamto.notifications.hooks import notify_report_declined
        notify_report_declined(report)
    except Exception:
        pass
    return report
