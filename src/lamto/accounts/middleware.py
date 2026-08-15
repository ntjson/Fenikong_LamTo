"""Management workspace middleware: session renewal and reauth redirect."""

from __future__ import annotations

from urllib.parse import urlencode

from django.shortcuts import redirect
from django.urls import reverse

from lamto.accounts.models import ManagementMembership
from lamto.accounts.security import (
    RecentAuthRequired,
    renew_management_session,
    stash_post_for_reauth,
)


class ManagementSessionMiddleware:
    """Renew Management sessions on every authenticated /s/ request.

    - An authenticated Management account requesting /s/ renews the session's
      server-side expiry and persistent cookie to 400 days from that request,
      so the session survives inactivity and browser restarts (ADR 0001).
      Non-members are left to the views' membership checks.
    - RecentAuthRequired → redirect to reauth with next=.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        path = request.path or ""
        if not path.startswith("/s/"):
            return None

        user = getattr(request, "user", None)
        if user is None or not getattr(user, "is_authenticated", False):
            return None
        if not ManagementMembership.objects.filter(user=user, active=True).exists():
            return None

        renew_management_session(request)
        return None

    def process_exception(self, request, exception):
        if isinstance(exception, RecentAuthRequired):
            stash_post_for_reauth(request)
            next_url = request.get_full_path()
            return redirect(f"{reverse('web:reauth')}?{urlencode({'next': next_url})}")
        return None
