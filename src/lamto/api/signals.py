"""Server-side knox token revocation (spec 3.2).

Safety net for ``.save()`` paths. Bulk ``queryset.update()`` bypasses signals;
prefer ``lamto.api.services.deactivate_occupancy`` /
``deactivate_occupancies`` / ``deactivate_user`` or call
``revoke_tokens_if_no_active_occupancy`` defensively after bulk updates.
Authentication itself also rejects inactive users (knox checks ``is_active``).
"""

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from knox.models import AuthToken

from lamto.accounts.models import ResidentOccupancy
from lamto.api.services import revoke_tokens_if_no_active_occupancy


@receiver(
    post_save,
    sender=settings.AUTH_USER_MODEL,
    dispatch_uid="api.revoke_tokens_inactive_user",
)
def revoke_tokens_for_inactive_user(sender, instance, **kwargs):
    if not instance.is_active:
        AuthToken.objects.filter(user=instance).delete()


@receiver(
    post_save,
    sender=ResidentOccupancy,
    dispatch_uid="api.revoke_tokens_last_occupancy",
)
def revoke_tokens_without_active_occupancy(sender, instance, **kwargs):
    if instance.active:
        return
    revoke_tokens_if_no_active_occupancy(instance.user)
