"""Shared staff routes: action inbox and membership switcher."""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from lamto.finance.selectors import fund_series
from lamto.web.action_inbox import ACTION_KIND_LABELS, action_items_for
from lamto.web.staff import require_management_context, staff_context, switch_building_redirect


logger = logging.getLogger(__name__)


def prepare_record_list(
    request, qs, *, search_fields=(), sorts=(), page_param="page", per_page=20
):
    """Search, sort, and paginate a record list (same pattern as the action inbox).

    ``sorts``: ``((value, label, order_by_fields), ...)``; the first entry is
    the default. A numeric query also matches the record's ID.
    """
    query = (request.GET.get("q") or "").strip()
    if query:
        condition = Q()
        for field in search_fields:
            condition |= Q(**{f"{field}__icontains": query})
        if query.isdigit():
            condition |= Q(pk=int(query))
        qs = qs.filter(condition)
    sort = request.GET.get("sort") or ""
    sort_map = {value: order_by for value, _label, order_by in sorts}
    if sort not in sort_map:
        sort = ""
    if sorts:
        qs = qs.order_by(*sort_map.get(sort, sorts[0][2]))
    page = Paginator(qs, per_page).get_page(request.GET.get(page_param))
    params = request.GET.copy()
    params.pop(page_param, None)
    return {
        "page": page,
        "query": query,
        "sort": sort,
        "sort_options": [
            {"value": value, "label": label, "active": value == sort}
            for value, label, _order in sorts
        ],
        "page_param": page_param,
        "querystring": params.urlencode(),
    }


EXCEPTION_KINDS = {"failed_outbox", "integrity_mismatch", "quarantined_upload"}
ACTION_GROUPS = (
    ("do_now", _("Do now")),
    ("due_soon", _("Due soon")),
    ("exceptions", _("Exceptions")),
)
def _action_group(item):
    if item.kind in EXCEPTION_KINDS:
        return "exceptions"
    if item.kind == "deadline_risk":
        return "due_soon"
    return "do_now"


def prepare_action_inbox(
    items, *, query="", kind="", status="", page_number=1, querystring=""
):
    query = query.strip()
    kind_filters = {
        item.kind: ACTION_KIND_LABELS[item.kind]
        for item in items
        if item.kind in ACTION_KIND_LABELS
    }

    filtered = [
        item
        for item in items
        if (not kind or item.kind == kind)
        and (not status or _action_group(item) == status)
        and (
            not query
            or query.casefold() in f"{item.title} {item.summary}".casefold()
        )
    ]
    page = Paginator(filtered, 20).get_page(page_number)
    grouped = {value: [] for value, _label in ACTION_GROUPS}
    for item in page.object_list:
        grouped[_action_group(item)].append(item)
    status_filters = [
        {"value": value, "label": label, "active": value == status}
        for value, label in ACTION_GROUPS
    ]
    kind_filter_list = [
        {"value": value, "label": label, "active": value == kind}
        for value, label in sorted(kind_filters.items(), key=lambda pair: pair[1])
    ]
    return {
        "groups": [
            {"label": label, "items": grouped[value]}
            for value, label in ACTION_GROUPS
            if grouped[value]
        ],
        "page": page,
        "kind_filters": kind_filter_list,
        "active_kind": kind,
        "status_filters": status_filters,
        "active_status": status,
        "query": query,
        "list_meta": {
            "page": page,
            "query": query,
            "sort": "",
            "sort_options": [],
            "page_param": "page",
            "querystring": querystring,
        },
        "filters": status_filters,
        "filters_active": bool(status or kind or query),
        "secondary_filters": kind_filter_list,
    }


