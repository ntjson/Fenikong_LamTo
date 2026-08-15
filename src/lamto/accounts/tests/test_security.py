"""Login throttle, session security, and retired MFA surface tests.

The MFA and re-authentication security model is permanently removed
(ADR 0001): enrollment, verification, device revocation, and re-authentication
paths return 404, while password-only Management access stays functional.
"""

from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from lamto.accounts.models import (
    AuthThrottleBucket,
    Building,
    ManagementMembership,
)
from lamto.accounts.security import (
    THROTTLE_MAX_FAILURES,
    THROTTLE_WINDOW_SECONDS,
    assert_not_throttled,
    record_auth_failure,
    reset_auth_throttle,
    throttle_digest,
)

FORMER_SECURITY_PATHS = [
    "/s/security/mfa/setup/",
    "/s/security/mfa/verify/",
    "/s/security/mfa/revoke/1/",
    "/s/security/mfa/revoke/999999/",
    "/s/security/reauth/",
]


class SecurityTests(TestCase):
    def setUp(self):
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

    def test_management_can_export_document_history(self):
        operator, auditor = self.make_operator_and_auditor()
        self.client.force_login(operator.user)
        self.assertEqual(self.client.get(reverse("web:audit-export")).status_code, 200)

        self.client.force_login(auditor.user)
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

    def test_password_only_session_reaches_management_workspace(self):
        board = self.make_manager()
        self.client.force_login(board.user)
        response = self.client.get(reverse("web:action-inbox"))
        self.assertEqual(response.status_code, 200)

    def test_former_mfa_urls_return_404_for_anonymous_and_manager(self):
        """Retired MFA/re-authentication surfaces are gone: a normal 404 with
        no compatibility redirect, for visitors and Management accounts alike."""
        board = self.make_manager()
        self.client.force_login(board.user)
        clients = (self.client, Client())
        for client in clients:
            for path in FORMER_SECURITY_PATHS:
                with self.subTest(path=path, authenticated=client is self.client):
                    response = client.get(path)
                    self.assertEqual(
                        response.status_code,
                        404,
                        msg=f"{path} must 404, got {response.status_code}",
                    )
                    self.assertEqual(
                        response.get("Location", ""),
                        "",
                        msg=f"{path} must not redirect",
                    )
                    self.assertTemplateNotUsed(response, "web/security/mfa_setup.html")
                    self.assertTemplateNotUsed(response, "web/security/reauth.html")

    def test_former_mfa_urls_404_on_post_and_unknown_device_id(self):
        board = self.make_manager()
        self.client.force_login(board.user)
        response = self.client.post("/s/security/mfa/setup/", {"token": "123456"})
        self.assertEqual(response.status_code, 404)
        response = self.client.post("/s/security/mfa/revoke/1/")
        self.assertEqual(response.status_code, 404)
        # Non-integer device ids are not a route at all.
        response = self.client.get("/s/security/mfa/revoke/not-an-id/")
        self.assertEqual(response.status_code, 404)

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

    def test_sensitive_financial_post_proceeds_without_reauth(self):
        """A password-only session posts sensitive work straight to its normal
        domain result (404 for a missing settlement): no MFA denial and no
        redirect to the removed re-authentication surface."""
        board = self.make_manager()
        self.client.force_login(board.user)

        response = self.client.post(
            reverse("web:settlement-record-transfer", kwargs={"pk": 999999}),
            {
                "bank_reference": "REF-1",
                "amount_vnd": "1000",
                "external_status": "COMPLETED",
                "proof": "1",
                "event_id": "0x" + "11" * 32,
                "signature": "0x" + "22" * 65,
                "settlement_id": "1",
            },
        )
        self.assertEqual(response.status_code, 404)
        self.assertNotIn("/s/security/reauth/", response.get("Location", ""))
