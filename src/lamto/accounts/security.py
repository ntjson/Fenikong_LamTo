"""Authentication throttle, re-auth, and privileged-action gates."""

from __future__ import annotations

import hashlib
import time
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.utils import timezone

from lamto.audit.services import record_audit

from .models import AuthThrottleBucket, ManagementMembership
from .services import require_management

RECENT_REAUTH_KEY = "recent_reauth_at"
DEFAULT_REAUTH_MAX_AGE = 300
THROTTLE_MAX_FAILURES = 5
THROTTLE_WINDOW_SECONDS = 15 * 60

# In-flight POST bodies preserved across the reauth hop (never files or secrets).
REAUTH_STASH_KEY = "reauth_stashed_post"
REAUTH_STASH_MAX_AGE_SECONDS = 15 * 60
REAUTH_STASH_MAX_CHARS = 20_000
# Never restore: CSRF, action routing, irreversibility confirms, credentials.
_REAUTH_STASH_DROP = {"csrfmiddlewaretoken", "action", "confirm", "password", "token"}


class RecentAuthRequired(PermissionDenied):
    """Recent re-authentication required; middleware redirects to reauth."""


def throttle_digest(account: str, ip: str | None) -> str:
    normalized = f"{(account or '').strip().lower()}|{(ip or '').strip()}"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def client_ip(request) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return (request.META.get("REMOTE_ADDR") or "").strip()


def _now():
    return timezone.now()


@transaction.atomic
def assert_not_throttled(account: str, ip: str | None) -> None:
    digest = throttle_digest(account, ip)
    bucket = (
        AuthThrottleBucket.objects.select_for_update().filter(key_digest=digest).first()
    )
    if bucket is None:
        return
    now = _now()
    if bucket.locked_until and bucket.locked_until > now:
        raise PermissionDenied(_("Too many authentication attempts. Try again later."))
    if (
        bucket.window_started_at
        and (now - bucket.window_started_at).total_seconds() > THROTTLE_WINDOW_SECONDS
    ):
        # Window expired; caller may proceed (bucket reset happens on next failure/success).
        return


@transaction.atomic
def record_auth_failure(
    account: str, ip: str | None, *, kind: str = "login"
) -> AuthThrottleBucket:
    """Record a failed login/MFA attempt. Never stores password or OTP values."""
    digest = throttle_digest(account, ip)
    bucket, _ = AuthThrottleBucket.objects.select_for_update().get_or_create(
        key_digest=digest,
        defaults={"failure_count": 0, "window_started_at": _now()},
    )
    now = _now()
    if (
        bucket.window_started_at is None
        or (now - bucket.window_started_at).total_seconds() > THROTTLE_WINDOW_SECONDS
    ):
        bucket.failure_count = 1
        bucket.window_started_at = now
        bucket.locked_until = None
    else:
        bucket.failure_count = (bucket.failure_count or 0) + 1
    if bucket.failure_count >= THROTTLE_MAX_FAILURES:
        bucket.locked_until = now + timedelta(seconds=THROTTLE_WINDOW_SECONDS)
    bucket.save(
        update_fields=[
            "failure_count",
            "window_started_at",
            "locked_until",
            "updated_at",
        ]
    )
    return bucket


@transaction.atomic
def record_registration_attempt(account: str, ip: str | None) -> AuthThrottleBucket:
    """Atomically admit and record one public registration attempt."""
    digest = throttle_digest(account, ip)
    bucket, _ = AuthThrottleBucket.objects.select_for_update().get_or_create(
        key_digest=digest,
        defaults={"failure_count": 0, "window_started_at": _now()},
    )
    now = _now()
    if bucket.locked_until and bucket.locked_until > now:
        raise PermissionDenied("Too many registration attempts. Try again later.")
    if (
        bucket.window_started_at is None
        or (now - bucket.window_started_at).total_seconds() > THROTTLE_WINDOW_SECONDS
    ):
        bucket.failure_count = 1
        bucket.window_started_at = now
        bucket.locked_until = None
    else:
        bucket.failure_count = (bucket.failure_count or 0) + 1
    if bucket.failure_count >= THROTTLE_MAX_FAILURES:
        bucket.locked_until = now + timedelta(seconds=THROTTLE_WINDOW_SECONDS)
    bucket.save(
        update_fields=[
            "failure_count",
            "window_started_at",
            "locked_until",
            "updated_at",
        ]
    )
    return bucket


@transaction.atomic
def reset_auth_throttle(account: str, ip: str | None) -> None:
    digest = throttle_digest(account, ip)
    bucket = (
        AuthThrottleBucket.objects.select_for_update().filter(key_digest=digest).first()
    )
    if bucket is None:
        return
    bucket.failure_count = 0
    bucket.window_started_at = None
    bucket.locked_until = None
    bucket.save(
        update_fields=[
            "failure_count",
            "window_started_at",
            "locked_until",
            "updated_at",
        ]
    )