@login_required
@require_GET
def action_inbox(request):
    membership, memberships = require_management_context(request)
    series = fund_series(membership.building_id, range_key="6m")
    items = action_items_for(membership)
    params = request.GET.copy()
    params.pop("page", None)
    inbox = prepare_action_inbox(
        items,
        query=request.GET.get("q", ""),
        kind=request.GET.get("kind", ""),
        status=request.GET.get("status", ""),
        page_number=request.GET.get("page", 1),
        querystring=params.urlencode(),
    )
    return render(
        request,
        "web/staff/action_inbox.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="inbox",
            fund_chart_points=[
                {**row, "period_start": row["period_start"].isoformat()}
                for row in series
            ],
            fund_balance_vnd=series[-1]["balance_vnd"] if series else 0,
            fund_link_ok=True,
            action_groups=inbox["groups"],
            action_page=inbox["page"],
            kind_filters=inbox["kind_filters"],
            active_kind=inbox["active_kind"],
            status_filters=inbox["status_filters"],
            active_status=inbox["active_status"],
            inbox_query=inbox["query"],
            list_meta=inbox["list_meta"],
            filters=inbox["filters"],
            filters_active=inbox["filters_active"],
            secondary_filters=inbox["secondary_filters"],
            secondary_filter_param="kind",
            secondary_filter_label=_("Task type"),
            search_label=_("Search tasks"),
            search_placeholder=_("Case, work, payment…"),
            pagination_label=_("Action inbox pages"),
        ),
    )


@login_required
@require_http_methods(["GET", "POST"])
def switch_building(request):
    return switch_building_redirect(request)


@login_required
@require_GET
def staff_home(request):
    require_management_context(request)
    return redirect("web:action-inbox")


ACCOUNTABILITY_STAGES = (
    ("report", _("Report")),
    ("triage", _("Triage")),
    ("work", _("Work")),
    ("proposal", _("Proposal publication")),
    ("settlement", _("Settlement")),
    ("publication", _("Publication")),
)


STAGE_STATE_LABELS = {
    "complete": _("Completed"),
    "current": _("Current step"),
    "blocked": _("Blocked"),
    "upcoming": _("Not started"),
    # Snapshot signed; independent chain confirmation / finalize still pending.
    "pending": _("Awaiting confirmation"),
}

# Proposal statuses that clear the proposal stage.
_PROPOSAL_AUTHORIZED = frozenset({"IN_PROGRESS", "COMPLETED"})
_WORK_DONE = frozenset({"AWAITING_ACCEPTANCE", "ACCEPTED", "CLOSED"})
_WORK_CLOSED = frozenset({"ACCEPTED", "CLOSED"})


def deadline_tone(deadline_at, *, now=None) -> str:
    """Neutral by default; amber near due (48h); red when past due."""
    if deadline_at is None:
        return "neutral"
    from datetime import timedelta

    from django.utils import timezone

    now = now or timezone.now()
    if timezone.is_naive(deadline_at):
        deadline_at = timezone.make_aware(deadline_at, timezone.utc)
    if deadline_at < now:
        return "overdue"
    if deadline_at <= now + timedelta(hours=48):
        return "soon"
    return "neutral"


def accountability_chain(
    current: str | None, *, blocked: bool = False, pending: bool = False
):
    """Return ordered stages for an explicit current key (or all-complete when None).

    ``pending`` marks the current stage as awaiting independent confirmation
    (amber) without treating it as complete.
    """
    keys = [key for key, _ in ACCOUNTABILITY_STAGES]
    if current is None:
        current_index = len(keys)
    else:
        current_index = keys.index(current)
    stages = []
    for index, (key, label) in enumerate(ACCOUNTABILITY_STAGES):
        if index == current_index and blocked:
            state = "blocked"
        elif index == current_index and pending:
            state = "pending"
        elif index == current_index:
            state = "current"
        elif index < current_index:
            state = "complete"
        else:
            state = "upcoming"
        stages.append(
            {
                "key": key,
                "label": label,
                "state": state,
                "state_label": STAGE_STATE_LABELS[state],
            }
        )
    return stages


def _related_or_none(obj, attr: str):
    if obj is None:
        return None
    from django.core.exceptions import ObjectDoesNotExist

    try:
        return getattr(obj, attr)
    except (ObjectDoesNotExist, AttributeError):
        # AttributeError: not every record type carries every relation
        # (e.g. Proposal has no outbox_event; only its current_version does).
        return None


