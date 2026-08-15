import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from lamto.accounts.models import Building, ResidentOccupancy, Unit
from lamto.notifications.devices import register_device
from lamto.notifications.models import Device, NotificationDelivery
from lamto.notifications.services import EVENT_PUBLICATION, process_delivery


def _make_resident(building, unit, email):
    user = get_user_model().objects.create_user(email=email, password="x", display_name="R")
    ResidentOccupancy.objects.create(user=user, unit=unit, active=True)
    return user


def _push_delivery(user, building):
    return NotificationDelivery.objects.create(
        recipient=user,
        building=building,
        channel=NotificationDelivery.Channel.PUSH,
        status=NotificationDelivery.Status.PENDING,
        event_key=f"{EVENT_PUBLICATION}:entry:1",
        event_code=EVENT_PUBLICATION,
        subject="s",
        body="b",
    )


@override_settings(PUSH_ENABLED=True)
class PushWorkerTests(TestCase):
    def setUp(self):
        self.building = Building.objects.create(name="Worker B")
        self.unit = Unit.objects.create(building=self.building, label="A-1")
        self.resident = _make_resident(self.building, self.unit, "wr@example.test")
        register_device(self.resident, str(uuid.uuid4()), "tok-1", Device.Platform.ANDROID)

    @patch("lamto.notifications.services.send_push", return_value="msg-1")
    def test_sends_and_marks_sent(self, send):
        delivery = _push_delivery(self.resident, self.building)
        result = process_delivery(delivery)
        assert result.status == NotificationDelivery.Status.SENT
        assert send.call_count == 1

    @patch("lamto.notifications.services.send_push")
    def test_terminal_error_deactivates_device(self, send):
        from firebase_admin import messaging

        from lamto.notifications.services import PUSH_SUPPRESSED_PREFIX

        send.side_effect = messaging.UnregisteredError("gone")
        delivery = _push_delivery(self.resident, self.building)
        result = process_delivery(delivery)
        assert Device.objects.filter(user=self.resident, active=True).count() == 0
        # All-terminal fan-out is not true FCM success (metrics / daily cap).
        assert result.status == NotificationDelivery.Status.SENT
        assert result.last_error == f"{PUSH_SUPPRESSED_PREFIX}all_tokens_terminal"

    @patch("lamto.notifications.services.send_push", return_value="msg-1")
    def test_revalidation_suppresses_when_occupancy_gone(self, send):
        ResidentOccupancy.objects.filter(user=self.resident).update(active=False)
        delivery = _push_delivery(self.resident, self.building)
        result = process_delivery(delivery)
        assert send.call_count == 0
        assert result.status == NotificationDelivery.Status.SENT  # non-retryable; in-app authoritative
        assert result.last_error.startswith("suppressed:")  # not a true FCM success

    @patch("lamto.notifications.services.send_push")
    def test_partial_success_retry_skips_already_sent_devices(self, send):
        """On retry after multi-device partial success, do not re-send successful tokens."""
        d1 = Device.objects.get(user=self.resident, active=True)
        d2 = register_device(
            self.resident, str(uuid.uuid4()), "tok-2", Device.Platform.IOS
        )

        def _side_effect(token, **kwargs):
            if token == d1.fcm_token:
                return "msg-ok"
            raise RuntimeError("transient-unavailable")

        send.side_effect = _side_effect
        delivery = _push_delivery(self.resident, self.building)
        result = process_delivery(delivery)
        assert result.status == NotificationDelivery.Status.FAILED
        assert d1.pk in result.push_sent_device_ids
        assert d2.pk not in result.push_sent_device_ids
        first_calls = send.call_count
        assert first_calls == 2

        # Retry: only the failed device should be attempted again.
        send.reset_mock()
        send.side_effect = lambda token, **kwargs: "msg-retry"
        # Reset for claimable retry path
        NotificationDelivery.objects.filter(pk=delivery.pk).update(
            status=NotificationDelivery.Status.FAILED,
            next_retry_at=None,
        )
        delivery.refresh_from_db()
        delivery.status = NotificationDelivery.Status.FAILED
        result2 = process_delivery(delivery)
        assert result2.status == NotificationDelivery.Status.SENT
        # Only tok-2 (the previously failed device) is sent again.
        assert send.call_count == 1
        assert send.call_args.args[0] == d2.fcm_token
        assert set(result2.push_sent_device_ids) == {d1.pk, d2.pk}

    @override_settings(PUSH_ENABLED=True, PUSH_DAILY_CAP_PER_CATEGORY=2)
    @patch("lamto.notifications.services.send_push", return_value="msg-1")
    def test_publication_collapse_key_and_daily_cap(self, send):
        from lamto.notifications.services import PUSH_SUPPRESSED_PREFIX, _collapse_key

        d1 = _push_delivery(self.resident, self.building)
        process_delivery(d1)
        assert send.call_args.kwargs["collapse_key"] == _collapse_key(d1)
        assert _collapse_key(d1) == f"pub:{self.building.pk}"

        # Suppressed SENT rows must not consume the daily cap.
        NotificationDelivery.objects.create(
            recipient=self.resident,
            building=self.building,
            channel=NotificationDelivery.Channel.PUSH,
            status=NotificationDelivery.Status.SENT,
            event_key=f"{EVENT_PUBLICATION}:entry:suppressed",
            event_code=EVENT_PUBLICATION,
            subject="s",
            body="b",
            last_error=f"{PUSH_SUPPRESSED_PREFIX}no_active_devices",
        )

        # One true success so far; second still allowed under cap=2.
        send.reset_mock()
        d2 = NotificationDelivery.objects.create(
            recipient=self.resident,
            building=self.building,
            channel=NotificationDelivery.Channel.PUSH,
            status=NotificationDelivery.Status.PENDING,
            event_key=f"{EVENT_PUBLICATION}:entry:2",
            event_code=EVENT_PUBLICATION,
            subject="s",
            body="b",
        )
        process_delivery(d2)
        assert send.call_count == 1

        # Two true FCM successes today (cap=2): the next is suppressed without a send.
        send.reset_mock()
        d3 = NotificationDelivery.objects.create(
            recipient=self.resident,
            building=self.building,
            channel=NotificationDelivery.Channel.PUSH,
            status=NotificationDelivery.Status.PENDING,
            event_key=f"{EVENT_PUBLICATION}:entry:3",
            event_code=EVENT_PUBLICATION,
            subject="s",
            body="b",
        )
        result = process_delivery(d3)
        assert send.call_count == 0
        assert result.status == NotificationDelivery.Status.SENT
        assert result.last_error.startswith("suppressed:")
        assert result.last_error == f"{PUSH_SUPPRESSED_PREFIX}daily_cap"
