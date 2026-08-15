from django.test import TestCase, override_settings
from django.urls import reverse


class PreAuthShellTests(TestCase):
    @override_settings(LANGUAGE_CODE="en")
    def test_login_uses_request_language_without_resident_chrome(self):
        response = self.client.get(reverse("login"))

        self.assertContains(response, '<html lang="en">')
        self.assertNotContains(response, "maintenance accountability for residents")
        self.assertNotContains(response, "building-label")
