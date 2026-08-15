"""HTTP journey: password-only persistent Management sessions (ADR 0001).

Proves the externally observable contract of ticket 01:
- password login reaches the Management workspace with no authenticator detour
- the Management session rides a persistent 400-day cookie
- every authenticated /s/ request renews server-side expiry and the cookie
- still-valid pre-change sessions are accepted and adopt the rolling lifetime
- the renewed cookie remains usable by Django admin
- Logout stays a CSRF-protected POST that flushes the session and re-locks /s/
- throttling, suspicious-login auditing, session rotation, password-change and
  account-disablement invalidation remain effective
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from lamto.accounts.models import AuthThrottleBucket, Building, ManagementMembership
from lamto.accounts.security import THROTTLE_MAX_FAILURES, throttle_digest
from lamto.audit.models import AuditEvent

MANAGEMENT_MAX_AGE_SECONDS = 400 * 24 * 60 * 60


class PasswordOnlyManagementSessionTests(TestCase):
    def setUp(self):
        self.building = Building.objects.create(name="Session Tower")
        self.password = "secret-pass-123"

    def make_manager(self, *, email="manager@example.test", is_staff=False):
        user = get_user_model().objects.create_user(
            email=email, password=self.password, display_name="Manager"
        )
        if is_staff:
            user.is_staff = True
            user.save(update_fields=["is_staff"])
        membership = ManagementMembership.objects.create(
            user=user, building=self.building
        )
        return user, membership

    def login(self, *, user=None, extra=None):
        user = user or self.make_manager()[0]
        data = {"username": user.email, "password": self.password, **(extra or {})}
        return self.client.post(reverse("login"), data)

    # --- Login reaches the workspace, password only -------------------------

    def test_password_login_reaches_workspace_without_authenticator_detour(self):
        user, _ = self.make_manager()
        response = self.login(user=user)

        self.assertRedirects(
            response, reverse("web:staff-home"), fetch_redirect_response=False
        )
        self.assertNotIn(
            "/s/security/mfa/", response["Location"], "no authenticator detour"
        )
        self.assertEqual(self.client.get(reverse("web:action-inbox")).status_code, 200)

    def test_password_login_honors_requested_next_destination(self):
        user, _ = self.make_manager()
        response = self.login(user=user, extra={"next": reverse("web:case-list")})

        self.assertRedirects(response, reverse("web:case-list"))
        self.assertEqual(self.client.get(reverse("web:case-list")).status_code, 200)

    def test_non_management_login_keeps_configured_destination(self):
        resident = get_user_model().objects.create_user(
            email="resident@example.test",
            password=self.password,
            display_name="Resident",
        )
        response = self.login(user=resident)

        self.assertRedirects(response, "/", fetch_redirect_response=False)

    def test_login_rotates_session_key_without_losing_data(self):
        user, _ = self.make_manager()
        session = self.client.session
        pre = session.session_key
        session["kept"] = "value"
        session.save()

        self.login(user=user)

        self.assertNotEqual(self.client.session.session_key, pre)
        self.assertEqual(self.client.session.get("kept"), "value")

    def test_workspace_pages_accept_password_only_session(self):
        user, _ = self.make_manager()
        self.login(user=user)
        for name in (
            "action-inbox",
            "case-list",
            "proposal-list",
            "settlement-list",
            "fund-home",
            "gate-queue",
            "ops-health",
            "audit-export",
        ):
            with self.subTest(name=name):
                self.assertEqual(
                    self.client.get(reverse(f"web:{name}")).status_code, 200
                )

    # --- Persistent rolling 400-day lifetime ---------------------------------

    def test_login_sets_persistent_400_day_session_cookie(self):
        user, _ = self.make_manager()
        response = self.login(user=user)

        cookie = response.cookies["sessionid"]
        self.assertIn("max-age", cookie, "persistent cookie, not browser-close")
        self.assertAlmostEqual(
            int(cookie["max-age"]), MANAGEMENT_MAX_AGE_SECONDS, delta=60
        )
        expiry = self.client.session.get_expiry_date()
        self.assertGreater(
            expiry, timezone.now() + timedelta(days=399), "server-side expiry"
        )

    def test_authenticated_workspace_request_renews_expiry_and_cookie(self):
        user, _ = self.make_manager()
        self.login(user=user)
        session = self.client.session
        session.set_expiry(timedelta(days=1))
        session.save()
        before = Session.objects.get(session_key=session.session_key).expire_date

        response = self.client.get(reverse("web:action-inbox"))

        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(
            int(response.cookies["sessionid"]["max-age"]),
            MANAGEMENT_MAX_AGE_SECONDS,
            delta=60,
        )
        row = Session.objects.get(session_key=self.client.session.session_key)
        self.assertGreater(row.expire_date, timezone.now() + timedelta(days=399))
        self.assertGreater(row.expire_date, before)

    def test_still_valid_pre_change_session_is_adopted_and_renewed(self):
        user, _ = self.make_manager()
        self.client.force_login(user)
        self.assertAlmostEqual(
            self.client.session.get_expiry_age(), 1209600, delta=60, msg="old default"
        )

        response = self.client.get(reverse("web:action-inbox"))

        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(
            int(response.cookies["sessionid"]["max-age"]),
            MANAGEMENT_MAX_AGE_SECONDS,
            delta=60,
        )

    # --- Shared Django admin cookie ------------------------------------------

    def test_renewed_management_session_remains_usable_in_django_admin(self):
        user, _ = self.make_manager(is_staff=True)
        self.login(user=user)
        self.assertEqual(self.client.get(reverse("web:action-inbox")).status_code, 200)

        response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 200)

    # --- Logout ---------------------------------------------------------------

    def test_logout_is_csrf_protected_post_that_flushes_and_relocks(self):
        user, _ = self.make_manager()
        csrf = Client(enforce_csrf_checks=True)
        login_page = csrf.get(reverse("login"))
        token = login_page.cookies["csrftoken"].value
        csrf.post(
            reverse("login"),
            {
                "username": user.email,
                "password": self.password,
                "csrfmiddlewaretoken": token,
            },
        )
        self.assertEqual(csrf.get(reverse("web:action-inbox")).status_code, 200)

        tokenless = csrf.post(reverse("logout"))
        self.assertEqual(tokenless.status_code, 403, "logout stays CSRF-protected")
        self.assertEqual(csrf.get(reverse("web:action-inbox")).status_code, 200)

        token = csrf.cookies["csrftoken"].value
        response = csrf.post(reverse("logout"), {"csrfmiddlewaretoken": token})
        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", csrf.session, "authenticated session flushed")

        relock = csrf.get(reverse("web:action-inbox"))
        self.assertEqual(relock.status_code, 302)
        self.assertIn(reverse("login"), relock["Location"])

    def test_logout_records_best_effort_audit_event(self):
        user, _ = self.make_manager()
        self.login(user=user)
        self.client.post(reverse("logout"))

        self.assertTrue(
            AuditEvent.objects.filter(
                action="security.logout", actor=user, result="accepted"
            ).exists()
        )

    # --- Safeguards remain effective -----------------------------------------

    def test_password_throttle_still_blocks_a_valid_credential(self):
        user, _ = self.make_manager()
        for _ in range(THROTTLE_MAX_FAILURES):
            self.client.post(
                reverse("login"),
                {"username": user.email, "password": "wrong-password"},
            )
        bucket = AuthThrottleBucket.objects.get(
            key_digest=throttle_digest(user.email, "127.0.0.1")
        )
        self.assertIsNotNone(bucket.locked_until)

        response = self.login(user=user)

        self.assertEqual(response.status_code, 200, "throttled login re-renders")
        self.assertTrue(response.context["form"].non_field_errors())

    def test_failed_management_login_records_suspicious_audit(self):
        user, _ = self.make_manager()
        self.client.post(
            reverse("login"), {"username": user.email, "password": "wrong-password"}
        )

        self.assertTrue(
            AuditEvent.objects.filter(
                action="security.login.suspicious", actor=user, result="denied"
            ).exists()
        )

    def test_password_change_invalidates_existing_session(self):
        user, _ = self.make_manager()
        self.login(user=user)
        self.assertEqual(self.client.get(reverse("web:action-inbox")).status_code, 200)

        user.set_password("rotated-password")
        user.save()

        response = self.client.get(reverse("web:action-inbox"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_account_disablement_invalidates_existing_session(self):
        user, _ = self.make_manager()
        self.login(user=user)
        self.assertEqual(self.client.get(reverse("web:action-inbox")).status_code, 200)

        user.is_active = False
        user.save(update_fields=["is_active"])

        response = self.client.get(reverse("web:action-inbox"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])
