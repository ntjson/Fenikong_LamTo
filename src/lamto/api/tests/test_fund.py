"""GET /fund/summary + X-LamTo-Occupancy context rules (spec 3.3, 3.4)."""

import json
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from knox.models import AuthToken

from lamto.accounts.models import Building, ResidentOccupancy, Unit
from lamto.finance.fund import fund_balance
from lamto.testing.factories import seed_pilot_world

_TEMP_STORAGE = tempfile.mkdtemp(prefix="lamto-api-fund-")


def problem(response):
    return json.loads(response.content)


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": _TEMP_STORAGE},
        },
        "private": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": _TEMP_STORAGE},
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
)
class FundSummaryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.seed = seed_pilot_world(
            building_name="API Fund Building",
            email_prefix="apif",
            create_sample_report=False,
        )
        cls.resident = cls.seed.residents[0]
        cls.occupancy = ResidentOccupancy.objects.get(user=cls.resident, active=True)
        # A second building with no fund rows, for multi-occupancy cases.
        cls.other_building = Building.objects.create(name="API Fund Building Two")
        cls.other_unit = Unit.objects.create(building=cls.other_building, label="C-303")
        # A stranger whose occupancy id must never resolve for cls.resident.
        stranger = get_user_model().objects.create_user(
            email="apif-stranger@example.com",
            password="resident-pass-123",
            display_name="Stranger",
        )
        cls.stranger_occupancy = ResidentOccupancy.objects.create(
            user=stranger, unit=cls.other_unit, active=True
        )

    def _auth(self):
        _instance, token = AuthToken.objects.create(user=self.resident)
        return {"authorization": f"Token {token}"}

    def test_sole_occupancy_auto_selected(self):
        response = self.client.get(reverse("api:fund-summary"), headers=self._auth())
        assert response.status_code == 200, response.content
        body = response.json()
        expected = fund_balance(self.seed.building.pk, verified_only=True)
        assert expected > 0
        assert body["balance_vnd"] == expected
        assert body["period_days"] == 30
        assert body["period_inflows_vnd"] >= 0
        assert body["period_outflows_vnd"] >= 0

    def test_multiple_occupancies_without_header_is_422(self):
        second = ResidentOccupancy.objects.create(
            user=self.resident, unit=self.other_unit, active=True
        )
        response = self.client.get(reverse("api:fund-summary"), headers=self._auth())
        assert response.status_code == 422
        assert problem(response)["code"] == "occupancy_selection_required"
        # With the header, each occupancy resolves to its own building.
        chosen = self.client.get(
            reverse("api:fund-summary"),
            headers={**self._auth(), "x-lamto-occupancy": str(second.pk)},
        )
        assert chosen.status_code == 200
        assert chosen.json()["balance_vnd"] == 0  # second building has no fund rows

    def test_foreign_occupancy_header_is_404(self):
        response = self.client.get(
            reverse("api:fund-summary"),
            headers={**self._auth(), "x-lamto-occupancy": str(self.stranger_occupancy.pk)},
        )
        assert response.status_code == 404
        assert problem(response)["code"] == "not_found"

    def test_garbage_occupancy_header_is_404(self):
        response = self.client.get(
            reverse("api:fund-summary"),
            headers={**self._auth(), "x-lamto-occupancy": "abc"},
        )
        assert response.status_code == 404

    def test_inactive_own_occupancy_header_is_404(self):
        extra = ResidentOccupancy.objects.create(
            user=self.resident, unit=self.other_unit, active=True
        )
        ResidentOccupancy.objects.filter(pk=extra.pk).update(active=False)
        response = self.client.get(
            reverse("api:fund-summary"),
            headers={**self._auth(), "x-lamto-occupancy": str(extra.pk)},
        )
        assert response.status_code == 404


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": _TEMP_STORAGE},
        },
        "private": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": _TEMP_STORAGE},
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
)
class FundSeriesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.seed = seed_pilot_world(
            building_name="API Series Building",
            email_prefix="apis",
            create_sample_report=False,
        )
        cls.resident = cls.seed.residents[0]

    def _auth(self):
        _instance, token = AuthToken.objects.create(user=self.resident)
        return {"authorization": f"Token {token}"}

    def test_default_range_shape_and_final_balance(self):
        response = self.client.get(reverse("api:fund-series"), headers=self._auth())
        assert response.status_code == 200, response.content
        body = response.json()
        assert body["range"] == "6m"
        assert len(body["points"]) == 6
        point = body["points"][-1]
        assert set(point) == {
            "period_start", "inflows_vnd", "outflows_vnd", "balance_vnd",
        }
        assert point["balance_vnd"] == fund_balance(
            self.seed.building.pk, verified_only=True
        )

    def test_each_range_bucket_count(self):
        for range_key, count in (("30d", 30), ("6m", 6), ("12m", 12)):
            response = self.client.get(
                reverse("api:fund-series"), {"range": range_key},
                headers=self._auth(),
            )
            assert response.status_code == 200
            assert len(response.json()["points"]) == count

    def test_invalid_range_is_400(self):
        response = self.client.get(
            reverse("api:fund-series"), {"range": "7d"}, headers=self._auth()
        )
        assert response.status_code == 400
        assert problem(response)["code"] == "validation_failed"

    def test_unauthenticated_is_401(self):
        assert self.client.get(reverse("api:fund-series")).status_code == 401
