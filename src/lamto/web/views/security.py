"""Login and logout views for the Management workspace."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils.translation import gettext as _

from lamto.accounts.models import ManagementMembership
from lamto.accounts.security import (
    assert_not_throttled,
    client_ip,
    record_auth_failure,
    renew_management_session,
    reset_auth_throttle,
    revoke_session,
    rotate_session,
)
from lamto.audit.services import record_audit


class PhoneOrEmailAuthenticationForm(AuthenticationForm):
    """Login form labeled for email (staff) or phone (residents)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = _("Email or phone")
        self.fields["username"].widget.attrs.setdefault("autocomplete", "username")


class SecureLoginView(LoginView):
    template_name = "web/login.html"
    authentication_form = PhoneOrEmailAuthenticationForm

    def get_redirect_url(self):
        """Send an active Management account to the workspace by default.

        Honors a safe ``next`` destination first; without one, a Management
        account lands on the workspace rather than the generic redirect target.
        """
        url = super().get_redirect_url()
        if url:
            return url
        user = getattr(self.request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False):
            if ManagementMembership.objects.filter(user=user, active=True).exists():
                return reverse("web:staff-home")
        return ""

    def form_valid(self, form):
        username = (
            form.cleaned_data.get("username") or form.cleaned_data.get("email") or ""
        )
        ip = client_ip(self.request)
        try:
            assert_not_throttled(username, ip)
        except PermissionDenied:
            form.add_error(
                None, _("Too many authentication attempts. Try again later.")
            )
            return self.form_invalid(form)

        user = form.get_user()
        login(self.request, user)
        rotate_session(self.request)
        reset_auth_throttle(username, ip)

        if ManagementMembership.objects.filter(user=user, active=True).exists():
            renew_management_session(self.request)

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        username = (
            self.request.POST.get("username") or self.request.POST.get("email") or ""
        )
        ip = client_ip(self.request)
        record_auth_failure(username, ip, kind="login")
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = (
            User.objects.filter(email__iexact=username.strip()).first()
            if username
            else None
        )
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
    messages.success(
        request, _("Signed out. This computer no longer holds your session.")
    )
    return redirect("login")
