"""Management session helpers: active building membership + workspace nav."""

from __future__ import annotations

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from lamto.accounts.models import ManagementMembership
from lamto.accounts.security import require_staff_mfa

SESSION_MANAGEMENT_KEY = "active_management_id"


def user_memberships(user):
    return (
        ManagementMembership.objects.select_related("building")
        .filter(user=user, active=True)
        .order_by("building__name", "pk")
    )


def resolve_active_management(request, *, building_id=None):
    memberships = list(user_memberships(request.user))
    if not memberships:
        raise PermissionDenied("An active management membership is required.")

    candidate = building_id
    if candidate is None:
        candidate = request.GET.get("building") or request.POST.get("building")
    if candidate is None:
        candidate = request.session.get(SESSION_MANAGEMENT_KEY)

    selected = None
    if candidate is not None:
        try:
            cid = int(candidate)
        except (TypeError, ValueError):
            cid = None
        if cid is not None:
            selected = next((m for m in memberships if m.pk == cid), None)
    if selected is None:
        selected = memberships[0]

    request.session[SESSION_MANAGEMENT_KEY] = selected.pk
    return selected, memberships


def require_management_context(request):
    require_staff_mfa(request)
    return resolve_active_management(request)


def nav_items_for(membership) -> list[dict]:
    # ≤5 top-level items (working-memory); secondary destinations live in sub-navs.
    return [
        {"label": _("Inbox"), "url_name": "web:action-inbox", "active_key": "inbox"},
        {"label": _("Cases"), "url_name": "web:case-list", "active_key": "cases"},
        {"label": _("Finance"), "url_name": "web:proposal-list", "active_key": "finance"},
        {"label": _("Building"), "url_name": "web:gate-queue", "active_key": "building"},
        {"label": _("Ops"), "url_name": "web:ops-health", "active_key": "ops"},
    ]


def finance_nav_items_for(membership) -> list[dict[str, str]]:
    return [
        {"label": _("Proposals"), "url_name": "web:proposal-list", "active_key": "proposals"},
        {"label": _("New proposal"), "url_name": "web:standalone-proposal-create", "active_key": "proposal-create"},
        {"label": _("Settlements"), "url_name": "web:settlement-list", "active_key": "settlements"},
        {"label": _("Fund"), "url_name": "web:fund-home", "active_key": "fund"},
    ]


def building_nav_items_for(membership) -> list[dict[str, str]]:
    return [
        {"label": _("Gate"), "url_name": "web:gate-queue", "active_key": "gate"},
        {
            "label": _("Registrations"),
            "url_name": "web:staff-registration-list",
            "active_key": "registrations",
        },
        {
            "label": _("Announcements"),
            "url_name": "web:staff-announcement-list",
            "active_key": "announcements",
        },
        {"label": _("Bills"), "url_name": "web:staff-bill-list", "active_key": "bills"},
    ]


def gate_nav_items_for(membership) -> list[dict[str, str]]:
    return [
        {"label": _("Review"), "url_name": "web:gate-queue", "active_key": "review"},
        {"label": _("Registrations"), "url_name": "web:gate-registrations", "active_key": "registrations"},
        {"label": _("Readers"), "url_name": "web:gate-devices", "active_key": "devices"},
        {"label": _("Activity"), "url_name": "web:gate-log", "active_key": "activity"},
    ]


def ops_nav_items_for(membership) -> list[dict[str, str]]:
    return [
        {"label": _("Health"), "url_name": "web:ops-health", "active_key": "health"},
        {"label": _("Exceptions"), "url_name": "web:exception-list", "active_key": "exceptions"},
        {"label": _("Metrics"), "url_name": "web:pilot-metrics", "active_key": "metrics"},
        {"label": _("Exports"), "url_name": "web:export-home", "active_key": "exports"},
    ]


def staff_context(request, membership, memberships, *, nav_active=None, **extra):
    nav_items = nav_items_for(membership)
    # Map legacy section keys onto the 5 top-level groups.
    top_active = {
        "inbox": "inbox",
        "cases": "cases",
        "finance": "finance",
        "gate": "building",
        "registrations": "building",
        "announcements": "building",
        "bills": "building",
        "building": "building",
        "ops": "ops",
        "exports": "ops",
    }.get(nav_active, nav_active)
    for item in nav_items:
        item["is_active"] = bool(top_active) and item.get("active_key") == top_active
    return {
        "membership": membership,
        "memberships": memberships,
        "membership_count": len(memberships) if memberships is not None else 0,
        "nav_items": nav_items,
        "nav_active": nav_active,
        "nav_top_active": top_active,
        "finance_nav_items": finance_nav_items_for(membership),
        "building_nav_items": building_nav_items_for(membership),
        "gate_nav_items": gate_nav_items_for(membership),
        "ops_nav_items": ops_nav_items_for(membership),
        **extra,
    }


def switch_building_redirect(request):
    building = request.POST.get("building") or request.GET.get("building")
    membership, _memberships = resolve_active_management(request, building_id=building)
    request.session[SESSION_MANAGEMENT_KEY] = membership.pk
    return redirect("web:action-inbox")
