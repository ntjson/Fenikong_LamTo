import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from knox.models import AuthToken

from lamto.notifications.models import NotificationDelivery
from lamto.testing.factories import seed_pilot_world

_TEMP = tempfile.mkdtemp(prefix="lamto-api-notif-")


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _TEMP}},
        "private": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _TEMP}},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class NotificationFeedTests(TestCase):
    def setUp(self):
        self.seed = seed_pilot_world(building_name="API Notif B", email_prefix="apin", create_sample_report=False)
        self.resident = self.seed.residents[0]
        self.delivery = NotificationDelivery.objects.create(
            recipient=self.resident, building=self.seed.building,
            channel=NotificationDelivery.Channel.IN_APP, status=NotificationDelivery.Status.AVAILABLE,
            event_key="ledger.publication:x:1", event_code="ledger.publication",
            subject="New spending published", body="A new expenditure was published.",
        )

    def _auth(self, user=None):
        _instance, token = AuthToken.objects.create(user=user or self.resident)
        return {"authorization": f"Token {token}"}

    def _occ(self):
        from lamto.accounts.models import ResidentOccupancy
        occ = ResidentOccupancy.objects.get(user=self.resident, active=True)
        return {**self._auth(), "x-lamto-occupancy": str(occ.pk)}

    def test_feed_lists_available_and_mark_read(self):
        resp = self.client.get(reverse("api:notifications"), headers=self._occ())
        assert resp.status_code == 200
        results = resp.json()["results"]
        assert len(results) == 1 and results[0]["read_at"] is None

        read = self.client.post(reverse("api:notification-read", kwargs={"pk": self.delivery.pk}), headers=self._auth())
        assert read.status_code == 204
        self.delivery.refresh_from_db()
        assert self.delivery.read_at is not None

    def test_feed_filters_by_event_code(self):
        NotificationDelivery.objects.create(
            recipient=self.resident, building=self.seed.building,
            channel=NotificationDelivery.Channel.IN_APP, status=NotificationDelivery.Status.AVAILABLE,
            event_key="building.announcement:x:1", event_code="building.announcement",
            subject="Announcement", body="News",
        )

        resp = self.client.get(
            reverse("api:notifications"),
            {"event_code": "building.announcement"},
            headers=self._occ(),
        )

        assert resp.status_code == 200
        assert [row["event_code"] for row in resp.json()["results"]] == ["building.announcement"]

    def test_feed_filters_by_read_state(self):
        self.delivery.read_at = timezone.now()
        self.delivery.save(update_fields=["read_at"])
        unread = NotificationDelivery.objects.create(
            recipient=self.resident, building=self.seed.building,
            channel=NotificationDelivery.Channel.IN_APP, status=NotificationDelivery.Status.AVAILABLE,
            event_key="ledger.publication:x:2", event_code="ledger.publication",
            subject="Unread", body="Unread",
        )

        unread_resp = self.client.get(
            reverse("api:notifications"), {"unread": "true"}, headers=self._occ()
        )
        read_resp = self.client.get(
            reverse("api:notifications"), {"unread": "false"}, headers=self._occ()
        )

        assert [row["id"] for row in unread_resp.json()["results"]] == [unread.pk]
        assert [row["id"] for row in read_resp.json()["results"]] == [self.delivery.pk]

    def test_feed_filters_compose_with_cursor_pagination(self):
        self.delivery.delete()
        for number in range(21):
            NotificationDelivery.objects.create(
                recipient=self.resident, building=self.seed.building,
                channel=NotificationDelivery.Channel.IN_APP, status=NotificationDelivery.Status.AVAILABLE,
                event_key=f"building.announcement:x:{number}", event_code="building.announcement",
                subject=f"Announcement {number}", body="News",
            )
        NotificationDelivery.objects.create(
            recipient=self.resident, building=self.seed.building,
            channel=NotificationDelivery.Channel.IN_APP, status=NotificationDelivery.Status.AVAILABLE,
            event_key="ledger.publication:x:noise", event_code="ledger.publication",
            subject="Noise", body="Noise",
        )

        first = self.client.get(
            reverse("api:notifications"),
            {"event_code": "building.announcement", "unread": "true"},
            headers=self._occ(),
        )
        second = self.client.get(first.json()["next"], headers=self._occ())

        assert len(first.json()["results"]) == 20
        assert len(second.json()["results"]) == 1
        assert all(
            row["event_code"] == "building.announcement" and row["read_at"] is None
            for row in first.json()["results"] + second.json()["results"]
        )

    def test_feed_rejects_invalid_unread_boolean(self):
        resp = self.client.get(
            reverse("api:notifications"), {"unread": "sometimes"}, headers=self._occ()
        )

        assert resp.status_code == 400
        assert resp.json()["code"] == "validation_failed"
        assert "unread" in resp.json()["errors"]

    def test_feed_filters_remain_tenant_and_user_scoped(self):
        from django.contrib.auth import get_user_model
        from lamto.accounts.models import ResidentOccupancy

        neighbor = get_user_model().objects.create_user(
            email="apin-neighbor@example.com", password="x", display_name="Neighbor"
        )
        ResidentOccupancy.objects.create(user=neighbor, unit=self.seed.unit, active=True)
        neighbor_delivery = NotificationDelivery.objects.create(
            recipient=neighbor, building=self.seed.building,
            channel=NotificationDelivery.Channel.IN_APP, status=NotificationDelivery.Status.AVAILABLE,
            event_key="building.announcement:neighbor:1", event_code="building.announcement",
            subject="Neighbor", body="Neighbor",
        )
        foreign = seed_pilot_world(
            building_name="API Notif Foreign", email_prefix="apinforeign", create_sample_report=False
        )
        foreign_delivery = NotificationDelivery.objects.create(
            recipient=foreign.residents[0], building=foreign.building,
            channel=NotificationDelivery.Channel.IN_APP, status=NotificationDelivery.Status.AVAILABLE,
            event_key="building.announcement:foreign:1", event_code="building.announcement",
            subject="Foreign", body="Foreign",
        )

        responses = [
            self.client.get(
                reverse("api:notifications"),
                query,
                headers=self._occ(),
            )
            for query in (
                {"event_code": "building.announcement"},
                {"unread": "true"},
                {"event_code": "building.announcement", "unread": "true"},
            )
        ]

        excluded_ids = {neighbor_delivery.pk, foreign_delivery.pk}
        assert all(response.status_code == 200 for response in responses)
        assert all(
            excluded_ids.isdisjoint(row["id"] for row in response.json()["results"])
            for response in responses
        )

    def test_feed_exposes_event_key_for_deep_links(self):
        resp = self.client.get(reverse("api:notifications"), headers=self._occ())
        assert resp.status_code == 200
        row = resp.json()["results"][0]
        # Opaque deep-link reference only — not subject/body free text (A8).
        assert row["event_key"] == "ledger.publication:x:1"
        assert row["event_code"] == "ledger.publication"
        assert row["event_key"] == self.delivery.event_key
        assert self.delivery.subject not in row["event_key"]
        assert self.delivery.body not in row["event_key"]

    def test_mark_read_foreign_delivery_is_404(self):
        from django.contrib.auth import get_user_model
        from lamto.accounts.models import ResidentOccupancy
        stranger = get_user_model().objects.create_user(email="apin-x@example.com", password="x", display_name="X")
        ResidentOccupancy.objects.create(user=stranger, unit=self.seed.unit, active=True)
        resp = self.client.post(
            reverse("api:notification-read", kwargs={"pk": self.delivery.pk}), headers=self._auth(stranger)
        )
        assert resp.status_code == 404
