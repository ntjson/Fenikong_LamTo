"""Authentication throttling, session lifecycle, and Management gates."""

from __future__ import annotations

import hashlib
import time
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.utils import timezone

from .models import AuthThrottleBucket

THROTTLE_MAX_FAILURES = 5
THROTTLE_WINDOW_SECONDS = 15 * 60


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
    """Record a failed login attempt. Never stores passwords."""
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


def rotate_session(request) -> None:
    """Rotate the session key (login) without losing data."""
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
