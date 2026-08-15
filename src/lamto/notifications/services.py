"""Durable notification queue and delivery helpers.

Business services must call ``queue_notification`` via ``transaction.on_commit``
so notification failures never roll back domain state.
"""

from __future__ import annotations

from datetime import timedelta

from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import NotificationDelivery, NotificationPreference


# Material event codes used by domain services and preference forms.
EVENT_REPORT_RECEIPT = "report.receipt"
EVENT_TRIAGE_STATUS = "triage.status"
EVENT_CASE_STATUS = "case.status"
EVENT_WORK_ASSIGNED = "work.assigned"
EVENT_DEADLINE_RISK = "work.deadline_risk"
EVENT_WORK_ACCEPTED = "work.accepted"
EVENT_WORK_COMPLETED = "work.completed"
EVENT_SETTLEMENT_RECORDED = "settlement.recorded"
EVENT_PAYMENT_REJECTED = "payment.rejected"
EVENT_PUBLICATION = "ledger.publication"
EVENT_INTEGRITY_MISMATCH = "integrity.mismatch"
EVENT_QUARANTINED_UPLOAD = "document.quarantined"
EVENT_OUTBOX_FAILED = "outbox.failed"
EVENT_ANNOUNCEMENT = "building.announcement"
EVENT_BILL_ISSUED = "building.bill_issued"

# In-app notices for these codes cannot be disabled.
REQUIRED_IN_APP_EVENT_CODES = frozenset(
    {
        EVENT_REPORT_RECEIPT,
        EVENT_TRIAGE_STATUS,
        EVENT_CASE_STATUS,
        EVENT_WORK_ASSIGNED,
        EVENT_DEADLINE_RISK,
        EVENT_WORK_ACCEPTED,
        EVENT_SETTLEMENT_RECORDED,
        EVENT_PAYMENT_REJECTED,
        EVENT_PUBLICATION,
        EVENT_INTEGRITY_MISMATCH,
        EVENT_QUARANTINED_UPLOAD,
        EVENT_OUTBOX_FAILED,
    }
)

PREFERENCE_EVENT_CHOICES = (
    (EVENT_ANNOUNCEMENT, "Building announcements"),
    (EVENT_BILL_ISSUED, "Building bills"),
    (EVENT_REPORT_RECEIPT, "Report receipt"),
    (EVENT_TRIAGE_STATUS, "Triage / case status"),
    (EVENT_WORK_COMPLETED, "Work completed (rate prompt)"),
    (EVENT_WORK_ASSIGNED, "Work assignment"),
    (EVENT_DEADLINE_RISK, "Deadline risk"),
    (EVENT_SETTLEMENT_RECORDED, "Settlement actions"),
    (EVENT_PUBLICATION, "Ledger publication"),
    (EVENT_INTEGRITY_MISMATCH, "Integrity mismatch"),
)

# Resident-relevant push events only (spec 7.4). No staff push in Phase 1.
RESIDENT_PUSH_EVENT_CODES = frozenset(
    {
        EVENT_REPORT_RECEIPT,
        EVENT_TRIAGE_STATUS,
        EVENT_WORK_COMPLETED,
        EVENT_PUBLICATION,
        EVENT_ANNOUNCEMENT,
        EVENT_BILL_ISSUED,
    }
)

DEFAULT_CHANNELS = (
    NotificationDelivery.Channel.IN_APP,
    NotificationDelivery.Channel.EMAIL,
    NotificationDelivery.Channel.PUSH,
)

MAX_EMAIL_ATTEMPTS = 8
MAX_PUSH_ATTEMPTS = 5
BASE_BACKOFF_SECONDS = 30

# Structured suppress markers: do not count as true FCM success in ops metrics.
PUSH_SUPPRESSED_PREFIX = "suppressed:"


def email_enabled_for(user, event_code: str) -> bool:
    pref = NotificationPreference.objects.filter(
        user=user, event_code=event_code
    ).first()
    if pref is None:
        return True
    return bool(pref.email_enabled)


