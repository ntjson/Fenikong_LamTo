from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import FaceEnrollment, GateEvent, GatePurgeHeartbeat, PendingEnrollmentPhoto, ReviewStatus
from .photos import process_photo_deletions, queue_photo_deletion

PURGE_STALE_AFTER_HOURS = 2


def purge_expired_gate_events(now=None):
    now = now or timezone.now()
    deleted, _ = GateEvent.objects.filter(occurred_at__lt=now - timedelta(hours=settings.GATE_EVENT_RETENTION_HOURS)).delete()
    return deleted


def purge_expired_enrollment_photos(now=None):
    now = now or timezone.now()
    expired = list(PendingEnrollmentPhoto.objects.filter(expires_at__lte=now).values_list("enrollment_id", flat=True))
    for enrollment_id in expired:
        with transaction.atomic():
            enrollment = FaceEnrollment.objects.select_for_update().get(pk=enrollment_id)
            photo = PendingEnrollmentPhoto.objects.select_for_update().filter(enrollment=enrollment, expires_at__lte=now).first()
            if photo is None:
                continue
            if enrollment.status == ReviewStatus.PENDING:
                enrollment.status = ReviewStatus.EXPIRED
                enrollment.embedding = None
                enrollment.save(update_fields=["status", "embedding"])
            queue_photo_deletion(photo)
    process_photo_deletions()
    return len(expired)


def record_purge_success(*, events, photos):
    heartbeat = GatePurgeHeartbeat.objects.order_by("pk").first()
    values = {"last_success_at": timezone.now(), "events_deleted": events, "photos_deleted": photos}
    if heartbeat is None:
        return GatePurgeHeartbeat.objects.create(**values)
    for field, value in values.items():
        setattr(heartbeat, field, value)
    heartbeat.save(update_fields=list(values))
    return heartbeat


def purge_is_stale(now=None):
    now = now or timezone.now()
    heartbeat = GatePurgeHeartbeat.objects.order_by("-last_success_at").first()
    return heartbeat is None or heartbeat.last_success_at < now - timedelta(hours=PURGE_STALE_AFTER_HOURS)
