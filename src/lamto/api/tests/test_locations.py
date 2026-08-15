import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse
from knox.models import AuthToken

from lamto.maintenance.models import BuildingLocation
from lamto.testing.factories import seed_pilot_world

_TEMP = tempfile.mkdtemp(prefix="lamto-api-loc-")


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _TEMP}},
        "private": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _TEMP}},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class LocationListTests(TestCase):
    def setUp(self):
        self.seed = seed_pilot_world(building_name="API Loc B", email_prefix="apiloc", create_sample_report=False)
        self.resident = self.seed.residents[0]
        # A child + an inactive sibling of the seed location.
        self.child = BuildingLocation.objects.create(
            building=self.seed.building, parent=self.seed.location, name="Cabin"
        )
        BuildingLocation.objects.create(building=self.seed.building, name="Retired", active=False)

    def _auth(self):
        _instance, token = AuthToken.objects.create(user=self.resident)
        return {"authorization": f"Token {token}"}

    def test_returns_active_tree_only(self):
        resp = self.client.get(reverse("api:locations"), headers=self._auth())
        assert resp.status_code == 200
        names = {row["name"] for row in resp.json()}
        assert "Cabin" in names
        assert "Retired" not in names
        child = next(row for row in resp.json() if row["name"] == "Cabin")
        assert child["parent_id"] == self.seed.location.pk