def push_enabled_for(user, event_code: str) -> bool:
    pref = NotificationPreference.objects.filter(user=user, event_code=event_code).first()
    if pref is None:
        return True  # default on once OS permission exists (spec 7.5)
    return bool(pref.push_enabled)


def queue_notification(
    recipient,
    event_key: str,
    subject: str,
    body: str,
    channels=None,
    *,
    event_code: str = "",
    building=None,
) -> list[NotificationDelivery]:
    """Idempotently enqueue delivery rows for the given channels.

    Unique on (recipient, event_key, channel). Returns existing rows on conflict.
    """
    if channels is None:
        channels = list(DEFAULT_CHANNELS)
    building_id = getattr(building, "pk", building)
    created: list[NotificationDelivery] = []
    for channel in channels:
        if channel == NotificationDelivery.Channel.EMAIL:
            code = event_code or _event_code_from_key(event_key)
            if not email_enabled_for(recipient, code):
                continue
        if channel == NotificationDelivery.Channel.PUSH:
            from django.conf import settings
            from lamto.notifications.models import Device

            code = event_code or _event_code_from_key(event_key)
            if not getattr(settings, "PUSH_ENABLED", False):
                continue
            if code not in RESIDENT_PUSH_EVENT_CODES:
                continue
            if not push_enabled_for(recipient, code):
                continue
            if not Device.objects.filter(user=recipient, active=True).exists():
                continue
        delivery, _ = NotificationDelivery.objects.get_or_create(
            recipient=recipient,
            event_key=event_key,
            channel=channel,
            defaults={
                "subject": subject,
                "body": body,
                "event_code": event_code or _event_code_from_key(event_key),
                "status": NotificationDelivery.Status.PENDING,
                "building_id": building_id,
            },
        )
        created.append(delivery)
    return created


def queue_notification_after_commit(
    recipient,
    event_key: str,
    subject: str,
    body: str,
    channels=None,
    *,
    event_code: str = "",
    building=None,
):
    """Schedule queue_notification after the current transaction commits."""
    recipient_id = getattr(recipient, "pk", recipient)
    building_id = getattr(building, "pk", building)

    def _enqueue():
        from django.contrib.auth import get_user_model

        user = get_user_model().objects.filter(pk=recipient_id).first()
        if user is None:
            return
        try:
            queue_notification(
                user,
                event_key,
                subject,
                body,
                channels,
                event_code=event_code,
                building=building_id,
            )
        except Exception:
            # Never raise into business path; failures are isolated to the worker.
            return

    transaction.on_commit(_enqueue)


def _event_code_from_key(event_key: str) -> str:
    # event_key format: "{code}:{entity}:{id}" or plain code
    if ":" in event_key:
        return event_key.split(":", 1)[0]
    return event_key


def claim_pending_deliveries(*, limit: int = 50) -> list[NotificationDelivery]:
    """Claim due pending/failed email or pending in-app rows with skip_locked."""
    now = timezone.now()
    claimed: list[NotificationDelivery] = []
    with transaction.atomic():
        qs = (
            NotificationDelivery.objects.select_for_update(skip_locked=True)
            .filter(
                Q(status=NotificationDelivery.Status.PENDING)
                | Q(
                    status=NotificationDelivery.Status.FAILED,
                    next_retry_at__lte=now,
                )
            )
            .order_by("created_at", "pk")[:limit]
        )
        for row in qs:
            claimed.append(row)
    return claimed


