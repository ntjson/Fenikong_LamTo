import pytest
from django.test import override_settings

from lamto.accounts.models import Building, ManagementMembership, ResidentOccupancy, Unit, User
from lamto.audit.models import AuditEvent
from lamto.billing.models import Bill
from lamto.billing.services import (
    BillActorError,
    BillReferenceError,
    BillVoidedError,
    confirm_payment,
    issue_bill,
)
from lamto.documents.models import Document, DocumentVersion


pytestmark = pytest.mark.django_db


def _bill():
    building = Building.objects.create(name="Tower A")
    manager = User.objects.create_user(email="m@x.test", password="pw")
    ManagementMembership.objects.create(user=manager, building=building)
    unit = Unit.objects.create(building=building, label="101")
    resident = User.objects.create_user(email="r@x.test", password="pw")
    ResidentOccupancy.objects.create(user=resident, unit=unit)
    document = Document.objects.create(building=building, kind=Document.Kind.RESIDENT_BILL)
    version = DocumentVersion.objects.create(
        document=document,
        version=1,
        storage_key=f"k/{document.pk}",
        provider_version_id="v",
        filename="b.pdf",
        content_type="application/pdf",
        byte_size=1,
        sha256="0" * 64,
        uploader=manager,
    )
    bill = issue_bill(
        manager,
        building.pk,
        resident.pk,
        title="x",
        amount_vnd=1000,
        document=version,
    )
    return bill, resident


def test_confirm_records_payment_and_is_idempotent():
    bill, resident = _bill()
    src = Bill.PaymentSource.SELF_ATTESTED_DEMO
    result = confirm_payment(bill, source=src, actor=resident, reference=bill.reference)
    assert result.status == Bill.Status.PAID
    assert result.payment_source == src
    assert result.paid_confirmed_by_id == resident.pk
    assert (
        AuditEvent.objects.filter(
            target_type="Bill",
            target_id=str(bill.pk),
            action="bill.payment_recorded",
        ).count()
        == 1
    )
    again = confirm_payment(bill, source=src, actor=resident, reference=bill.reference)
    assert again.status == Bill.Status.PAID
    assert AuditEvent.objects.filter(action="bill.payment_recorded").count() == 1


def test_confirm_rejects_wrong_reference():
    bill, resident = _bill()
    with pytest.raises(BillReferenceError):
        confirm_payment(
            bill,
            source=Bill.PaymentSource.SELF_ATTESTED_DEMO,
            actor=resident,
            reference="not-it",
        )
    bill.refresh_from_db()
    assert bill.status == Bill.Status.ISSUED


@override_settings(LANGUAGE_CODE="en-us")  # asserts English source strings
def test_self_attested_confirmation_rejects_another_actor():
    bill, _resident = _bill()
    stranger = User.objects.create_user(email="stranger@x.test", password="pw")

    with pytest.raises(BillActorError, match="bill resident"):
        confirm_payment(
            bill,
            source=Bill.PaymentSource.SELF_ATTESTED_DEMO,
            actor=stranger,
            reference=bill.reference,
        )

    bill.refresh_from_db()
    assert bill.status == Bill.Status.ISSUED


def test_confirm_rejects_wrong_reference_when_already_paid():
    bill, resident = _bill()
    source = Bill.PaymentSource.SELF_ATTESTED_DEMO
    confirm_payment(bill, source=source, actor=resident, reference=bill.reference)

    with pytest.raises(BillReferenceError):
        confirm_payment(bill, source=source, actor=resident, reference="not-it")


def test_confirm_rejects_void_bill():
    bill, resident = _bill()
    bill.status = Bill.Status.VOID
    bill.save(update_fields=["status"])

    with pytest.raises(BillVoidedError):
        confirm_payment(
            bill,
            source=Bill.PaymentSource.SELF_ATTESTED_DEMO,
            actor=resident,
            reference=bill.reference,
        )
