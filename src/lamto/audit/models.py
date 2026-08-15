from django.conf import settings
from django.db import models

from lamto.accounts.models import ManagementMembership


class AuditEvent(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    membership = models.ForeignKey(ManagementMembership, null=True, blank=True, on_delete=models.PROTECT)
    action = models.CharField(max_length=128)
    target_type = models.CharField(max_length=128)
    target_id = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict)
    result = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Audit events are append-only.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Audit events are append-only.")
