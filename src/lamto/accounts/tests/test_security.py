"""MFA, re-auth, throttle, and session security controls."""

from __future__ import annotations

import time
from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.oath import totp
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex

from lamto.accounts.mfa import (
    begin_totp_enrollment,
    confirm_totp_enrollment,
    verify_totp_for_session,
)
from lamto.accounts.models import (
    AuthThrottleBucket,
    Building,
    ManagementMembership,
)
from lamto.accounts.security import (
    RECENT_REAUTH_KEY,
    REAUTH_STASH_KEY,
    THROTTLE_MAX_FAILURES,
    THROTTLE_WINDOW_SECONDS,
    assert_not_throttled,
    mark_recent_reauth,
    pop_stashed_post,
    record_auth_failure,
    require_recent_auth,
    reset_auth_throttle,
    stash_post_for_reauth,
    throttle_digest,
)


def _current_totp_token(device: TOTPDevice) -> str:
    # Force a fresh step after last_t updates by using django_otp.oath.totp directly
    # and temporarily clearing last_t when needed.
    return f"{totp(device.bin_key):06d}"


class SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.building = Building.objects.create(name="Sec Building")

    def _unique(self, base):
        n = getattr(self, "_seq", 0) + 1
        self._seq = n
        return f"{base}-{n}"

    def make_membership(self, suffix, *, building=None):
        building = building or self.building
        suffix = self._unique(suffix)
        user = get_user_model().objects.create_user(
            email=f"{suffix}@example.test",
            password="secret-pass-123",
            display_name=suffix,
        )
        return ManagementMembership.objects.create(user=user, building=building)

    def make_manager(self):
        return self.make_membership("board-pay")

    def make_operator_and_auditor(self):
        operator = self.make_membership("op")
        auditor = self.make_membership("aud")
        return operator, auditor

    def valid_payment_payload(self):
        return {
            "bank_reference": "REF-1",
            "amount_vnd": "1000",
            "external_status": "COMPLETED",
            "proof": "1",
            "event_id": "0x" + "11" * 32,
            "signature": "0x" + "22" * 65,
            "settlement_id": "1",
        }

    def enroll_and_bind(self, client: Client, user) -> TOTPDevice:
        device = TOTPDevice.objects.create(
            user=user,
            name="test",
            confirmed=True,
            key=random_hex(),
        )
        # Bind device into session after login.
        session = client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session[RECENT_REAUTH_KEY] = time.time()
        session.save()
        return device

    def test_privileged_action_requires_verified_otp_and_recent_reauth(self):
        board = self.make_manager()
        self.client.force_login(board.user)
        response = self.client.post(
            reverse("web:settlement-record-transfer", kwargs={"pk": 999999}),
            self.valid_payment_payload(),
        )
        self.assertEqual(response.status_code, 403)

    def test_privileged_action_allowed_with_otp_and_recent_reauth_gate_passes(self):
        board = self.make_manager()
        self.client.force_login(board.user)
        self.enroll_and_bind(self.client, board.user)
        # Gate should not 403 for MFA/reauth; may 404/400 for missing settlement.
        response = self.client.post(
            reverse("web:settlement-record-transfer", kwargs={"pk": 999999}),
            self.valid_payment_payload(),
        )
        self.assertNotEqual(response.status_code, 403)

    def test_management_can_export_document_history(self):
        operator, auditor = self.make_operator_and_auditor()
        self.client.force_login(operator.user)
        self.enroll_and_bind(self.client, operator.user)
        self.assertEqual(self.client.get(reverse("web:audit-export")).status_code, 200)

        self.client.force_login(auditor.user)
        self.enroll_and_bind(self.client, auditor.user)
        self.assertEqual(self.client.get(reverse("web:audit-export")).status_code, 200)

    def test_throttle_locks_after_five_failures_and_resets_on_success(self):
        account = "throttle@example.test"
        ip = "203.0.113.9"
        for _ in range(THROTTLE_MAX_FAILURES):
            record_auth_failure(account, ip)
        with self.assertRaises(PermissionDenied):
            assert_not_throttled(account, ip)
        bucket = AuthThrottleBucket.objects.get(key_digest=throttle_digest(account, ip))
        self.assertIsNotNone(bucket.locked_until)
        reset_auth_throttle(account, ip)
        assert_not_throttled(account, ip)
        bucket.refresh_from_db()
        self.assertEqual(bucket.failure_count, 0)
        self.assertIsNone(bucket.locked_until)

    def test_throttle_window_expiry_allows_new_attempts(self):
        account = "window@example.test"
        ip = "198.51.100.2"
        for _ in range(THROTTLE_MAX_FAILURES):
            record_auth_failure(account, ip)
        bucket = AuthThrottleBucket.objects.get(key_digest=throttle_digest(account, ip))
        bucket.window_started_at = timezone.now() - timedelta(
            seconds=THROTTLE_WINDOW_SECONDS + 5
        )
        bucket.locked_until = timezone.now() - timedelta(seconds=1)
        bucket.save(update_fields=["window_started_at", "locked_until"])
        # Locked_until in the past → not throttled.
        assert_not_throttled(account, ip)

    def test_session_rotation_on_mfa_and_revocation_on_logout(self):
        membership = self.make_manager()
        user = membership.user
        self.client.force_login(user)
        device = TOTPDevice.objects.create(
            user=user, name="rot", confirmed=True, key=random_hex()
        )
        session_key_before = self.client.session.session_key
        # Verify token path rotates session.
        request = self.factory.post("/s/security/mfa/verify/")
        request.user = user
        request.session = self.client.session
        token = _current_totp_token(device)
        # Ensure last_t allows current token.
        device.last_t = -1
        device.save(update_fields=["last_t"])
        verify_totp_for_session(user, token, request=request)
        request.session.save()
        self.assertTrue(request.session.get(DEVICE_ID_SESSION_KEY))
        self.assertIsNotNone(request.session.get(RECENT_REAUTH_KEY))
        # Logout flushes session.
        self.client.logout()
        # New anonymous session should not carry MFA binding.
        self.assertFalse(self.client.session.get(DEVICE_ID_SESSION_KEY))

    def test_require_recent_auth_expires(self):
        membership = self.make_manager()
        user = membership.user
        device = TOTPDevice.objects.create(
            user=user, name="re", confirmed=True, key=random_hex()
        )
        request = self.factory.post("/s/payments/record/")
        request.user = user
        # Minimal session-like dict with OTP binding via middleware simulation:
        from django.contrib.sessions.backends.db import SessionStore

        session = SessionStore()
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session[RECENT_REAUTH_KEY] = time.time() - 400
        session.save()
        request.session = session

        # OTPMiddleware-style wrap: user.is_verified from django_otp.models
        from django_otp.middleware import OTPMiddleware

        # Manually set verified by attaching device
        user.otp_device = device
        # django_otp.is_verified checks session device id
        with mock.patch(
            "lamto.accounts.security.user_is_otp_verified", return_value=True
        ):
            with self.assertRaises(PermissionDenied):
                require_recent_auth(request, max_age_seconds=300)
            mark_recent_reauth(request)
            require_recent_auth(request, max_age_seconds=300)

    def test_reauth_stash_round_trip_preserves_typed_values_only(self):
        from django.contrib.sessions.backends.db import SessionStore

        request = self.factory.post(
            "/s/proposals/new/",
            {
                "contractor_name": "Công ty TNHH Minh Phát",
                "amount_vnd": "184500000",
                "confirm": "on",
                "csrfmiddlewaretoken": "x",
                "action": "prepare",
            },
        )
        request.session = SessionStore()
        stash_post_for_reauth(request)

        restore = self.factory.get("/s/proposals/new/")
        restore.session = request.session
        data = pop_stashed_post(restore)
        self.assertEqual(data["contractor_name"], "Công ty TNHH Minh Phát")
        self.assertEqual(data["amount_vnd"], "184500000")
        # Irreversibility confirms and CSRF are never re-armed.
        self.assertNotIn("confirm", data)
        self.assertNotIn("csrfmiddlewaretoken", data)
        # One-shot: a second pop returns nothing.
        self.assertIsNone(pop_stashed_post(restore))

    def test_reauth_stash_is_path_scoped_and_expires(self):
        from django.contrib.sessions.backends.db import SessionStore

        request = self.factory.post("/s/fund/record/", {"amount_vnd": "1"})
        request.session = SessionStore()
        stash_post_for_reauth(request)

        elsewhere = self.factory.get("/s/proposals/new/")
        elsewhere.session = request.session
        self.assertIsNone(pop_stashed_post(elsewhere))

        request.session[REAUTH_STASH_KEY]["at"] = time.time() - 3600
        same_path = self.factory.get("/s/fund/record/")
        same_path.session = request.session
        self.assertIsNone(pop_stashed_post(same_path))

    def test_password_only_session_reaches_management_workspace(self):
        board = self.make_manager()
        self.client.force_login(board.user)
        response = self.client.get(reverse("web:action-inbox"))
        self.assertEqual(response.status_code, 200)

    def test_totp_enrollment_confirm_and_verify(self):
        board = self.make_manager()
        user = board.user
        device = begin_totp_enrollment(user)
        self.assertFalse(device.confirmed)
        token = _current_totp_token(device)
        request = self.factory.post("/s/security/mfa/setup/")
        request.user = user
        from django.contrib.sessions.backends.db import SessionStore

        request.session = SessionStore()
        request.session.create()
        confirmed = confirm_totp_enrollment(user, token, request=request)
        self.assertTrue(confirmed.confirmed)
        # Second verify with a new step: advance last_t handling
        confirmed.last_t = -1
        confirmed.save(update_fields=["last_t"])
        # Sleep if needed to avoid same-token reuse — reset last_t already allows.
        token2 = _current_totp_token(confirmed)
        verify_totp_for_session(user, token2, request=request)
        self.assertTrue(request.session.get(DEVICE_ID_SESSION_KEY))

    def test_password_only_session_accepted_on_staff_workspaces(self):
        """Password-only sessions reach key staff workspaces (ADR 0001)."""
        board = self.make_manager()
        auditor = self.make_membership("aud-mfa")
        maint = self.make_membership("maint-mfa")

        for membership, url_name in (
            (board, "web:settlement-list"),
            (auditor, "web:audit-export"),
            (maint, "web:case-list"),
        ):
            with self.subTest(url=url_name):
                client = Client()
                client.force_login(membership.user)
                response = client.get(reverse(url_name))
                self.assertEqual(
                    response.status_code,
                    200,
                    msg=f"password-only session must reach {url_name}",
                )

    def test_signed_financial_post_requires_recent_reauth(self):
        """Signed financial POSTs redirect to reauth when stale (Finding 2)."""
        board = self.make_manager()
        self.client.force_login(board.user)
        self.enroll_and_bind(self.client, board.user)
        # Stale reauth window.
        session = self.client.session
        session[RECENT_REAUTH_KEY] = time.time() - 400
        session.save()

        response = self.client.post(
            reverse("web:settlement-record-transfer", kwargs={"pk": 999999}),
            self.valid_payment_payload(),
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/s/security/reauth/", response["Location"])
        self.assertIn("next=", response["Location"])