def user_is_otp_verified(request) -> bool:
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    is_verified = getattr(user, "is_verified", None)
    if callable(is_verified):
        return bool(is_verified())
    return False


def require_otp_verified(request) -> None:
    if not user_is_otp_verified(request):
        _deny_sensitive(request, "otp_required")
        raise PermissionDenied("Verified OTP is required.")


def recent_reauth_age_seconds(request) -> float | None:
    raw = request.session.get(RECENT_REAUTH_KEY)
    if raw is None:
        return None
    try:
        return time.time() - float(raw)
    except (TypeError, ValueError):
        return None


def mark_recent_reauth(request) -> None:
    request.session[RECENT_REAUTH_KEY] = time.time()
    request.session.modified = True


def stash_post_for_reauth(request) -> None:
    """Keep typed POST values across the reauth redirect so the hop loses no work.

    File uploads cannot be stashed in the session; the form copy tells the
    manager attachments need re-selecting. Confirm checkboxes are dropped so an
    irreversible action is never re-armed without a fresh human tick.
    """
    if request.method != "POST":
        return
    data = {
        key: values if len(values) > 1 else values[0]
        for key in request.POST
        if key not in _REAUTH_STASH_DROP
        for values in [request.POST.getlist(key)]
    }
    if not data or sum(len(str(v)) for v in data.values()) > REAUTH_STASH_MAX_CHARS:
        return
    request.session[REAUTH_STASH_KEY] = {
        "path": request.path,
        "at": time.time(),
        "data": data,
    }
    request.session.modified = True


def pop_stashed_post(request) -> dict | None:
    """Return the values stashed for this path, once, or None."""
    stash = request.session.get(REAUTH_STASH_KEY)
    if stash is None:
        return None
    if (
        stash.get("path") != request.path
        or time.time() - float(stash.get("at") or 0) > REAUTH_STASH_MAX_AGE_SECONDS
    ):
        return None
    del request.session[REAUTH_STASH_KEY]
    request.session.modified = True
    return stash.get("data") or None


def require_recent_auth(request, max_age_seconds: int = DEFAULT_REAUTH_MAX_AGE) -> None:
    """Require verified OTP and password+OTP re-auth within max_age_seconds."""
    if not getattr(request.user, "is_authenticated", False):
        raise PermissionDenied("Authentication required.")
    require_otp_verified(request)
    age = recent_reauth_age_seconds(request)
    if age is None or age > max_age_seconds:
        _deny_sensitive(
            request, "reauth_required", {"max_age_seconds": max_age_seconds}
        )
        raise RecentAuthRequired("Recent re-authentication is required.")


def _deny_sensitive(request, reason: str, extra: dict | None = None) -> None:
    membership = None
    mid = request.session.get("active_management_id")
    if mid is not None:
        membership = ManagementMembership.objects.filter(
            pk=mid, user=request.user, active=True
        ).first()
    try:
        record_audit(
            request.user if getattr(request.user, "is_authenticated", False) else None,
            require_management(request.user, membership.building_id)
            if membership
            else None,
            "security.sensitive_action",
            "Session",
            str(getattr(request.user, "pk", "") or ""),
            "denied",
            {"reason": reason, **(extra or {})},
        )
    except Exception:
        # Audit attribution may fail for anonymous users; never block denial path.
        pass


def user_has_confirmed_totp(user) -> bool:
    from django_otp.plugins.otp_totp.models import TOTPDevice

    if user is None or not getattr(user, "is_authenticated", False):
        return False
    return TOTPDevice.objects.filter(user=user, confirmed=True).exists()


def require_staff_mfa(request) -> None:
    """Privileged staff workspace entry requires a confirmed TOTP device + OTP session."""
    if not getattr(request.user, "is_authenticated", False):
        raise PermissionDenied("Authentication required.")
    if not user_has_confirmed_totp(request.user):
        raise PermissionDenied("TOTP enrollment is required for staff workspaces.")
    require_otp_verified(request)


def rotate_session(request) -> None:
    """Rotate the session key (login / MFA / reauth) without losing data."""
    try:
        request.session.cycle_key()
    except Exception:
        # Empty session edge case in tests.
        request.session.create()


def renew_management_session(request) -> None:
    """Give the session the persistent rolling Management lifetime (ADR 0001).

    Called when a password login first establishes a Management session and on
    every authenticated Management workspace request. Marks the session modified
    so Django saves it: the server-side expiry moves to 400 days from this
    request and the response re-sends the persistent cookie with the same age.
    """
    request.session.set_expiry(
        timedelta(days=settings.LAMTO_MANAGEMENT_SESSION_MAX_AGE_DAYS)
    )
    request.session.modified = True


def revoke_session(request) -> None:
    """Flush session (logout / explicit revocation)."""
    request.session.flush()
