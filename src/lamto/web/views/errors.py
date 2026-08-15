"""Custom 500 handler: Django's default renders without request context, so the
template cannot offer an authenticated user the way back to the Action inbox."""

from __future__ import annotations

from django.http import HttpResponseServerError
from django.template import loader


def server_error(request, template_name="500.html"):
    try:
        authed = bool(getattr(request, "user", None) and request.user.is_authenticated)
    except Exception:
        # Whatever broke the request may also break sessions; render signed-out.
        authed = False
    # No request context: context processors must not run on the failure path.
    return HttpResponseServerError(
        loader.render_to_string(template_name, {"authed": authed})
    )
