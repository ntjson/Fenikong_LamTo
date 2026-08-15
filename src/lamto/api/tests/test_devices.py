import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from knox.models import AuthToken

from lamto.accounts.models import Building, ResidentOccupancy, Unit
from lamto.notifications.models import Device


class DeviceApiTests(TestCase):
    def setUp(self):
        # ResidentTokenAuthentication requires an active occupancy; bare users
        # get tokens revoked (see authentication.py).
        self.user = get_user_model().objects.create_user(
            email="d@example.test", password="x", display_name="D"
        )
        building = Building.objects.create(name="Device API Building")
        unit = Unit.objects.create(building=building, label="D-1")
        ResidentOccupancy.objects.create(user=self.user, unit=unit, active=True)

    def _auth(self, user=None):
        _instance, token = AuthToken.objects.create(user=user or self.user)
        return {"authorization": f"Token {token}"}

    def test_register_and_delete(self):
        install = str(uuid.uuid4())
        resp = self.client.post(
            reverse("api:devices"),
            data={
                "install_id": install,
                "fcm_token": "tok-1",
                "platform": "ANDROID",
                "app_version": "1.0",
            },
            content_type="application/json",
            headers=self._auth(),
        )
        assert resp.status_code == 200, resp.content
        assert (
            Device.objects.filter(
                user=self.user, install_id=install, active=True
            ).count()
            == 1
        )

        gone = self.client.delete(
            reverse("api:device-delete", args=[install]), headers=self._auth()
        )
        assert gone.status_code == 204
        assert Device.objects.get(user=self.user, install_id=install).active is False

    def test_registration_reassigns_token_from_other_user(self):
        other = get_user_model().objects.create_user(
            email="o@example.test", password="x", display_name="O"
        )
        Device.objects.create(
            user=other,
            install_id="o-install",
            fcm_token="shared",
            platform="IOS",
            active=True,
            last_seen_at=timezone.now(),
        )
        resp = self.client.post(
            reverse("api:devices"),
            data={
                "install_id": str(uuid.uuid4()),
                "fcm_token": "shared",
                "platform": "IOS",
            },
            content_type="application/json",
            headers=self._auth(),
        )
        assert resp.status_code == 200
        assert Device.objects.get(user=other, install_id="o-install").active is False

    def test_logout_with_install_id_deactivates_device(self):
        install = str(uuid.uuid4())
        Device.objects.create(
            user=self.user,
            install_id=install,
            fcm_token="logout-tok",
            platform="ANDROID",
            active=True,
            last_seen_at=timezone.now(),
        )
        resp = self.client.post(
            reverse("api:auth-logout"),
            headers={**self._auth(), "x-install-id": install},
        )
        assert resp.status_code == 204
        assert Device.objects.get(user=self.user, install_id=install).active is False

    def test_logout_without_install_id_leaves_device_active(self):
        install = str(uuid.uuid4())
        Device.objects.create(
            user=self.user,
            install_id=install,
            fcm_token="keep-tok",
            platform="ANDROID",
            active=True,
            last_seen_at=timezone.now(),
        )
        resp = self.client.post(reverse("api:auth-logout"), headers=self._auth())
        assert resp.status_code == 204
        assert Device.objects.get(user=self.user, install_id=install).active is True
