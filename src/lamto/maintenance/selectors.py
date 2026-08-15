"""Read selectors for resident-owned maintenance records (spec 2.3, layer 2)."""

from django.db.models import Prefetch

from lamto.maintenance.models import (
    BuildingLocation,
    CaseReport,
    CompletionRating,
    IssueReport,
    WorkUpdate,
    WorkUpdateEvidence,
)


def resident_reports(user):
    """Reports the user submitted, newest first (ownership scope)."""
    return (
        IssueReport.objects.filter(reporter=user)
        .select_related("unit", "selected_location")
        .order_by("-created_at", "-pk")
    )


def rateable_cases(user, report):
    """Completed cases for the report that the user has not rated yet."""
    case_ids = CaseReport.objects.filter(report=report).values_list("case_id", flat=True)
    rated = CompletionRating.objects.filter(resident=user).values_list("case_id", flat=True)
    from .models import MaintenanceCase
    return MaintenanceCase.objects.filter(pk__in=case_ids, completed_at__isnull=False).exclude(pk__in=rated)


def resident_report_timeline(report):
    """Ownership timeline for one report (spec 3.3): triage -> case -> work -> settlement."""
    triage_job = getattr(report, "triage_job", None)
    decision = getattr(report, "triage_decision", None)
    rated_ids = set(
        CompletionRating.objects.filter(resident_id=report.reporter_id).values_list(
            "case_id", flat=True
        )
    )
    cases = []
    updates = Prefetch(
        "case__updates",
        queryset=WorkUpdate.objects.order_by("pk").prefetch_related(
            Prefetch(
                "evidence_links",
                queryset=WorkUpdateEvidence.objects.select_related("version").order_by("pk"),
                to_attr="timeline_evidence_links",
            )
        ),
        to_attr="timeline_updates",
    )
    for link in CaseReport.objects.filter(report=report).select_related("case").prefetch_related(
        updates
    ).order_by("case_id"):
        case = link.case
        timeline_updates = []
        for update in case.timeline_updates:
            timeline_updates.append(
                {
                    "id": update.pk,
                    "cause": update.cause,
                    "result": update.result,
                    "created_at": update.created_at,
                    "photos": [
                        {
                            "id": link.version.pk,
                            "filename": link.version.filename,
                            "kind": link.kind,
                        }
                        for link in update.timeline_evidence_links
                    ],
                }
            )
        cases.append(
            {
                "id": case.pk,
                "category": case.category,
                "urgency": case.urgency,
                "deadline_at": case.deadline_at,
                "active": case.active,
                "completed_at": case.completed_at,
                "closed_at": case.closed_at,
                "updates": timeline_updates,
                "can_rate": case.completed_at is not None and case.pk not in rated_ids,
            }
        )
    info = report.info_requests.filter(resolved_at__isnull=True).first()
    from lamto.finance.models import PublishedLedgerEntry

    ledger_entry_ids = list(
        PublishedLedgerEntry.objects.filter(case__reports=report)
        .order_by("published_at", "pk")
        .values_list("pk", flat=True)
    )
    return {
        "id": report.pk,
        "text": report.text,
        "status": report.status,
        "declined_reason": report.declined_reason or None,
        "is_private": report.is_private,
        "open_info_request": (
            {"id": info.pk, "message": info.message, "created_at": info.created_at}
            if info else None
        ),
        "location_path_snapshot": report.location_path_snapshot,
        "unit_label": report.unit.label,
        "created_at": report.created_at,
        "triage_status": triage_job.status if triage_job is not None else None,
        "category": decision.category if decision is not None else None,
        "photos": [
            {
                "id": rp.version.pk,
                "filename": rp.version.filename,
                "sha256": rp.version.sha256,
            }
            for rp in report.photos.select_related("version").order_by("pk")
        ],
        "cases": cases,
        "ledger_entry_ids": ledger_entry_ids,
    }


def active_location_tree(building_id):
    """Active locations for one building, ordered so parents precede siblings (spec 3.3)."""
    return (
        BuildingLocation.objects.filter(building_id=building_id, active=True)
        .order_by("parent_id", "name", "pk")
    )
