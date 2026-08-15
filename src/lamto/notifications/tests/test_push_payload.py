from django.test import TestCase
from firebase_admin import exceptions, messaging

from lamto.notifications.models import NotificationDelivery
from lamto.notifications.push import build_push_payload, classify_push_error
from lamto.notifications.services import (
    EVENT_SETTLEMENT_RECORDED,
    EVENT_PUBLICATION,
)


def _firebase_err(cls, message: str):
    """firebase_admin exception constructors require message + optional cause/http_response."""
    return cls(message, cause=None, http_response=None)


class PushPayloadTests(TestCase):
    def _delivery(self, event_key, event_code, body):
        return NotificationDelivery(
            event_key=event_key, event_code=event_code, subject="secret subject",
            body=body, channel=NotificationDelivery.Channel.PUSH,
        )

    def test_publication_payload_is_minimized_and_deep_linked(self):
        d = self._delivery(f"{EVENT_PUBLICATION}:entry:42", EVENT_PUBLICATION, "Spending of 9999999 VND published")
        title, body, data = build_push_payload(d)
        assert "9999999" not in title and "9999999" not in body  # no sensitive content
        assert data["type"] == "ledger" and data["id"] == "42"
        assert "delivery_id" in data

    def test_unknown_entity_falls_back_to_feed(self):
        d = self._delivery(f"{EVENT_SETTLEMENT_RECORDED}:settlement:7", EVENT_SETTLEMENT_RECORDED, "x")
        _title, _body, data = build_push_payload(d)
        assert data["type"] == "notifications"  # payment is not an allowlisted resident deep link

class ClassifyPushErrorTests(TestCase):
    def test_unregistered_is_terminal(self):
        assert classify_push_error(_firebase_err(messaging.UnregisteredError, "gone")) == "terminal"

    def test_sender_id_mismatch_is_terminal(self):
        assert (
            classify_push_error(_firebase_err(messaging.SenderIdMismatchError, "mismatch"))
            == "terminal"
        )

    def test_invalid_argument_token_messages_are_terminal(self):
        assert (
            classify_push_error(
                _firebase_err(exceptions.InvalidArgumentError, "invalid registration token")
            )
            == "terminal"
        )
        assert (
            classify_push_error(
                _firebase_err(exceptions.InvalidArgumentError, "not a valid FCM registration token")
            )
            == "terminal"
        )
        assert (
            classify_push_error(
                _firebase_err(exceptions.InvalidArgumentError, "Requested entity was not found")
            )
            == "terminal"
        )

    def test_other_errors_are_transient(self):
        assert (
            classify_push_error(_firebase_err(messaging.QuotaExceededError, "rate limited"))
            == "transient"
        )
        assert (
            classify_push_error(
                _firebase_err(exceptions.InvalidArgumentError, "message too big")
            )
            == "transient"
        )
        assert classify_push_error(RuntimeError("network blip")) == "transient"
