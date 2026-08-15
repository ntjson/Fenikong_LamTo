from django.contrib.auth import get_user_model
from django.test import TestCase

from lamto.notifications.models import NotificationPreference
from lamto.notifications.services import EVENT_PUBLICATION
from lamto.web.forms.staff import NotificationPreferenceForm


class PushPreferenceFormTests(TestCase):
    def test_saves_push_enabled_flag(self):
        user = get_user_model().objects.create_user(
            email="p@example.test", password="x", display_name="P"
        )
        form = NotificationPreferenceForm(
            data={f"push_{EVENT_PUBLICATION}": "", f"email_{EVENT_PUBLICATION}": "on"},
            user=user,
        )
        assert form.is_valid(), form.errors
        form.save()
        pref = NotificationPreference.objects.get(user=user, event_code=EVENT_PUBLICATION)
        assert pref.push_enabled is False and pref.email_enabled is True
