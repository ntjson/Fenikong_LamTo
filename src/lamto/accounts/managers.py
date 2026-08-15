from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email=None, password=None, **fields):
        if not email and (fields.get("is_staff") or fields.get("is_superuser")):
            raise ValueError("Staff users require an email address")
        if not email and not fields.get("phone"):
            raise ValueError("An email or phone number is required")
        user = self.model(
            email=self.normalize_email(email) if email else None,
            **fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **fields):
        if not email:
            raise ValueError("Superusers require an email address")
        fields.setdefault("is_staff", True)
        fields.setdefault("is_superuser", True)
        fields.setdefault("is_active", True)
        if fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email=email, password=password, **fields)
