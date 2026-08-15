"""Resident API auth lifecycle (spec 3.2)."""

import json
from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from knox.models import AuthToken

from lamto.accounts.models import AuthThrottleBucket, Building, ResidentOccupancy, Unit
from lamto.api.services import (
    canonicalize_login_identifier,
    deactivate_occupancies,
    deactivate_occupancy,
    deactivate_user,
    revoke_tokens_if_no_active_occupancy,
)

PASSWORD = "resident-pass-123"


def problem(response):
    """Parse a problem+json body (Client.json() rejects the media type)."""
    return json.loads(response.content)


class ApiAuthTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.resident = User.objects.create_user(
            email="api-resident@example.com",
            password=PASSWORD,
            display_name="API Resident",
            phone="0912345678",
        )
        building = Building.objects.create(name="API Auth Building")
        cls.unit = Unit.objects.create(building=building, label="A-101")
        cls.occupancy = ResidentOccupancy.objects.create(
            user=cls.resident, unit=cls.unit, active=True
        )
        cls.staff = User.objects.create_user(
            email="api-staff@example.com",
            password=PASSWORD,
            display_name="API Staff",
        )

    def _login(self, identifier, password=PASSWORD):
        return self.client.post(
            reverse("api:auth-login"),
            {"identifier": identifier, "password": password},
            content_type="application/json",
        )

    def _token(self, user=None):
        _instance, token = AuthToken.objects.create(user=user or self.resident)
        return token

    def test_login_with_email_returns_token_and_30_day_expiry(self):
        response = self._login("api-resident@example.com")
        assert response.status_code == 200, response.content
        body = response.json()
        assert body["token"]
        expiry = datetime.fromisoformat(body["expiry"])
        remaining = expiry - timezone.now()
        assert 29 <= remaining.days <= 30
        assert AuthToken.objects.filter(user=self.resident).count() == 1

    def test_login_with_phone_in_any_accepted_form(self):
        for identifier in ("0912345678", "+84 912 345 678"):
            with self.subTest(identifier=identifier):
                response = self._login(identifier)
                assert response.status_code == 200, response.content

    def test_login_wrong_password_is_401_problem_and_recorded(self):
        with self.assertLogs("lamto.api", level="INFO") as cm:
            response = self._login("api-resident@example.com", password="wrong")
        assert response.status_code == 401
        assert response["Content-Type"].startswith("application/problem+json")
        body = problem(response)
        assert body["code"] == "authentication_failed"
        assert body["detail"] == "Invalid credentials."
        assert AuthThrottleBucket.objects.count() == 1
        assert any("invalid_credentials" in msg for msg in cm.output)

    def test_login_locked_after_max_failures(self):
        for _ in range(5):
            self._login("api-resident@example.com", password="wrong")
        response = self._login("api-resident@example.com")  # correct password
        assert response.status_code == 429
        assert problem(response)["code"] == "throttled"

    def test_login_missing_fields_is_validation_failed(self):
        response = self.client.post(
            reverse("api:auth-login"), {}, content_type="application/json"
        )
        assert response.status_code == 400
        body = problem(response)
        assert body["code"] == "validation_failed"
        assert "identifier" in body["errors"]
        assert "password" in body["errors"]

    def test_login_without_active_occupancy_is_unified_401(self):
        """Staff / no occupancy: same external 401 as wrong password (clarification 2)."""
        with self.assertLogs("lamto.api", level="INFO") as cm:
            response = self._login("api-staff@example.com")
        assert response.status_code == 401
        assert response["Content-Type"].startswith("application/problem+json")
        body = problem(response)
        assert body["code"] == "authentication_failed"
        assert body["detail"] == "Invalid credentials."
        assert not AuthToken.objects.filter(user=self.staff).exists()
        assert any("no_active_occupancy" in msg for msg in cm.output)
        # Same throttle path as invalid credentials (Important #1).
        assert AuthThrottleBucket.objects.count() == 1
        assert AuthThrottleBucket.objects.get().failure_count == 1

    def test_login_ineligible_counts_toward_throttle_lockout(self):
        """Staff / no occupancy failures lock out like wrong-password failures."""
        for _ in range(5):
            response = self._login("api-staff@example.com")
            assert response.status_code == 401
        # Further attempts (even with correct password) are 429.
        response = self._login("api-staff@example.com")
        assert response.status_code == 429
        assert problem(response)["code"] == "throttled"
        assert AuthThrottleBucket.objects.get().failure_count >= 5

    def test_login_without_active_occupancy_revokes_leftover_tokens(self):
        """Bulk occupancy deactivation can leave tokens; login cleans them up."""
        self._token(user=self.resident)
        ResidentOccupancy.objects.filter(pk=self.occupancy.pk).update(active=False)
        assert AuthToken.objects.filter(user=self.resident).count() == 1
        response = self._login("api-resident@example.com")
        assert response.status_code == 401
        assert AuthToken.objects.filter(user=self.resident).count() == 0

    def test_inactive_user_cannot_login(self):
        self.resident.is_active = False
        self.resident.save()
        response = self._login("api-resident@example.com")
        assert response.status_code == 401

    def test_token_cap_evicts_oldest(self):
        for _ in range(5):
            assert self._login("api-resident@example.com").status_code == 200
        first_pk = (
            AuthToken.objects.filter(user=self.resident).order_by("created").first().pk
        )
        assert self._login("api-resident@example.com").status_code == 200
        remaining = AuthToken.objects.filter(user=self.resident)
        assert remaining.count() == 5
        assert not remaining.filter(pk=first_pk).exists()

    def test_logout_deletes_only_the_calling_token(self):
        token = self._login("api-resident@example.com").json()["token"]
        other = self._login("api-resident@example.com").json()["token"]
        response = self.client.post(
            reverse("api:auth-logout"),
            headers={"authorization": f"Token {token}"},
        )
        assert response.status_code == 204
        assert AuthToken.objects.filter(user=self.resident).count() == 1
        # The deleted token no longer authenticates.
        again = self.client.post(
            reverse("api:auth-logout"),
            headers={"authorization": f"Token {token}"},
        )
        assert again.status_code == 401
        assert problem(again)["code"] == "authentication_failed"
        # The surviving token still works.
        assert (
            self.client.post(
                reverse("api:auth-logout-all"),
                headers={"authorization": f"Token {other}"},
            ).status_code
            == 204
        )

    def test_logout_all_deletes_every_token(self):
        token = self._login("api-resident@example.com").json()["token"]
        self._login("api-resident@example.com")
        response = self.client.post(
            reverse("api:auth-logout-all"),
            headers={"authorization": f"Token {token}"},
        )
        assert response.status_code == 204
        assert AuthToken.objects.filter(user=self.resident).count() == 0

    def test_deactivating_user_deletes_tokens(self):
        self._token()
        self._token()
        self.resident.is_active = False
        self.resident.save()
        assert AuthToken.objects.filter(user=self.resident).count() == 0

    def test_deactivating_last_occupancy_deletes_tokens(self):
        self._token()
        self.occupancy.active = False
        self.occupancy.save()
        assert AuthToken.objects.filter(user=self.resident).count() == 0

    def test_deactivating_one_of_two_occupancies_keeps_tokens(self):
        second = ResidentOccupancy.objects.create(
            user=self.resident, unit=self.unit, active=True
        )
        self._token()
        second.active = False
        second.save()
        assert AuthToken.objects.filter(user=self.resident).count() == 1

    def test_token_of_inactive_user_is_rejected_regardless(self):
        token = self._token()
        # Bypass the signal deliberately (bulk update): auth must still reject.
        get_user_model().objects.filter(pk=self.resident.pk).update(is_active=False)
        response = self.client.post(
            reverse("api:auth-logout"),
            headers={"authorization": f"Token {token}"},
        )
        assert response.status_code == 401

    # --- Clarification 1: throttle keys are canonicalized ---

    def test_canonicalize_login_identifier_phone_and_email(self):
        assert canonicalize_login_identifier("0912345678") == "0912345678"
        assert canonicalize_login_identifier("+84 912 345 678") == "0912345678"
        assert (
            canonicalize_login_identifier("API-Resident@Example.com")
            == "api-resident@example.com"
        )

    def test_login_throttle_uses_canonical_identifier(self):
        """Alternate phone forms and mixed-case email each share one bucket."""
        self._login("0912345678", password="wrong")
        self._login("+84 912 345 678", password="wrong")
        assert AuthThrottleBucket.objects.count() == 1
        assert AuthThrottleBucket.objects.get().failure_count == 2

        AuthThrottleBucket.objects.all().delete()
        self._login("API-Resident@Example.com", password="wrong")
        self._login("api-resident@example.com", password="wrong")
        assert AuthThrottleBucket.objects.count() == 1
        assert AuthThrottleBucket.objects.get().failure_count == 2

    # --- Clarification 5: service path + signal-bypass defensive cleanup ---

    def test_deactivate_occupancy_service_revokes_tokens(self):
        self._token()
        deactivate_occupancy(self.occupancy, reason="test")
        self.occupancy.refresh_from_db()
        assert not self.occupancy.active
        assert AuthToken.objects.filter(user=self.resident).count() == 0

    def test_deactivate_user_service_revokes_tokens(self):
        self._token()
        deactivate_user(self.resident, reason="test")
        self.resident.refresh_from_db()
        assert not self.resident.is_active
        assert AuthToken.objects.filter(user=self.resident).count() == 0

    def test_bulk_update_then_defensive_cleanup_revokes_tokens(self):
        """QuerySet.update() bypasses post_save; defensive cleanup still revokes."""
        self._token()
        ResidentOccupancy.objects.filter(pk=self.occupancy.pk).update(active=False)
        # Tokens remain because signals did not fire.
        assert AuthToken.objects.filter(user=self.resident).count() == 1
        deleted = revoke_tokens_if_no_active_occupancy(self.resident)
        assert deleted >= 1
        assert AuthToken.objects.filter(user=self.resident).count() == 0

    def test_deactivate_occupancies_bulk_service_revokes_without_relogin(self):
        """Preferred bulk path: tokens gone immediately, no login required."""
        self._token()
        self._token()
        updated = deactivate_occupancies(
            ResidentOccupancy.objects.filter(user=self.resident),
            reason="test-bulk",
        )
        assert updated == 1
        self.occupancy.refresh_from_db()
        assert not self.occupancy.active
        assert AuthToken.objects.filter(user=self.resident).count() == 0

    def test_authenticated_request_revokes_residual_tokens_after_signal_bypass(self):
        """Bulk occupancy update leaves a knox token; first API use cleans it.

        Cleanup happens at authentication time — not only on the next login.
        """
        token = self._token()
        ResidentOccupancy.objects.filter(pk=self.occupancy.pk).update(active=False)
        assert AuthToken.objects.filter(user=self.resident).count() == 1
        response = self.client.post(
            reverse("api:auth-logout"),
            headers={"authorization": f"Token {token}"},
        )
        assert response.status_code == 401
        assert problem(response)["code"] == "authentication_failed"
        assert AuthToken.objects.filter(user=self.resident).count() == 0

    def test_bulk_user_deactivation_service_revokes_tokens(self):
        self._token()
        get_user_model().objects.filter(pk=self.resident.pk).update(is_active=False)
        assert AuthToken.objects.filter(user=self.resident).count() == 1
        # Service path always revokes even if already inactive in DB.
        deactivate_user(self.resident, reason="bulk-cleanup")
        assert AuthToken.objects.filter(user=self.resident).count() == 0
