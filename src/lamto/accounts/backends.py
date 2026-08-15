"""Phone-or-email authentication (spec 2.1: residents log in by phone)."""

import re

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

_SEPARATORS = re.compile(r"[\s.\-()]+")
_VN_PHONE = re.compile(r"^0\d{9,10}$")


def normalize_phone(raw):
    """Return the canonical local phone form (0xxxxxxxxx) or None."""
    if not raw:
        return None
    value = _SEPARATORS.sub("", str(raw))
    if value.startswith("+84"):
        value = "0" + value[3:]
    elif value.startswith("84") and len(value) >= 11:
        value = "0" + value[2:]
    if _VN_PHONE.fullmatch(value):
        return value
    return None


class PhoneOrEmailBackend(ModelBackend):
    """Authenticate with email (staff) or Vietnamese phone number (residents)."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return None
        phone = normalize_phone(username)
        try:
            if phone is not None:
                user = UserModel.objects.get(phone=phone)
            else:
                user = UserModel.objects.get(email__iexact=username)
        except UserModel.DoesNotExist:
            # Run a hash anyway so lookup misses take the same time.
            UserModel().set_password(password)
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
