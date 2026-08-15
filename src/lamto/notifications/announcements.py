from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from lamto.accounts.services import require_management
from lamto.audit.services import record_audit
from lamto.notifications.models import Announcement, NotificationDelivery
from lamto.notifications.services import EVENT_ANNOUNCEMENT, queue_notification


class AnnouncementConflict(Exception):
    pass


def in_app_event_key(announcement_id: int) -> str:
    return f"{EVENT_ANNOUNCEMENT}:announcement:{announcement_id}"


def push_event_key(announcement_id: int, revision: int, action: str) -> str:
    return (
        f"{EVENT_ANNOUNCEMENT}:announcement:{announcement_id}:"
        f"revision:{revision}:{action}"
    )


def _active_residents(building_id: int):
    return get_user_model().objects.filter(
        residentoccupancy__unit__building_id=building_id,
        residentoccupancy__active=True,
        is_active=True,
    ).distinct()


def _queue_push(announcement: Announcement, recipient, action: str) -> None:
    queue_notification(
        recipient=recipient,
        building=announcement.building,
        event_code=EVENT_ANNOUNCEMENT,
        event_key=push_event_key(announcement.id, announcement.revision, action),
        subject=announcement.title,
        body=announcement.body,
        channels=[NotificationDelivery.Channel.PUSH],
    )


@transaction.atomic
def publish_announcement(actor, building_id: int, title: str, body: str) -> Announcement:
    membership = require_management(actor, building_id)
    announcement = Announcement(
        building_id=building_id,
        title=title,
        body=body,
        created_by=actor,
        updated_by=actor,
    )
    announcement.full_clean()
    announcement.save()

    recipients = _active_residents(building_id)
    for recipient in recipients:
        queue_notification(
            recipient=recipient,
            building=announcement.building,
            event_code=EVENT_ANNOUNCEMENT,
            event_key=in_app_event_key(announcement.id),
            subject=announcement.title,
            body=announcement.body,
            channels=[NotificationDelivery.Channel.IN_APP],
        )
        _queue_push(announcement, recipient, "published")

    NotificationDelivery.objects.filter(
        building_id=building_id,
        event_key=in_app_event_key(announcement.id),
        channel=NotificationDelivery.Channel.IN_APP,
    ).update(status=NotificationDelivery.Status.AVAILABLE)

    record_audit(
        actor=actor,
        membership=membership,
        action="announcement.published",
        target_type="Announcement",
        target_id=str(announcement.id),
        result="accepted",
        metadata={
            "announcement_id": announcement.id,
            "revision": announcement.revision,
        },
    )
    return announcement


@transaction.atomic
def edit_announcement(
    actor,
    announcement_id: int,
    *,
    expected_revision: int,
    title: str,
    body: str,
) -> Announcement:
    announcement = (
        Announcement.objects.select_for_update()
        .select_related("building")
        .get(pk=announcement_id)
    )
    membership = require_management(actor, announcement.building_id)
    if (
        announcement.state != Announcement.State.PUBLISHED
        or announcement.revision != expected_revision
    ):
        raise AnnouncementConflict()

    announcement.title = title
    announcement.body = body
    announcement.revision += 1
    announcement.updated_by = actor
    announcement.full_clean()
    announcement.save()

    for recipient in _active_residents(announcement.building_id):
        queue_notification(
            recipient=recipient,
            building=announcement.building,
            event_code=EVENT_ANNOUNCEMENT,
            event_key=in_app_event_key(announcement.id),
            subject=announcement.title,
            body=announcement.body,
            channels=[NotificationDelivery.Channel.IN_APP],
        )
        _queue_push(announcement, recipient, "updated")

    NotificationDelivery.objects.filter(
        building_id=announcement.building_id,
        event_key=in_app_event_key(announcement.id),
        channel=NotificationDelivery.Channel.IN_APP,
    ).update(
        subject=announcement.title,
        body=announcement.body,
        read_at=None,
        status=NotificationDelivery.Status.AVAILABLE,
    )
    record_audit(
        actor=actor,
        membership=membership,
        action="announcement.updated",
        target_type="Announcement",
        target_id=str(announcement.id),
        result="accepted",
        metadata={"announcement_id": announcement.id, "revision": announcement.revision},
    )
    return announcement


@transaction.atomic
def withdraw_announcement(
    actor, announcement_id: int, *, expected_revision: int
) -> Announcement:
    announcement = (
        Announcement.objects.select_for_update()
        .select_related("building")
        .get(pk=announcement_id)
    )
    membership = require_management(actor, announcement.building_id)
    if (
        announcement.state != Announcement.State.PUBLISHED
        or announcement.revision != expected_revision
    ):
        raise AnnouncementConflict()

    announcement.revision += 1
    announcement.state = Announcement.State.WITHDRAWN
    announcement.withdrawn_at = timezone.now()
    announcement.updated_by = actor
    announcement.save()
    NotificationDelivery.objects.filter(
        building_id=announcement.building_id,
        event_key=in_app_event_key(announcement.id),
        channel=NotificationDelivery.Channel.IN_APP,
    ).delete()
    for recipient in _active_residents(announcement.building_id):
        _queue_push(announcement, recipient, "withdrawn")
    record_audit(
        actor=actor,
        membership=membership,
        action="announcement.withdrawn",
        target_type="Announcement",
        target_id=str(announcement.id),
        result="accepted",
        metadata={"announcement_id": announcement.id, "revision": announcement.revision},
    )
    return announcement
