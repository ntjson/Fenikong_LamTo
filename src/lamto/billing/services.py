from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from lamto.accounts.models import ResidentOccupancy
from lamto.accounts.services import require_management
from lamto.audit.services import record_audit
from lamto.billing.models import Bill
from lamto.documents.models import Document
from lamto.notifications.models import NotificationDelivery
from lamto.notifications.services import EVENT_BILL_ISSUED, queue_notification
from django.utils.translation import gettext_lazy as _


class BillError(Exception):
    pass


class BillVoidedError(BillError):
    pass


class BillReferenceError(BillError):
    pass


class BillActorError(BillError):
    pass


def in_app_event_key(bill_id: int) -> str:
    return f"{EVENT_BILL_ISSUED}:bill:{bill_id}"


def push_event_key(bill_id: int) -> str:
    return f"{EVENT_BILL_ISSUED}:bill:{bill_id}:issued"


@transaction.atomic
def issue_bill(
    actor,
    building_id,
    resident_id,
    *,
    title,
    amount_vnd,
    document,
    note="",
    period="",
    due_date=None,
) -> Bill:
    membership = require_management(actor, building_id)
    resident = get_user_model().objects.filter(pk=resident_id).first()
    if resident is None:
        raise BillError(_("Resident does not exist."))
    if not ResidentOccupancy.objects.filter(
        user_id=resident_id,
        active=True,
        unit__building_id=building_id,
    ).exists():
        raise BillError(_("Resident has no active occupancy in this building."))
    if document.document.kind != Document.Kind.RESIDENT_BILL:
        raise BillError(_("Document must be a resident bill."))
    if document.document.building_id != building_id:
        raise BillError(_("Document must belong to the target building."))

    bill = Bill.objects.create(
        building_id=building_id,
        resident=resident,
        title=title,
        note=note,
        period=period,
        due_date=due_date,
        amount_vnd=amount_vnd,
        document=document,
        issued_by=actor,
    )
    subject = f"{title} — {amount_vnd:,}đ"
    queue_notification(
        recipient=resident,
        building=bill.building,
        event_code=EVENT_BILL_ISSUED,
        event_key=in_app_event_key(bill.pk),
        subject=subject,
        body=note,
        channels=[NotificationDelivery.Channel.IN_APP],
    )
    queue_notification(
        recipient=resident,
        building=bill.building,
        event_code=EVENT_BILL_ISSUED,
        event_key=push_event_key(bill.pk),
        subject=subject,
        body=note,
        channels=[NotificationDelivery.Channel.PUSH],
    )
    NotificationDelivery.objects.filter(
        event_key=in_app_event_key(bill.pk),
        channel=NotificationDelivery.Channel.IN_APP,
    ).update(status=NotificationDelivery.Status.AVAILABLE)
    record_audit(
        actor=actor,
        membership=membership,
        action="bill.issued",
        target_type="Bill",
        target_id=str(bill.pk),
        result="accepted",
        metadata={"bill_id": bill.pk, "amount_vnd": amount_vnd},
    )
    return bill


@transaction.atomic
def confirm_payment(bill, *, source, actor, reference) -> Bill:
    locked = Bill.objects.select_for_update().get(pk=bill.pk)
    if locked.status == Bill.Status.VOID:
        raise BillVoidedError()
    if reference != locked.reference:
        raise BillReferenceError()
    if (
        source == Bill.PaymentSource.SELF_ATTESTED_DEMO
        and actor.pk != locked.resident_id
    ):
        raise BillActorError(
            _("Self-attested payment must be confirmed by the bill resident.")
        )
    if locked.status == Bill.Status.PAID:
        return locked
    locked.status = Bill.Status.PAID
    locked.payment_source = source
    locked.paid_at = timezone.now()
    locked.paid_confirmed_by = actor
    locked.save(
        update_fields=["status", "payment_source", "paid_at", "paid_confirmed_by"]
    )
    record_audit(
        actor=actor,
        membership=None,
        action="bill.payment_recorded",
        target_type="Bill",
        target_id=str(locked.pk),
        result="accepted",
        metadata={"bill_id": locked.pk, "source": source},
    )
    return locked


@transaction.atomic
def void_bill(actor, bill_id, *, reason) -> Bill:
    reason = (reason or "").strip()
    if not reason:
        raise BillError(_("A void reason is required."))
    locked = Bill.objects.select_for_update().get(pk=bill_id)
    membership = require_management(actor, locked.building_id)
    if locked.status != Bill.Status.ISSUED:
        raise BillError(_("Only an issued bill can be voided."))
    locked.status = Bill.Status.VOID
    locked.void_by = actor
    locked.void_at = timezone.now()
    locked.void_reason = reason
    locked.save(update_fields=["status", "void_by", "void_at", "void_reason"])
    NotificationDelivery.objects.filter(
        event_key=in_app_event_key(locked.pk),
        channel=NotificationDelivery.Channel.IN_APP,
    ).delete()
    record_audit(
        actor=actor,
        membership=membership,
        action="bill.voided",
        target_type="Bill",
        target_id=str(locked.pk),
        result="accepted",
        metadata={"bill_id": locked.pk},
    )
    return locked
