"""MFA enrollment/verification, re-authentication, login, and logout views."""

from __future__ import annotations

import io

import qrcode
import qrcode.image.svg
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from django.utils.translation import gettext as _

from lamto.accounts.mfa import (
    begin_totp_enrollment,
    confirm_totp_enrollment,
    confirmed_totp_devices,
    pending_totp_device,
    provisioning_uri,
    reauthenticate,
    revoke_totp_device,
    verify_totp_for_session,
)
from lamto.accounts.models import ManagementMembership
from lamto.accounts.security import (
    REAUTH_STASH_KEY,
    assert_not_throttled,
    client_ip,
    record_auth_failure,
    reset_auth_throttle,
    revoke_session,
    rotate_session,
    user_has_confirmed_totp,
    user_is_otp_verified,
)
from lamto.audit.services import record_audit


def _otpauth_qr_svg(uri: str) -> str:
    """Render the otpauth:// provisioning URI as an inline SVG QR code."""
    image = qrcode.make(
        uri,
        image_factory=qrcode.image.svg.SvgPathImage,
        box_size=10,
        border=2,
    )
    buffer = io.BytesIO()
    image.save(buffer)
    return buffer.getvalue().decode("utf-8")


class PhoneOrEmailAuthenticationForm(AuthenticationForm):
    """Login form labeled for email (staff) or phone (residents)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = _("Email or phone")
        self.fields["username"].widget.attrs.setdefault(
            "autocomplete", "username"
        )


class SecureLoginView(LoginView):
    template_name = "web/login.html"
    authentication_form = PhoneOrEmailAuthenticationForm

    def form_valid(self, form):
        username = form.cleaned_data.get("username") or form.cleaned_data.get("email") or ""
        ip = client_ip(self.request)
        try:
            assert_not_throttled(username, ip)
        except PermissionDenied:
            form.add_error(None, _("Too many authentication attempts. Try again later."))
            return self.form_invalid(form)

        user = form.get_user()
        login(self.request, user)
        rotate_session(self.request)
        reset_auth_throttle(username, ip)

        if user_has_confirmed_totp(user):
            self.request.session["mfa_pending_user_id"] = user.pk
            return redirect("web:mfa-verify")
        if ManagementMembership.objects.filter(user=user, active=True).exists():
            return redirect("web:mfa-setup")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        username = self.request.POST.get("username") or self.request.POST.get("email") or ""
        ip = client_ip(self.request)
        record_auth_failure(username, ip, kind="login")
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.filter(email__iexact=username.strip()).first() if username else None
        if user is not None:
            membership = user.managementmembership_set.filter(active=True).first()
            if membership is not None:
                try:
                    record_audit(
                        user,
                        membership,
                        "security.login.suspicious",
                        "User",
                        str(user.pk),
                        "denied",
                        {"reason": "bad_password"},
                    )
                except Exception:
                    pass
        return super().form_invalid(form)


@login_required
@require_http_methods(["GET", "POST"])
def mfa_setup(request):
    if confirmed_totp_devices(request.user).exists() and user_is_otp_verified(request):
        messages.info(request, _("MFA is already configured."))
        return redirect("web:staff-home")

    device = pending_totp_device(request.user)
    if request.method == "GET" and device is None:
        device = begin_totp_enrollment(request.user)

    if request.method == "POST":
        action = request.POST.get("action") or "confirm"
        if action == "restart":
            device = begin_totp_enrollment(request.user)
        else:
            token = request.POST.get("token", "")
            try:
                confirm_totp_enrollment(request.user, token, request=request)
            except ValidationError as error:
                messages.error(request, _("; ").join(error.messages) if hasattr(error, "messages") else str(error))
            else:
                messages.success(request, _("Authenticator enrolled."))
                next_url = request.POST.get("next") or request.GET.get("next") or reverse("web:staff-home")
                return redirect(next_url)
        device = pending_totp_device(request.user) or device

    config_url = provisioning_uri(device, request.user.email) if device else ""
    return render(
        request,
        "web/security/mfa_setup.html",
        {
            "device": device,
            "config_url": config_url,
            "qr_svg": mark_safe(_otpauth_qr_svg(config_url)) if config_url else "",
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def mfa_verify(request):
    if user_is_otp_verified(request):
        return redirect(request.GET.get("next") or reverse("web:staff-home"))
    if not confirmed_totp_devices(request.user).exists():
        return redirect("web:mfa-setup")

    if request.method == "POST":
        token = request.POST.get("token", "")
        try:
            assert_not_throttled(request.user.email, client_ip(request))
            verify_totp_for_session(request.user, token, request=request)
        except PermissionDenied as error:
            messages.error(request, str(error))
        except ValidationError as error:
            messages.error(request, _("; ").join(error.messages) if hasattr(error, "messages") else str(error))
        else:
            messages.success(request, _("MFA verified."))
            next_url = request.POST.get("next") or request.GET.get("next") or reverse("web:staff-home")
            return redirect(next_url)

    return render(request, "web/security/mfa_setup.html", {"verify_only": True})


@login_required
@require_http_methods(["GET", "POST"])
def reauth(request):
    next_url = request.GET.get("next") or request.POST.get("next") or reverse("web:staff-home")
    if request.method == "POST":
        password = request.POST.get("password", "")
        token = request.POST.get("token", "")
        try:
            assert_not_throttled(request.user.email, client_ip(request))
            reauthenticate(request.user, password, token, request=request)
        except PermissionDenied as error:
            messages.error(request, str(error))
        except ValidationError as error:
            messages.error(request, _("; ").join(error.messages) if hasattr(error, "messages") else str(error))
        else:
            messages.success(request, _("Re-authentication successful."))
            return redirect(next_url)
    return render(
        request,
        "web/security/reauth.html",
        {"next": next_url, "stash_pending": bool(request.session.get(REAUTH_STASH_KEY))},
    )


@login_required
@require_POST
def mfa_revoke_device(request, device_id: int):
    try:
        revoke_totp_device(request.user, device_id, actor=request.user)
    except ValidationError as error:
        messages.error(request, str(error))
    else:
        messages.success(request, _("Authenticator device revoked."))
        revoke_session(request)
        return redirect("login")
    return redirect("web:mfa-setup")


@require_POST
def secure_logout(request):
    if request.user.is_authenticated:
        membership = request.user.managementmembership_set.filter(active=True).first()
        if membership is not None:
            try:
                record_audit(
                    request.user,
                    membership,
                    "security.logout",
                    "Session",
                    str(request.user.pk),
                    "accepted",
                    {},
                )
            except Exception:
                pass
    logout(request)
    revoke_session(request)
    # After the flush, so the confirmation rides the fresh anonymous session.
    messages.success(request, _("Signed out. This computer no longer holds your session."))
    return redirect("login")
