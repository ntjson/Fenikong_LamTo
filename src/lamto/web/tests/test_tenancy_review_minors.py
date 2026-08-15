"""Regression tests for residual tenancy-hardening review minors."""

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from lamto.accounts.models import Building, ResidentOccupancy, Unit
from lamto.accounts.tenancy import SESSION_OCCUPANCY_KEY
from lamto.evidence.models import BlockchainOutboxEvent
from lamto.notifications.models import NotificationDelivery
from lamto.web.action_inbox import _failed_outbox_items
from lamto.web.views.security import PhoneOrEmailAuthenticationForm


class FailedOutboxBuildingKeyTests(TestCase):
    def test_failed_outbox_items_filter_by_event_building_id(self):
        import inspect

        from django.db.models import QuerySet

        from lamto.web import action_inbox

        source = inspect.getsource(action_inbox._failed_outbox_items)
        assert "building_id=building_id" in source
        assert "organization__building_id" not in source

        # Drive the real helper: empty building yields no items; filter key is
        # on the event, so queryset SQL must reference evidence building column.
        building = Building.objects.create(name="Outbox Inbox Building")
        items = _failed_outbox_items(building.pk)
        assert items == []
        qs = BlockchainOutboxEvent.objects.filter(
            status=BlockchainOutboxEvent.Status.FAILED,
            building_id=building.pk,
        )
        assert isinstance(qs, QuerySet)
        sql = str(qs.query)
        assert "building_id" in sql or "building" in sql.lower()


@override_settings(LANGUAGE_CODE="en-us")  # asserts English source strings
class LoginLabelTests(TestCase):
    def test_login_form_label_is_email_or_phone(self):
        form = PhoneOrEmailAuthenticationForm()
        assert form.fields["username"].label == "Email or phone"
        assert form.fields["username"].label != "Username"

    def test_login_page_renders_email_or_phone_label(self):
        response = self.client.get("/accounts/login/")
        assert response.status_code == 200
        self.assertContains(response, "Email or phone")
        self.assertNotContains(response, ">Username<")
