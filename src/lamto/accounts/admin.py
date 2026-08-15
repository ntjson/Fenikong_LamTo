from django.contrib import admin

from .models import RegistrationRequest


@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    readonly_fields = ("password_hash", "status_token_digest", "created_at", "updated_at")
