from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from lamto.notifications.models import NotificationDelivery
from lamto.notifications.push import build_push_payload
from lamto.notifications.services import process_delivery


class AnnouncementPushTests(TestCase):
    def _delivery(self, action="published"):
        recipient = get_user_model().objects.create_user(
            email="push-worker@example.test", password="pw", display_name="Resident"
        )
        return NotificationDelivery.objects.create(
            recipient=recipient,
            event_code="building.announcement",
            event_key=(
                "building.announcement:announcement:7:revision:1:" f"{action}"
            ),
            subject="Secret title",
            body="Secret body",
            channel=NotificationDelivery.Channel.PUSH,
        )

    def test_payload_uses_generic_action_specific_vietnamese_copy(self):
        expected = {
            "published": "Thông báo mới từ ban quản lý",
            "updated": "Thông báo của ban quản lý đã được cập nhật",
            "withdrawn": "Thông báo của ban quản lý đã được thu hồi",
        }
        for action, expected_title in expected.items():
            delivery = NotificationDelivery(
                pk=9,
                event_code="building.announcement",
                event_key=(
                    "building.announcement:announcement:7:revision:1:" f"{action}"
                ),
                subject="Secret title",
                body="Secret body",
                channel=NotificationDelivery.Channel.PUSH,
            )
            title, body, data = build_push_payload(delivery)
            assert title == expected_title
            assert "Secret" not in title + body
            assert data["type"] == "notifications"

    @patch("lamto.notifications.services._recipient_can_receive_push", return_value=True)
    @patch("lamto.notifications.models.Device.objects.filter")
    @patch("lamto.notifications.services.send_push")
    def test_worker_retries_announcement_push(self, send, devices, _eligible):
        device = type("Device", (), {"pk": 11, "fcm_token": "token"})()
        devices.return_value = [device]
        send.side_effect = [RuntimeError("temporary"), "message-id"]
        delivery = self._delivery()

        first = process_delivery(delivery)
        assert first.status == NotificationDelivery.Status.FAILED
        first.status = NotificationDelivery.Status.FAILED
        second = process_delivery(first)
        assert second.status == NotificationDelivery.Status.SENT
        assert second.attempts == 2
