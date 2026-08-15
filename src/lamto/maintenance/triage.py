from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from lamto.accounts.services import require_management
from lamto.audit.services import record_audit
from django.utils.translation import gettext_lazy as _

from .ai import URGENCIES
from .models import (
    BuildingLocation,
    CaseReport,
    IssueReport,
    MaintenanceCase,
    TriageDecision,
    TriageSuggestion,
    normalize_category,
    normalize_management_queue,
)


def _active_location(location, building_id):
    target = BuildingLocation.objects.select_for_update().filter(pk=getattr(location, "pk", None)).first()
    if target is None:
        raise ValidationError(_("Case location must be active and belong to the report building."))
    curr = target
    seen = set()
    while curr is not None:
        if curr.pk in seen or not curr.active or curr.building_id != building_id:
            raise ValidationError(_("Case location must be active and belong to the report building."))
        seen.add(curr.pk)
        if curr.parent_id is None:
            return target
        curr = BuildingLocation.objects.select_for_update().filter(pk=curr.parent_id).first()
    raise ValidationError(_("Case location hierarchy is invalid."))


def _decision_values(category, urgency, management_queue, deadline_minutes):
    if not isinstance(category, str) or not (category := category.strip()):
        raise ValidationError(_("Case category is required."))
    category = normalize_category(category)
    if urgency not in URGENCIES:
        raise ValidationError(_("Case urgency is invalid."))
    if not isinstance(management_queue, str) or not (management_queue := management_queue.strip()):
        raise ValidationError(_("Management queue is required."))
    management_queue = normalize_management_queue(management_queue)
    if type(deadline_minutes) is not int or deadline_minutes <= 0:
        raise ValidationError(_("Case deadline must be a positive number of minutes."))
    return category, urgency, management_queue, deadline_minutes


@transaction.atomic
def confirm_triage(report, operator, category, urgency, location, management_queue, deadline_minutes):
    report = (
        IssueReport.objects.select_for_update()
        .select_related("unit")
        .filter(pk=getattr(report, "pk", None))
        .first()
    )
    if report is None:
        raise ValidationError(_("Report is required."))
    membership = require_management(operator, report.unit.building_id)
    location = _active_location(location, report.unit.building_id)
    category, urgency, management_queue, deadline_minutes = _decision_values(
        category, urgency, management_queue, deadline_minutes
    )
    suggestion = TriageSuggestion.objects.select_for_update().filter(job__report=report).first()
    decision = TriageDecision.objects.select_for_update().filter(report=report).first()
    if decision is not None:
        return decision.case
    selected = {
        "category": category,
        "urgency": urgency,
        "management_queue": management_queue,
        "deadline_minutes": deadline_minutes,
    }
    suggested = {} if suggestion is None else {
        "category": suggestion.category,
        "urgency": suggestion.urgency,
        "management_queue": suggestion.management_queue,
        "deadline_minutes": suggestion.deadline_minutes,
    }
    differences = {
        key: {"suggested": suggested[key], "chosen": value}
        for key, value in selected.items()
        if key in suggested and suggested[key] != value
    }
    decision = TriageDecision.objects.create(
        report=report,
        suggestion=suggestion,
        operator=operator,
        location=location,
        differences=differences,
        **selected,
    )
    case = MaintenanceCase.objects.create(
        decision=decision,
        building_id=report.unit.building_id,
        location=location,
        deadline_at=timezone.now() + timedelta(minutes=deadline_minutes),
        category=category,
        urgency=urgency,
        management_queue=management_queue,
    )
    CaseReport.objects.create(case=case, report=report, grouped_by=operator)
    record_audit(
        actor=operator,
        membership=membership,
        action="triage.confirm",
        target_type="MaintenanceCase",
        target_id=str(case.pk),
        result="accepted",
        metadata={"report_id": report.pk, "differences": differences},
    )
    try:
        from lamto.notifications.hooks import notify_triage_confirmed

        notify_triage_confirmed(case, report)
    except Exception:
        pass
    return case


@transaction.atomic
def group_report(case, report, operator):
    case = MaintenanceCase.objects.select_for_update().filter(pk=getattr(case, "pk", None)).first()
    report = (
        IssueReport.objects.select_for_update()
        .select_related("unit")
        .filter(pk=getattr(report, "pk", None))
        .first()
    )
    if case is None or report is None or not case.active:
        raise ValidationError(_("An active case and report are required."))
    membership = require_management(operator, case.building_id)
    if report.unit.building_id != case.building_id:
        raise ValidationError(_("Report must belong to the case building."))
    existing = (
        CaseReport.objects.select_for_update()
        .select_related("case")
        .filter(report=report, case__active=True)
        .first()
    )
    if existing is not None:
        if existing.case_id == case.pk:
            return existing
        raise ValidationError(_("Report already belongs to another active case."))
    if case.reports.filter(status=IssueReport.Status.IN_PROGRESS).exists():
        status = IssueReport.Status.IN_PROGRESS
    elif hasattr(case, "proposal"):
        status = IssueReport.Status.PROPOSED
    else:
        status = IssueReport.Status.IN_REVIEW
    if report.is_private and status == IssueReport.Status.PROPOSED:
        raise ValidationError(_("Private requests cannot join a case with a community proposal."))
    link = CaseReport.objects.create(case=case, report=report, grouped_by=operator)
    report.status = status
    report.save(update_fields=["status"])
    record_audit(
        actor=operator,
        membership=membership,
        action="case.group",
        target_type="CaseReport",
        target_id=str(link.pk),
        result="accepted",
        metadata={"case_id": case.pk, "report_id": report.pk},
    )
    return link
