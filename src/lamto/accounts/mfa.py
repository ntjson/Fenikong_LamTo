"""TOTP enrollment and verification helpers (django-otp)."""

from __future__ import annotations

import hashlib
import secrets

from django.core.exceptions import PermissionDenied, ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django_otp import DEVICE_ID_SESSION_KEY, user_has_device
from django_otp.plugins.otp_totp.models import TOTPDevice

from lamto.audit.services import record_audit

from .security import (
    client_ip,
    mark_recent_reauth,
    record_auth_failure,
    reset_auth_throttle,
    rotate_session,
)


def confirmed_totp_devices(user):
    return TOTPDevice.objects.filter(user=user, confirmed=True)


def pending_totp_device(user) -> TOTPDevice | None:
    return TOTPDevice.objects.filter(user=user, confirmed=False).order_by("-id").first()


def begin_totp_enrollment(user, *, name: str = "default") -> TOTPDevice:
    """Create (or replace) an unconfirmed TOTP device for enrollment."""
    if not user or not user.is_authenticated:
        raise PermissionDenied("Authentication required.")
    with transaction.atomic():
        TOTPDevice.objects.filter(user=user, confirmed=False).delete()
        # django-otp generates a random key when key is empty on save for some versions;
        # set an explicit key for portability.
        device = TOTPDevice.objects.create(
            user=user,
            name=name[:64] or "default",
            confirmed=False,
            key=secrets.token_hex(20),
        )
    membership = user.managementmembership_set.filter(active=True).first()
    try:
        record_audit(
            user,
            membership,
            "security.mfa.enroll_begin",
            "TOTPDevice",
            str(device.pk),
            "accepted",
            {"device_name": device.name},
        )
    except Exception:
        pass
    return device


def confirm_totp_enrollment(user, token: str, *, request=None) -> TOTPDevice:
    device = pending_totp_device(user)
    if device is None:
        raise ValidationError(_("No pending TOTP enrollment."))
    if not device.verify_token(str(token).strip()):
        if request is not None:
            record_auth_failure(user.email, client_ip(request), kind="mfa")
            _audit_mfa(user, "security.mfa.enroll_fail", device, "denied")
        raise ValidationError(_("Invalid TOTP token."))
    device.confirmed = True
    device.save(update_fields=["confirmed"])
    # Drop other unconfirmed leftovers.
    TOTPDevice.objects.filter(user=user, confirmed=False).exclude(pk=device.pk).delete()
    if request is not None:
        reset_auth_throttle(user.email, client_ip(request))
        _bind_device_to_session(request, device)
        rotate_session(request)
        mark_recent_reauth(request)
    _audit_mfa(user, "security.mfa.enroll_confirm", device, "accepted")
    return device


def verify_totp_for_session(user, token: str, *, request) -> TOTPDevice:
    """Verify a TOTP token, bind the device to the session, rotate session key."""
    if request is None:
        raise ValidationError(_("Request is required."))
    account = getattr(user, "email", "") or ""
    ip = client_ip(request)
    devices = list(confirmed_totp_devices(user))
    if not devices:
        raise ValidationError(_("No confirmed TOTP device."))
    token = str(token).strip()
    for device in devices:
        if device.verify_token(token):
            reset_auth_throttle(account, ip)
            _bind_device_to_session(request, device)
            rotate_session(request)
            mark_recent_reauth(request)
            _audit_mfa(user, "security.mfa.verify", device, "accepted")
            return device
    record_auth_failure(account, ip, kind="mfa")
    _audit_mfa(user, "security.mfa.verify", devices[0], "denied")
    raise ValidationError(_("Invalid TOTP token."))


def reauthenticate(user, password: str, token: str, *, request) -> None:
    """Password + OTP verification for sensitive actions; sets recent_reauth_at."""
    account = getattr(user, "email", "") or ""
    ip = client_ip(request)
    if not user.check_password(password):
        record_auth_failure(account, ip, kind="reauth")
        _audit_mfa(user, "security.reauth", None, "denied", {"reason": "password"})
        raise ValidationError(_("Invalid credentials."))
    verify_totp_for_session(user, token, request=request)
    mark_recent_reauth(request)
    _audit_mfa(user, "security.reauth", None, "accepted")


def revoke_totp_device(user, device_id: int, *, actor=None) -> None:
    device = TOTPDevice.objects.filter(user=user, pk=device_id).first()
    if device is None:
        raise ValidationError(_("Device not found."))
    device_pk = device.pk
    device.delete()
    _audit_mfa(actor or user, "security.mfa.revoke", None, "accepted", {"device_id": device_pk})


def _bind_device_to_session(request, device: TOTPDevice) -> None:
    request.session[DEVICE_ID_SESSION_KEY] = device.persistent_id
    request.session.modified = True


def bind_device_for_tests(request, device: TOTPDevice) -> None:
    """Test helper: mark session OTP-verified for a confirmed device."""
    _bind_device_to_session(request, device)
    mark_recent_reauth(request)


def provisioning_uri(device: TOTPDevice, account_name: str | None = None) -> str:
    if hasattr(device, "config_url"):
        return device.config_url
    # Fallback minimal otpauth URI.
    label = account_name or getattr(device.user, "email", "user")
    secret = device.bin_key.hex() if hasattr(device, "bin_key") else device.key
    return f"otpauth://totp/LamTo:{label}?secret={secret}&issuer=LamTo"


def _audit_mfa(user, action, device, result, extra=None):
    membership = None
    if user is not None and getattr(user, "is_authenticated", False):
        membership = user.managementmembership_set.filter(active=True).first()
    try:
        record_audit(
            user,
            membership,
            action,
            "TOTPDevice",
            str(getattr(device, "pk", "") or (extra or {}).get("device_id", "")),
            result,
            extra or {},
        )
    except Exception:
        pass


def device_fingerprint(device: TOTPDevice) -> str:
    raw = f"{device.pk}:{device.key}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
