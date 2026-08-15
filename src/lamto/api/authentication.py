"""Resident API knox authentication with occupancy token cleanup.

After a knox token authenticates a user, if they have no active occupancy
(e.g. bulk ``QuerySet.update(active=False)`` bypassed post_save signals),
all of their knox tokens are revoked and the request is treated as
unauthenticated. Prefer ``deactivate_occupancy`` /
``deactivate_occupancies`` / ``deactivate_user`` for writers; this is the
automatic invariant so residual tokens cannot stay live until re-login.
"""

from __future__ import annotations

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object
from knox.auth import TokenAuthentication
from rest_framework import exceptions

from lamto.accounts.tenancy import active_occupancies
from lamto.api.services import revoke_tokens_if_no_active_occupancy


class ResidentTokenAuthentication(TokenAuthentication):
    """Knox token auth that revokes tokens when the user lost all occupancies."""

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None
        user, auth_token = result
        if active_occupancies(user).exists():
            return result
        # Signal-bypass deactivation may leave live tokens; clean them now.
        revoke_tokens_if_no_active_occupancy(user)
        raise exceptions.AuthenticationFailed(
            "Invalid token or account is not eligible for the resident API."
        )


class ResidentTokenScheme(OpenApiAuthenticationExtension):
    """Reuse knoxApiToken security scheme for the resident auth subclass."""

    target_class = "lamto.api.authentication.ResidentTokenAuthentication"
    name = "knoxApiToken"
    match_subclasses = True
    priority = 1

    def get_security_definition(self, auto_schema):
        return build_bearer_security_scheme_object(
            header_name="Authorization",
            token_prefix=self.target.authenticate_header(""),
        )
