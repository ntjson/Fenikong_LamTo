import pytest

from lamto.accounts.models import User


def test_create_phone_only_user(db):
    user = User.objects.create_user(
        email=None,
        phone="+84901234567",
        password="correct horse battery staple",
    )

    assert user.email is None
    assert user.phone == "0901234567"
    assert user.check_password("correct horse battery staple")


def test_create_superuser_requires_email(db):
    with pytest.raises(ValueError, match="email"):
        User.objects.create_superuser(
            email=None,
            phone="+84901234567",
            password="correct horse battery staple",
        )


def test_create_staff_user_requires_email(db):
    with pytest.raises(ValueError, match="email"):
        User.objects.create_user(
            email=None,
            phone="+84901234567",
            password="correct horse battery staple",
            is_staff=True,
        )
