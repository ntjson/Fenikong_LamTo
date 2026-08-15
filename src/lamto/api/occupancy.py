"""X-LamTo-Occupancy resolution (spec 3.4).

The server validates the header against the caller's own active occupancies
and derives unit + building from the validated occupancy. A client-supplied
building ID is never trusted or accepted. Sole active occupancy -> auto-
selected when the header is absent. Multiple and no header -> 422. An ID that
is not the caller's active occupancy -> 404 (existence not revealed).
"""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from rest_framework import exceptions

from lamto.accounts.tenancy import TenantContext, active_occupancies
from lamto.api.problems import OccupancySelectionRequired

OCCUPANCY_HEADER = "X-LamTo-Occupancy"

# Shared OpenAPI parameter for tenant-list / tenant-object routes.
OCCUPANCY_HEADER_PARAMETER = OpenApiParameter(
    name=OCCUPANCY_HEADER,
    type=OpenApiTypes.INT,
    location=OpenApiParameter.HEADER,
    required=False,
    description=(
        "Active occupancy id for the authenticated resident. Required when the "
        "caller has multiple active occupancies; omitted when exactly one is "
        "auto-selected. Invalid or foreign ids yield 404."
    ),
)


def resolve_api_occupancy(request):
    """Return (occupancy, TenantContext) for the authenticated resident."""
    occupancies = list(active_occupancies(request.user))
    if not occupancies:
        raise exceptions.PermissionDenied("An active resident occupancy is required.")
    raw = request.headers.get(OCCUPANCY_HEADER)
    if raw is None:
        if len(occupancies) > 1:
            raise OccupancySelectionRequired()
        selected = occupancies[0]
    else:
        try:
            wanted = int(raw)
        except (TypeError, ValueError):
            raise exceptions.NotFound("Occupancy not found.")
        selected = next((o for o in occupancies if o.pk == wanted), None)
        if selected is None:
            raise exceptions.NotFound("Occupancy not found.")
    return selected, TenantContext.from_occupancy(selected)