def process_delivery(delivery: NotificationDelivery) -> NotificationDelivery:
    """Process a single claimed delivery row."""
    with transaction.atomic():
        locked = (
            NotificationDelivery.objects.select_for_update()
            .filter(pk=delivery.pk)
            .first()
        )
        if locked is None:
            return delivery
        if locked.status in {
            NotificationDelivery.Status.SENT,
            NotificationDelivery.Status.AVAILABLE,
            NotificationDelivery.Status.DEAD,
        }:
            return locked

        if locked.channel == NotificationDelivery.Channel.IN_APP:
            locked.status = NotificationDelivery.Status.AVAILABLE
            locked.attempts += 1
            locked.last_error = ""
            locked.save(
                update_fields=["status", "attempts", "last_error", "updated_at"]
            )
            return locked

        if locked.channel == NotificationDelivery.Channel.PUSH:
            return _process_push_delivery(locked)

        # EMAIL
        locked.attempts += 1
        try:
            send_mail(
                locked.subject,
                locked.body,
                None,
                [locked.recipient.email],
                fail_silently=False,
            )
        except Exception as exc:
            locked.last_error = str(exc)[:2000]
            if locked.attempts >= MAX_EMAIL_ATTEMPTS:
                locked.status = NotificationDelivery.Status.DEAD
                locked.next_retry_at = None
            else:
                locked.status = NotificationDelivery.Status.FAILED
                backoff = BASE_BACKOFF_SECONDS * (2 ** min(locked.attempts - 1, 6))
                locked.next_retry_at = timezone.now() + timedelta(seconds=backoff)
            locked.save(
                update_fields=[
                    "status",
                    "attempts",
                    "last_error",
                    "next_retry_at",
                    "updated_at",
                ]
            )
            return locked

        locked.status = NotificationDelivery.Status.SENT
        locked.last_error = ""
        locked.next_retry_at = None
        locked.save(
            update_fields=[
                "status",
                "attempts",
                "last_error",
                "next_retry_at",
                "updated_at",
            ]
        )
        return locked


def process_due_notifications(*, limit: int = 50) -> list[NotificationDelivery]:
    """Claim and process a bounded batch of due notification deliveries."""
    results: list[NotificationDelivery] = []
    for delivery in claim_pending_deliveries(limit=limit):
        results.append(process_delivery(delivery))
    return results


def notify_users(
    users,
    *,
    event_key: str,
    subject: str,
    body: str,
    event_code: str,
    building=None,
):
    """Queue notifications for many users after commit (deduped by id)."""
    seen = set()
    for user in users:
        if user is None:
            continue
        uid = getattr(user, "pk", None)
        if uid is None or uid in seen:
            continue
        seen.add(uid)
        queue_notification_after_commit(
            user,
            event_key=event_key,
            subject=subject,
            body=body,
            event_code=event_code,
            building=building,
        )


def resident_feed(user, building_id):
    """Resident in-app feed for one building (spec 3.3): available IN_APP notices,
    plus legacy null-building rows, newest first."""
    return (
        NotificationDelivery.objects.filter(
            recipient=user,
            channel=NotificationDelivery.Channel.IN_APP,
            status=NotificationDelivery.Status.AVAILABLE,
        )
        .filter(Q(building_id=building_id) | Q(building_id__isnull=True))
        .order_by("-created_at", "-pk")
    )


def mark_notification_read(user, delivery_id) -> int:
    """Mark one of the caller's IN_APP notices read. Returns rows updated (0/1)."""
    return (
        NotificationDelivery.objects.filter(
            pk=delivery_id,
            recipient=user,
            channel=NotificationDelivery.Channel.IN_APP,
            read_at__isnull=True,
        ).update(read_at=timezone.now())
    )


def _recipient_can_receive_push(delivery) -> bool:
    """Send-time revalidation (spec 7.3): user active + active occupancy in building."""
    from lamto.accounts.tenancy import active_occupancies

    user = delivery.recipient
    if not getattr(user, "is_active", False):
        return False
    if delivery.building_id is None:
        return True
    return active_occupancies(user).filter(unit__building_id=delivery.building_id).exists()


# Categories that collapse on-device and are daily-capped (spec 7.3).
_AGGREGATED_PUSH_CODES = frozenset({EVENT_PUBLICATION})


def _collapse_key(delivery):
    code = delivery.event_code or _event_code_from_key(delivery.event_key)
    if code == EVENT_PUBLICATION and delivery.building_id is not None:
        return f"pub:{delivery.building_id}"
    return None


