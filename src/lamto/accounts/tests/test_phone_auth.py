from django.contrib.auth import authenticate, get_user_model
from django.test import TestCase

from lamto.accounts.backends import normalize_phone


class NormalizePhoneTests(TestCase):
    def test_accepts_local_and_international_forms(self):
        assert normalize_phone("0901234567") == "0901234567"
        assert normalize_phone("+84 90 123 4567") == "0901234567"
        assert normalize_phone("84901234567") == "0901234567"
        assert normalize_phone("090-123-4567") == "0901234567"

    def test_rejects_non_phones(self):
        assert normalize_phone("") is None
        assert normalize_phone(None) is None
        assert normalize_phone("resident@example.test") is None
        assert normalize_phone("12345") is None


class PhoneOrEmailBackendTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            email="phone-user@example.test", password="pw-secret", display_name="P"
        )
        cls.user.phone = "0901234567"
        cls.user.save(update_fields=["phone"])

    def test_email_login_still_works(self):
        assert authenticate(None, username="phone-user@example.test", password="pw-secret") == self.user

    def test_phone_login_works_with_formatting(self):
        assert authenticate(None, username="+84 901 234 567", password="pw-secret") == self.user

    def test_wrong_password_fails(self):
        assert authenticate(None, username="0901234567", password="nope") is None

    def test_inactive_user_rejected(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        assert authenticate(None, username="0901234567", password="pw-secret") is None

    def test_login_view_accepts_phone(self):
        self.client.logout()
        response = self.client.post(
            "/accounts/login/",
            {"username": "0901234567", "password": "pw-secret"},
        )
        assert response.status_code == 302

    def test_phone_is_normalized_on_save(self):
        self.user.phone = "+84 901 234 567"
        self.user.save()
        self.user.refresh_from_db()
        assert self.user.phone == "0901234567"
