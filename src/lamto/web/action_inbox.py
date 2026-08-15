"""Management action inbox queries.

The inbox is authoritative for staff work; email is a secondary channel.
Callers pass a single building-scoped management membership.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy

from lamto.accounts.models import ManagementMembership, RegistrationRequest
from lamto.documents.models import QuarantinedUpload
from lamto.evidence.models import BlockchainOutboxEvent, SETTLED_STATUSES
from lamto.finance.models import (
    Settlement,
    Proposal,
    PublishedLedgerEntry,
    VerificationObservation,
)
from lamto.finance.proposals import spending_proposal_cases
from lamto.maintenance.models import (
    IssueReport,
    MaintenanceCase,
    TriageJob,
)


# One vocabulary for the inbox: the filter dropdown and the row titles read
# from the same map, so a filter never returns rows under a different name.
ACTION_KIND_LABELS = {
    "registration": _lazy("Resident registration"),
    "manual_triage": _lazy("Manual triage"),
    "review_report": _lazy("Report review"),
    "deadline_risk": _lazy("Deadline risk"),
    "in_progress_case": _lazy("Case in progress"),
    "proposal_create": _lazy("Proposal creation"),
    "proposal_decision": _lazy("Proposal decision"),
    "settlement_transfer": _lazy("Transfer recording"),
    "settlement_ack": _lazy("Acknowledgement recording"),
    "integrity_mismatch": _lazy("Integrity mismatch"),
    "failed_outbox": _lazy("Failed evidence anchor"),
    "quarantined_upload": _lazy("Quarantined upload"),
}


def _kind_title(kind: str) -> str:
    return str(ACTION_KIND_LABELS[kind])


@dataclass(frozen=True)
class ActionItem:
    kind: str
    title: str
    summary: str
    target_type: str
    target_id: int
    url: str
    priority: int = 50
    deadline_at: datetime | None = None
    amount_vnd: int | None = None

    @property
    def deadline_tone(self) -> str:
        from lamto.web.views.staff_common import deadline_tone

        return deadline_tone(self.deadline_at)


def _building_id(membership) -> int:
    return membership.building_id


def action_items_for(membership: ManagementMembership) -> list[ActionItem]:
    """Return every surviving queue for one active management membership."""
    if membership is None or not membership.active:
        return []
    membership = (
        ManagementMembership.objects.select_related("building", "user")
        .filter(pk=membership.pk, active=True)
        .first()
    )
    if membership is None:
        return []

    items: list[ActionItem] = []
    building_id = _building_id(membership)
    now = timezone.now()

    items.extend(_manual_triage_items(building_id))
    items.extend(_review_queue_items(building_id))
    items.extend(_deadline_risk_items(building_id))
    items.extend(_in_progress_case_items(building_id))
    items.extend(_proposal_create_candidates(building_id))
    items.extend(_proposal_decision_items(building_id))
    items.extend(_settlement_transfer_items(building_id))
    items.extend(_settlement_ack_items(building_id))
    items.extend(_integrity_mismatch_items(building_id))
    items.extend(_failed_outbox_items(building_id))
    items.extend(_quarantined_upload_items(building_id, membership))
    items.extend(_registration_items(building_id))

    # Deduplicate by (kind, target_type, target_id)
    seen = set()
    unique: list[ActionItem] = []
    for item in sorted(items, key=lambda i: (i.priority, i.title, i.target_id)):
        key = (item.kind, item.target_type, item.target_id)
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def _registration_items(building_id: int) -> list[ActionItem]:
    return [
        ActionItem(
            kind="registration",
            title=request.full_name,
            summary=f"{request.unit.label} · {request.phone}",
            target_type="RegistrationRequest",
            target_id=str(request.id),
            url=reverse("web:staff-registration-detail", args=[request.id]),
            priority=40,
        )
        for request in RegistrationRequest.objects.filter(
            building_id=building_id,
            status=RegistrationRequest.Status.PENDING,
        )
        .select_related("unit")
        .order_by("created_at")
    ]


def _manual_triage_items(building_id: int) -> list[ActionItem]:
    items = []
    qs = (
        IssueReport.objects.filter(
            unit__building_id=building_id,
            status__in=[IssueReport.Status.SUBMITTED, IssueReport.Status.IN_REVIEW],
        )
        .filter(
            Q(triage_job__status=TriageJob.Status.NEEDS_MANUAL)
            | Q(triage_job__status=TriageJob.Status.SUCCEEDED, triage_decision__isnull=True)
            | Q(triage_job__isnull=True)
        )
        .exclude(case_reports__case__active=True)
        .distinct()
        .order_by("created_at")[:50]
    )
    for report in qs:
        items.append(
            ActionItem(
                kind="manual_triage",
                title=_kind_title("manual_triage"),
                summary=report.text[:120],
                target_type="IssueReport",
                target_id=report.pk,
                url=reverse("web:staff-report-detail", kwargs={"pk": report.pk}),
                priority=10,
            )
        )
    return items


def _review_queue_items(building_id: int) -> list[ActionItem]:
    return [
        ActionItem(
            kind="review_report", title=_kind_title("review_report"),
            summary=report.text[:120], target_type="IssueReport", target_id=report.pk,
            url=reverse("web:staff-report-detail", kwargs={"pk": report.pk}), priority=11,
        )
        for report in IssueReport.objects.filter(
            building_id=building_id, status=IssueReport.Status.IN_REVIEW,
            triage_decision__isnull=True,
        ).order_by("created_at")[:20]
    ]


def _deadline_risk_items(building_id: int) -> list[ActionItem]:
    items = []
    horizon = timezone.now() + timedelta(hours=24)
    cases = MaintenanceCase.objects.filter(
        building_id=building_id,
        active=True,
        completed_at__isnull=True,
        deadline_at__lt=horizon,
    ).order_by("deadline_at")[:30]
    for case in cases:
        items.append(
            ActionItem(
                kind="deadline_risk",
                title=_kind_title("deadline_risk"),
                summary=_("Case #%(id)s · %(category)s") % {"id": case.pk, "category": case.get_category_display()},
                target_type="MaintenanceCase",
                target_id=case.pk,
                url=reverse("web:case-detail", kwargs={"pk": case.pk}),
                priority=15,
                deadline_at=case.deadline_at,
            )
        )
    return items


def _in_progress_case_items(building_id: int) -> list[ActionItem]:
    return [ActionItem(kind="in_progress_case", title=_kind_title("in_progress_case"),
                       summary=_("Case #%(id)s · %(category)s") % {"id": case.pk, "category": case.get_category_display()},
                       target_type="MaintenanceCase",
                       target_id=case.pk, url=reverse("web:case-detail", kwargs={"pk": case.pk}),
                       priority=20, deadline_at=case.deadline_at)
            for case in MaintenanceCase.objects.filter(
                building_id=building_id, active=True, completed_at__isnull=True,
                reports__status=IssueReport.Status.IN_PROGRESS).distinct().order_by("deadline_at")[:50]]


def _proposal_create_candidates(building_id: int) -> list[ActionItem]:
    items = []
    qs = spending_proposal_cases().filter(
        building_id=building_id,
        proposal__isnull=True,
    ).distinct().order_by("created_at")[:30]
    for case in qs:
        items.append(
            ActionItem(
                kind="proposal_create",
                title=_kind_title("proposal_create"),
                summary=_("Case #%(id)s needs a spending proposal") % {"id": case.pk},
                target_type="MaintenanceCase",
                target_id=case.pk,
                url=reverse("web:proposal-create", kwargs={"pk": case.pk}),
                priority=25,
            )
        )
    return items


def _proposal_decision_items(building_id: int) -> list[ActionItem]:
    return [ActionItem(
        kind="proposal_decision", title=_kind_title("proposal_decision"),
        summary=_("Proposal #%(id)s awaits a proceed decision") % {"id": proposal.pk},
        target_type="Proposal",
        target_id=proposal.pk, url=reverse("web:proposal-detail", kwargs={"pk": proposal.pk}),
        priority=16,
    ) for proposal in Proposal.objects.filter(
        building_id=building_id, status=Proposal.Status.PUBLISHED, decided_at__isnull=True,
    ).order_by("created_at")[:30]]


def _settlement_transfer_items(building_id: int) -> list[ActionItem]:
    return [ActionItem(kind="settlement_transfer", title=_kind_title("settlement_transfer"), summary=_("Proposal #%(id)s") % {"id": p.pk}, target_type="Proposal", target_id=p.pk, url=reverse("web:proposal-detail", kwargs={"pk": p.pk}), priority=16, amount_vnd=p.current_version.amount_vnd) for p in Proposal.objects.filter(building_id=building_id, status=Proposal.Status.COMPLETED, settlement__isnull=True).select_related("current_version")[:40]]


def _settlement_ack_items(building_id: int) -> list[ActionItem]:
    return [ActionItem(kind="settlement_ack", title=_kind_title("settlement_ack"), summary=_("Settlement #%(id)s") % {"id": s.pk}, target_type="Settlement", target_id=s.pk, url=reverse("web:settlement-detail", kwargs={"pk": s.pk}), priority=14, amount_vnd=s.amount_vnd) for s in Settlement.objects.filter(proposal__building_id=building_id, settled_at__isnull=True)[:40]]


def mismatched_ledger_entry_ids(building_id: int, limit: int = 30) -> list[int]:
    """Ledger entries whose LATEST observation is still a mismatch, newest first.

    Shared by the inbox and the Exceptions review surface so both always agree
    on what counts as an open mismatch.
    """
    latest_mismatch = VerificationObservation.objects.filter(
        published_entry__proposal__building_id=building_id,
        result=VerificationObservation.Result.MISMATCH,
    ).order_by("-observed_at")[:limit]
    entry_ids: list[int] = []
    for obs in latest_mismatch:
        if obs.published_entry_id in entry_ids:
            continue
        latest = (
            VerificationObservation.objects.filter(
                published_entry_id=obs.published_entry_id
            )
            .order_by("-observed_at", "-pk")
            .first()
        )
        if latest is None or latest.result != VerificationObservation.Result.MISMATCH:
            continue
        entry_ids.append(obs.published_entry_id)
    return entry_ids


def _integrity_mismatch_items(building_id: int) -> list[ActionItem]:
    return [
        ActionItem(
            kind="integrity_mismatch",
            title=_kind_title("integrity_mismatch"),
            summary=_("Ledger entry #%(id)s") % {"id": entry_id},
            target_type="PublishedLedgerEntry",
            target_id=entry_id,
            url=reverse(
                "web:exception-review", args=["integrity_mismatch", entry_id]
            ),
            priority=8,
        )
        for entry_id in mismatched_ledger_entry_ids(building_id)
    ]


def _failed_outbox_items(building_id: int) -> list[ActionItem]:
    items = []
    # Denormalized building on the outbox event is the tenant key (spec 2.2).
    qs = BlockchainOutboxEvent.objects.filter(
        status=BlockchainOutboxEvent.Status.FAILED,
        building_id=building_id,
    ).order_by("-updated_at")[:30]
    for event in qs:
        items.append(
            ActionItem(
                kind="failed_outbox",
                title=_kind_title("failed_outbox"),
                summary=_("Event %(event_id)s… · %(error)s")
                % {"event_id": event.event_id[:18], "error": event.last_error[:80]},
                target_type="BlockchainOutboxEvent",
                target_id=event.pk,
                url=reverse("web:exception-review", args=["failed_outbox", event.pk]),
                priority=9,
            )
        )
    return items


def _quarantined_upload_items(building_id: int, membership) -> list[ActionItem]:
    items = []
    qs = (
        QuarantinedUpload.objects.filter(building_id=building_id)
        .order_by("-created_at")[:20]
    )
    for upload in qs:
        from lamto.web.templatetags.staff_extras import upload_reason_label

        items.append(
            ActionItem(
                kind="quarantined_upload",
                title=_kind_title("quarantined_upload"),
                summary=f"{upload.filename} · {upload_reason_label(upload.reason)}",
                target_type="QuarantinedUpload",
                target_id=upload.pk,
                url=reverse(
                    "web:exception-review", args=["quarantined_upload", upload.pk]
                ),
                priority=12,
            )
        )
    return items