def _daily_push_cap_reached(delivery) -> bool:
    from django.conf import settings

    code = delivery.event_code or _event_code_from_key(delivery.event_key)
    if code not in _AGGREGATED_PUSH_CODES:
        return False
    cap = getattr(settings, "PUSH_DAILY_CAP_PER_CATEGORY", 10)
    today = timezone.localdate()  # Asia/Ho_Chi_Minh calendar day (settings.TIME_ZONE)
    # Count only true FCM successes (empty last_error), not suppressions.
    sent_today = NotificationDelivery.objects.filter(
        recipient=delivery.recipient,
        channel=NotificationDelivery.Channel.PUSH,
        event_code=code,
        status=NotificationDelivery.Status.SENT,
        last_error="",
        updated_at__date=today,
    ).count()
    return sent_today >= cap


def _process_push_delivery(delivery):
    from lamto.notifications.models import Device
    from lamto.notifications.push import build_push_payload, classify_push_error

    now = timezone.now()
    if not _recipient_can_receive_push(delivery):
        delivery.status = NotificationDelivery.Status.SENT  # non-retryable; in-app feed holds it
        delivery.last_error = f"{PUSH_SUPPRESSED_PREFIX}recipient_ineligible"
        delivery.save(update_fields=["status", "last_error", "updated_at"])
        return delivery

    devices = list(Device.objects.filter(user=delivery.recipient, active=True))
    if not devices:
        delivery.status = NotificationDelivery.Status.SENT
        delivery.last_error = f"{PUSH_SUPPRESSED_PREFIX}no_active_devices"
        delivery.save(update_fields=["status", "last_error", "updated_at"])
        return delivery

    if _daily_push_cap_reached(delivery):
        delivery.status = NotificationDelivery.Status.SENT  # capped; in-app feed holds it
        delivery.last_error = f"{PUSH_SUPPRESSED_PREFIX}daily_cap"
        delivery.save(update_fields=["status", "last_error", "updated_at"])
        return delivery

    title, body, data = build_push_payload(delivery)
    collapse_key = _collapse_key(delivery)
    already_sent = set(delivery.push_sent_device_ids or [])
    any_success = bool(already_sent)
    any_transient = False
    last_error = ""
    for device in devices:
        if device.pk in already_sent:
            # Prior attempt already delivered to this device — do not re-send.
            continue
        try:
            # Module-level send_push so tests can patch lamto.notifications.services.send_push
            send_push(
                device.fcm_token,
                title=title,
                body=body,
                data=data,
                collapse_key=collapse_key,
            )
            already_sent.add(device.pk)
            any_success = True
        except Exception as exc:  # noqa: BLE001 - provider errors are classified below
            if classify_push_error(exc) == "terminal":
                Device.objects.filter(pk=device.pk).update(active=False)
            else:
                any_transient = True
                last_error = str(exc)[:2000]

    delivery.attempts += 1
    delivery.push_sent_device_ids = list(already_sent)
    if any_transient:
        delivery.last_error = last_error
        if delivery.attempts >= MAX_PUSH_ATTEMPTS:
            delivery.status = NotificationDelivery.Status.FAILED
            delivery.next_retry_at = None
        else:
            delivery.status = NotificationDelivery.Status.FAILED
            backoff = BASE_BACKOFF_SECONDS * (2 ** min(delivery.attempts - 1, 6))
            delivery.next_retry_at = now + timedelta(seconds=backoff)
    elif any_success:
        delivery.status = NotificationDelivery.Status.SENT
        delivery.last_error = ""
        delivery.next_retry_at = None
    else:
        # All tokens terminal / dead — not a true FCM success (ops metrics + daily cap).
        delivery.status = NotificationDelivery.Status.SENT
        delivery.last_error = f"{PUSH_SUPPRESSED_PREFIX}all_tokens_terminal"
        delivery.next_retry_at = None
    delivery.save(
        update_fields=[
            "status",
            "attempts",
            "last_error",
            "next_retry_at",
            "push_sent_device_ids",
            "updated_at",
        ]
    )
    return delivery


# Re-export for worker call sites and test patches (avoids circular import at top).
from lamto.notifications.push import send_push  # noqa: E402
