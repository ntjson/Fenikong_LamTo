from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lamto.api"

    def ready(self):
        from lamto.api import authentication  # noqa: F401  (OpenAPI knox scheme)
        from lamto.api import signals  # noqa: F401  (token-revocation receivers)
