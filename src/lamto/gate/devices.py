"""Issue and authenticate reader credentials without storing plaintext tokens."""

import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from lamto.accounts.security import (
    assert_not_throttled,
    record_auth_failure,
    reset_auth_throttle,
)

from .models import GateDevice, GateDeviceCredential

AUTH_SCHEME = "GateDevice"
TOKEN_BYTES = 32
_THROTTLE_ACCOUNT = "gate_device"


class GateAuthenticationFailed(Exception):
    code = "gate_device_unauthenticated"


class GateCredentialRevoked(GateAuthenticationFailed):
    code = "gate_device_revoked"


class GateCredentialExpired(GateAuthenticationFailed):
    code = "gate_device_expired"


def _digest(token: str) -> str:
    return hashlib.sha256((token or "").encode()).hexdigest()


def token_from_header(value: str | None) -> str:
    parts = (value or "").split()
    return parts[1] if len(parts) == 2 and parts[0].lower() == AUTH_SCHEME.lower() else ""


def issue_credential(device, membership) -> tuple[GateDeviceCredential, str]:
    token = secrets.token_urlsafe(TOKEN_BYTES)
    credential = GateDeviceCredential.objects.create(
        device=device, token_sha256=_digest(token), created_by=membership.user
    )
    return credential, token


def rotate_credential(
    device, membership, *, grace_hours: int | None = None
) -> tuple[GateDeviceCredential, str]:
    grace = settings.GATE_CREDENTIAL_ROTATION_GRACE_HOURS if grace_hours is None else grace_hours
    expiry = timezone.now() + timedelta(hours=grace)
    with transaction.atomic():
        GateDeviceCredential.objects.filter(device=device, revoked_at__isnull=True).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=expiry)
        ).update(expires_at=expiry)
        return issue_credential(device, membership)


def revoke_credential(credential, membership) -> GateDeviceCredential:
    credential.revoked_at = timezone.now()
    credential.revoked_by = membership.user
    credential.save(update_fields=["revoked_at", "revoked_by"])
    return credential


def authenticate_device(token: str, *, ip: str | None = None) -> GateDeviceCredential:
    assert_not_throttled(_THROTTLE_ACCOUNT, ip)
    credential = (
        GateDeviceCredential.objects.select_related("device", "device__building")
        .filter(token_sha256=_digest(token))
        .first()
    )
    if credential is None or not credential.device.active:
        record_auth_failure(_THROTTLE_ACCOUNT, ip, kind="gate_device")
        raise GateAuthenticationFailed("Invalid gate device credential.")
    if credential.revoked_at is not None:
        record_auth_failure(_THROTTLE_ACCOUNT, ip, kind="gate_device")
        raise GateCredentialRevoked("This reader's credential was revoked.")
    if not credential.is_valid():
        record_auth_failure(_THROTTLE_ACCOUNT, ip, kind="gate_device")
        raise GateCredentialExpired("This reader's credential has expired.")

    reset_auth_throttle(_THROTTLE_ACCOUNT, ip)
    hour = timezone.now().replace(minute=0, second=0, microsecond=0)
    if credential.device.last_seen_hour != hour:
        GateDevice.objects.filter(pk=credential.device_id).update(last_seen_hour=hour)
        credential.device.last_seen_hour = hour
    return credential
