"""Resident API auth services — login identity, deactivation, token cleanup.

Primary path for deactivation/token revocation (clarification 5). Signals in
``lamto.api.signals`` remain a safety net for ``.save()`` paths; bulk
``QuerySet.update()`` bypasses signals, so callers must use these services or
call ``revoke_tokens_if_no_active_occupancy`` / ``deactivate_*`` defensively.
"""

from __future__ import annotations

import logging

from django.contrib.auth import get_user_model
from knox.models import AuthToken

from lamto.accounts.backends import normalize_phone
from lamto.accounts.tenancy import active_occupancies

logger = logging.getLogger("lamto.api")

# External detail shown for every failed resident login (clarification 2).
INVALID_CREDENTIALS_DETAIL = "Invalid credentials."


def canonicalize_login_identifier(raw: str) -> str:
    """Normalize phone/email so throttle keys and lookups share one account key.

    Phone forms → local ``0xxxxxxxxx`` via ``normalize_phone``.
    Otherwise email case-fold (Django ``normalize_email``).
    """
    value = (raw or "").strip()
    phone = normalize_phone(value)
    if phone is not None:
        return phone
    # Full case-fold so mixed-case emails share one throttle key (clarification 1).
    # Django normalize_email only lowercases the domain; we lower the whole string.
    return get_user_model().objects.normalize_email(value).lower()


def log_auth_outcome(
    *,
    reason: str,
    identifier: str,
    user_id: int | None = None,
    ip: str | None = None,
) -> None:
    """Structured internal log for auth outcomes (distinct reasons; generic externally)."""
    logger.info(
        "auth.login reason=%s identifier=%s user_id=%s ip=%s",
        reason,
        identifier,
        user_id if user_id is not None else "",
        ip or "",
    )


def revoke_user_tokens(user) -> int:
    """Delete all knox tokens for ``user``. Returns number of tokens deleted."""
    deleted, _ = AuthToken.objects.filter(user=user).delete()
    return deleted


def revoke_tokens_if_no_active_occupancy(user) -> int:
    """Defensive cleanup: revoke tokens when the user has no active occupancy.

    Safe to call after bulk ``QuerySet.update()`` that bypassed post_save signals.
    Returns the number of tokens deleted (0 if any active occupancy remains).
    """
    if active_occupancies(user).exists():
        return 0
    deleted = revoke_user_tokens(user)
    if deleted:
        log_auth_outcome(
            reason="tokens_revoked_no_active_occupancy",
            identifier=str(getattr(user, "email", "") or ""),
            user_id=getattr(user, "pk", None),
        )
    return deleted


def deactivate_occupancy(occupancy, *, reason: str = "") -> None:
    """Deactivate an occupancy and revoke tokens if it was the user's last active one.

    Supported path for occupancy deactivation that must not leave live knox tokens.
    """
    if occupancy.active:
        occupancy.active = False
        occupancy.save(update_fields=["active"])
    # Always run defensive cleanup (covers signal-bypass if save was skipped).
    revoke_tokens_if_no_active_occupancy(occupancy.user)
    logger.info(
        "occupancy.deactivated occupancy_id=%s user_id=%s reason=%s",
        occupancy.pk,
        occupancy.user_id,
        reason or "",
    )


def deactivate_occupancies(queryset, *, reason: str = "") -> int:
    """Bulk-deactivate occupancies and revoke knox tokens for users left with none.

    Preferred path for multi-row deactivation. Uses ``QuerySet.update()`` then
    defensive cleanup so residual knox tokens are not left until re-login.
    Returns the number of rows updated to inactive.
    """
    active_qs = queryset.filter(active=True)
    user_ids = list(active_qs.values_list("user_id", flat=True).distinct())
    updated = active_qs.update(active=False)
    User = get_user_model()
    for user in User.objects.filter(pk__in=user_ids):
        revoke_tokens_if_no_active_occupancy(user)
    if updated:
        logger.info(
            "occupancies.bulk_deactivated count=%s user_count=%s reason=%s",
            updated,
            len(user_ids),
            reason or "",
        )
    return updated


def deactivate_user(user, *, reason: str = "") -> None:
    """Deactivate a user and always revoke all of their knox tokens."""
    if user.is_active:
        user.is_active = False
        user.save(update_fields=["is_active"])
    # Always revoke even if already inactive (bulk update then service cleanup).
    revoke_user_tokens(user)
    logger.info(
        "user.deactivated user_id=%s reason=%s",
        user.pk,
        reason or "",
    )