def _publication_still_pending(entry, proposal, settlement) -> bool:
    """True until an outbox event is chain-confirmed (LOCAL_SIGNED stays pending)."""
    from lamto.evidence.models import BlockchainOutboxEvent, EvidenceLevel

    events = []
    if entry is not None:
        for attr in ("settlement", "proposal"):
            related = _related_or_none(entry, attr)
            if related is not None:
                event = _related_or_none(related, "outbox_event")
                if event is None and attr == "proposal":
                    version = _related_or_none(related, "current_version")
                    event = _related_or_none(version, "outbox_event") if version else None
                if event is not None:
                    events.append(event)
    if settlement is not None:
        event = _related_or_none(settlement, "outbox_event")
        if event is not None:
            events.append(event)
    if proposal is not None:
        version = _related_or_none(proposal, "current_version")
        event = _related_or_none(version, "outbox_event") if version else None
        if event is not None:
            events.append(event)
    if not events:
        return True
    for event in events:
        level = getattr(event, "evidence_level", None) or ""
        status = getattr(event, "status", None) or ""
        if level == EvidenceLevel.CHAIN_CONFIRMED or status == BlockchainOutboxEvent.Status.CONFIRMED:
            continue
        return True
    return False


def resolve_accountability_stage(
    source=None,
    *,
    proposal=None,
    settlement=None,
    entry=None,
    case=None,
    published: bool | None = None,
    publication_pending: bool | None = None,
) -> tuple[str | None, bool, bool]:
    """Derive (current_stage_key, blocked, publication_pending) from real state.

    Returns ``(None, False, False)`` when every stage is complete. Pass ``published`` / ``publication_pending``
    to skip DB lookups (tests and pre-resolved views).

    Publication happens atomically with settlement.
    """
    from lamto.finance.models import PublishedLedgerEntry
    from lamto.finance.models.execution import Settlement
    from lamto.finance.models.proposals import Proposal
    from lamto.maintenance.models import MaintenanceCase

    if source is not None:
        if isinstance(source, PublishedLedgerEntry):
            entry = source
        elif isinstance(source, Settlement):
            settlement = source
        elif isinstance(source, Proposal):
            proposal = source
        elif isinstance(source, MaintenanceCase):
            case = source

    if proposal is None and settlement is not None:
        proposal = settlement.proposal
    if case is None and proposal is not None:
        case = getattr(proposal, "case", None)
    if proposal is None and case is not None:
        proposal = _related_or_none(case, "proposal")
    if settlement is None and proposal is not None:
        settlement = _related_or_none(proposal, "settlement")
    if entry is None and proposal is not None:
        entry = _related_or_none(proposal, "published_ledger_entry")
    if entry is None and case is not None:
        entry = PublishedLedgerEntry.objects.filter(case=case).first()

    # Publication is complete only when the anchor is chain-confirmed — a ledger
    # row alone is not enough (matches evidence_level, not a verified boolean).
    if entry is not None or published is True:
        if publication_pending is None:
            publication_pending = _publication_still_pending(entry, proposal, settlement)
        if publication_pending:
            return "publication", False, True
        return None, False, False

    if case is not None:
        if settlement is not None and settlement.settled_at is not None:
            return "publication", False, False
        proposal_status = getattr(proposal, "status", None) if proposal else None
        if proposal_status in _PROPOSAL_AUTHORIZED:
            return "settlement", False, False
        if proposal_status == Proposal.Status.NOT_PROCEEDING or proposal_status in {"NOT_PROCEEDING", "REJECTED"}:
            return "proposal", True, False
        if proposal is not None:
            return "proposal", False, False
        return ("settlement", False, False) if case.completed_at else ("work", False, False)

    if proposal is not None:
        if settlement is not None and settlement.settled_at is not None:
            return "publication", False, False
        if proposal.status in _PROPOSAL_AUTHORIZED:
            return "settlement", False, False
        if proposal.status == Proposal.Status.NOT_PROCEEDING:
            return "proposal", True, False
        return "proposal", False, False

    return "report", False, False


def accountability_chain_for(
    source=None, *, blocked: bool | None = None, pending: bool | None = None, **kwargs
):
    """Compute the chain from a domain record instead of a hard-coded page stage."""
    current, derived_blocked, derived_pending = resolve_accountability_stage(
        source, **kwargs
    )
    return accountability_chain(
        current,
        blocked=derived_blocked if blocked is None else blocked,
        pending=derived_pending if pending is None else pending,
    )
