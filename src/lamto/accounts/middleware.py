"""Staff workspace security: MFA gate and reauth redirect."""

from __future__ import annotations

from urllib.parse import urlencode

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse

from lamto.accounts.security import (
    RecentAuthRequired,
    require_staff_mfa,
    stash_post_for_reauth,
)

# MFA enrollment/verify must remain reachable before OTP is confirmed.
_MFA_EXEMPT_PREFIXES = (
    "/s/security/mfa/setup/",
    "/s/security/mfa/verify/",
)


class StaffSecurityMiddleware:
    """Enforce staff MFA on every /s/ request.

    - Confirmed TOTP + OTP-verified session required for all /s/ routes
      except MFA setup/verify (so users can enroll and step up).
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

        exempt = any(path.startswith(prefix) for prefix in _MFA_EXEMPT_PREFIXES)
        if not exempt:
            require_staff_mfa(request)

        return None

    def process_exception(self, request, exception):
        if isinstance(exception, RecentAuthRequired):
            stash_post_for_reauth(request)
            next_url = request.get_full_path()
            return redirect(
                f"{reverse('web:reauth')}?{urlencode({'next': next_url})}"
            )
        return None
