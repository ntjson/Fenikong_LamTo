"""Tenant-context resolution (spec 2.3 layer 1, 2.4).

Staff requests already carry their tenant context as the active
ManagementMembership (lamto.web.staff.resolve_active_membership); the
membership IS the staff context. Resident requests resolve an explicit active
ResidentOccupancy here — never `.first()` by accident. TenantContext is the
frozen carrier handed to selectors by both presentation layers (templates now,
API later).
"""

from __future__ import annotations

from dataclasses import dataclass

from django.core.exceptions import PermissionDenied
from django.http import Http404

from lamto.accounts.models import ResidentOccupancy

SESSION_OCCUPANCY_KEY = "active_occupancy_id"


@dataclass(frozen=True)
class TenantContext:
    building_id: int
    actor: str  # "resident" | "staff"
    occupancy_id: int | None = None
    membership_id: int | None = None

    @classmethod
    def from_occupancy(cls, occupancy) -> "TenantContext":
        return cls(
            building_id=occupancy.unit.building_id,
            actor="resident",
            occupancy_id=occupancy.pk,
        )

    @classmethod
    def from_membership(cls, membership) -> "TenantContext":
        return cls(
            building_id=membership.building_id,
            actor="staff",
            membership_id=membership.pk,
        )


def active_occupancies(user):
    return (
        ResidentOccupancy.objects.select_related("unit__building")
        .filter(user=user, active=True)
        .order_by("pk")
    )


def resolve_resident_occupancy(request, *, occupancy_id=None):
    """Resolve and pin the resident's active occupancy for this request.

    Priority: explicit occupancy_id -> session -> sole/first occupancy.
    An explicit id that is not the caller's own active occupancy raises 404
    (cross-tenant convention); a stale session id silently falls back and
    repins. Raises PermissionDenied when the user has no active occupancy.
    Returns (selected, all_active) so views can render the switcher.
    """
    occupancies = list(active_occupancies(request.user))
    if not occupancies:
        raise PermissionDenied("Active resident occupancy is required.")

    def _find(candidate):
        try:
            cid = int(candidate)
        except (TypeError, ValueError):
            return None
        return next((o for o in occupancies if o.pk == cid), None)

    selected = None
    if occupancy_id is not None:
        selected = _find(occupancy_id)
        if selected is None:
            raise Http404("Occupancy not found.")
    if selected is None:
        session_id = request.session.get(SESSION_OCCUPANCY_KEY)
        if session_id is not None:
            selected = _find(session_id)
    if selected is None:
        selected = occupancies[0]
    if request.session.get(SESSION_OCCUPANCY_KEY) != selected.pk:
        request.session[SESSION_OCCUPANCY_KEY] = selected.pk
    return selected, occupancies
