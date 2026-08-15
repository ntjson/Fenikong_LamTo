"""GET /me — profile, active occupancies, notification prefs (spec 3.3)."""

import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from knox.models import AuthToken

from lamto.accounts.models import Building, ResidentOccupancy, Unit
from lamto.notifications.models import NotificationPreference


class MeViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.resident = User.objects.create_user(
            email=None,
            password="resident-pass-123",
            display_name="Me Resident",
            phone="0987654321",
        )
        building_a = Building.objects.create(name="Building Alpha")
        building_b = Building.objects.create(name="Building Beta")
        cls.occupancy_a = ResidentOccupancy.objects.create(
            user=cls.resident,
            unit=Unit.objects.create(building=building_a, label="A-101"),
            active=True,
        )
        cls.occupancy_b = ResidentOccupancy.objects.create(
            user=cls.resident,
            unit=Unit.objects.create(building=building_b, label="B-202"),
            active=True,
        )
        NotificationPreference.objects.create(
            user=cls.resident, event_code="ledger.published", email_enabled=False
        )

    def _auth(self, user=None):
        _instance, token = AuthToken.objects.create(user=user or self.resident)
        return {"authorization": f"Token {token}"}

    def test_me_returns_profile_occupancies_and_prefs(self):
        response = self.client.get(reverse("api:me"), headers=self._auth())
        assert response.status_code == 200, response.content
        body = response.json()
        assert body["display_name"] == "Me Resident"
        assert body["email"] is None
        assert body["phone"] == "0987654321"
        occupancies = {o["id"]: o for o in body["occupancies"]}
        assert set(occupancies) == {self.occupancy_a.pk, self.occupancy_b.pk}
        assert occupancies[self.occupancy_a.pk]["unit_label"] == "A-101"
        assert occupancies[self.occupancy_a.pk]["building_name"] == "Building Alpha"
        assert body["notification_preferences"] == [
            {
                "event_code": "ledger.published",
                "email_enabled": False,
                "push_enabled": True,
            }
        ]

    def test_me_preferences_include_push_enabled(self):
        from lamto.notifications.services import EVENT_PUBLICATION

        NotificationPreference.objects.create(
            user=self.resident,
            event_code=EVENT_PUBLICATION,
            email_enabled=True,
            push_enabled=False,
        )
        response = self.client.get(reverse("api:me"), headers=self._auth())
        assert response.status_code == 200
        prefs = {p["event_code"]: p for p in response.json()["notification_preferences"]}
        assert prefs[EVENT_PUBLICATION]["push_enabled"] is False

    def test_patch_notification_preferences_and_reflected_on_me(self):
        from lamto.notifications.services import EVENT_PUBLICATION, EVENT_REPORT_RECEIPT

        headers = self._auth()
        resp = self.client.patch(
            reverse("api:me-notification-preferences"),
            data={
                "preferences": [
                    {
                        "event_code": EVENT_PUBLICATION,
                        "email_enabled": False,
                        "push_enabled": False,
                    },
                    {"event_code": EVENT_REPORT_RECEIPT, "push_enabled": False},
                ]
            },
            content_type="application/json",
            headers=headers,
        )
        assert resp.status_code == 200, resp.content
        by_code = {p["event_code"]: p for p in resp.json()}
        assert by_code[EVENT_PUBLICATION]["email_enabled"] is False
        assert by_code[EVENT_PUBLICATION]["push_enabled"] is False
        assert by_code[EVENT_REPORT_RECEIPT]["push_enabled"] is False

        me = self.client.get(reverse("api:me"), headers=headers)
        assert me.status_code == 200
        me_prefs = {p["event_code"]: p for p in me.json()["notification_preferences"]}
        assert me_prefs[EVENT_PUBLICATION]["email_enabled"] is False
        assert me_prefs[EVENT_PUBLICATION]["push_enabled"] is False
        assert me_prefs[EVENT_REPORT_RECEIPT]["push_enabled"] is False

        row = NotificationPreference.objects.get(
            user=self.resident, event_code=EVENT_PUBLICATION
        )
        assert row.email_enabled is False and row.push_enabled is False

    def test_patch_notification_preferences_rejects_unknown_event_code(self):
        resp = self.client.patch(
            reverse("api:me-notification-preferences"),
            data={"preferences": [{"event_code": "not.a.real.event", "email_enabled": False}]},
            content_type="application/json",
            headers=self._auth(),
        )
        assert resp.status_code == 400

    def test_patch_notification_preferences_rejects_push_on_non_resident_event(self):
        from lamto.notifications.services import EVENT_SETTLEMENT_RECORDED

        resp = self.client.patch(
            reverse("api:me-notification-preferences"),
            data={
                "preferences": [
                    {"event_code": EVENT_SETTLEMENT_RECORDED, "push_enabled": False}
                ]
            },
            content_type="application/json",
            headers=self._auth(),
        )
        assert resp.status_code == 400

    def test_me_requires_token(self):
        response = self.client.get(reverse("api:me"))
        assert response.status_code == 401
        assert response["Content-Type"].startswith("application/problem+json")
        assert json.loads(response.content)["code"] == "not_authenticated"

    def test_me_without_active_occupancy_rejects_token(self):
        """No active occupancy → residual knox token is revoked at authenticate.

        Staff (or a former resident after bulk deactivation) never receive data.
        Auth-time cleanup turns leftover tokens into authentication_failed rather
        than leaving a live token that only fails later with 403.
        """
        staff = get_user_model().objects.create_user(
            email="me-staff@example.com",
            password="resident-pass-123",
            display_name="Me Staff",
        )
        headers = self._auth(staff)
        response = self.client.get(reverse("api:me"), headers=headers)
        assert response.status_code == 401
        assert response["Content-Type"].startswith("application/problem+json")
        assert json.loads(response.content)["code"] == "authentication_failed"
        assert not AuthToken.objects.filter(user=staff).exists()
