"""Push device registry with token rotation/reassignment (spec 7.2)."""

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import Device


@transaction.atomic
def register_device(user, install_id, fcm_token, platform, app_version="") -> Device:
    """Upsert the caller's (user, install_id) device, reassigning the token away
    from any other active device that currently holds it.

    Race-hardened: locks conflicting active token holders with select_for_update,
    then upserts. On partial-unique IntegrityError (device_active_fcm_token_once),
    re-deactivates and retries once.
    """
    from django.db import IntegrityError

    def _deactivate_other_holders():
        list(
            Device.objects.select_for_update()
            .filter(fcm_token=fcm_token, active=True)
            .exclude(user=user, install_id=install_id)
        )
        Device.objects.filter(fcm_token=fcm_token, active=True).exclude(
            user=user, install_id=install_id
        ).update(active=False)

    def _upsert():
        device, _ = Device.objects.update_or_create(
            user=user,
            install_id=install_id,
            defaults={
                "fcm_token": fcm_token,
                "platform": platform,
                "app_version": app_version,
                "active": True,
                "last_seen_at": timezone.now(),
            },
        )
        return device

    _deactivate_other_holders()
    try:
        with transaction.atomic():
            return _upsert()
    except IntegrityError:
        # Nested savepoint so the outer atomic is not poisoned after a partial-unique conflict.
        _deactivate_other_holders()
        with transaction.atomic():
            return _upsert()


def deactivate_device(user, install_id) -> int:
    """Deactivate one install's device (logout / explicit DELETE). Returns rows updated."""
    return Device.objects.filter(user=user, install_id=install_id, active=True).update(
        active=False
    )


def deactivate_user_devices(user) -> int:
    """Deactivate all active devices for a user (logout-all). Returns rows updated."""
    return Device.objects.filter(user=user, active=True).update(active=False)


def deactivate_stale_devices(days: int = 180) -> int:
    """Deactivate devices unseen for `days` (inactivity cleanup, spec 7.2)."""
    cutoff = timezone.now() - timedelta(days=days)
    return Device.objects.filter(active=True, last_seen_at__lt=cutoff).update(
        active=False
    )
