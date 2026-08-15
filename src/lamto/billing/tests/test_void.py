import pytest

from lamto.accounts.models import (
    Building,
    ManagementMembership,
    ResidentOccupancy,
    Unit,
    User,
)
from lamto.billing.models import Bill
from lamto.billing.services import (
    BillError,
    BillVoidedError,
    confirm_payment,
    in_app_event_key,
    issue_bill,
    void_bill,
)
from lamto.documents.models import Document, DocumentVersion
from lamto.notifications.models import NotificationDelivery


pytestmark = pytest.mark.django_db


def _setup():
    building = Building.objects.create(name="Tower A")
    manager = User.objects.create_user(email="m@x.test", password="pw")
    ManagementMembership.objects.create(user=manager, building=building)
    unit = Unit.objects.create(building=building, label="101")
    resident = User.objects.create_user(email="r@x.test", password="pw")
    ResidentOccupancy.objects.create(user=resident, unit=unit)
    document = Document.objects.create(
        building=building, kind=Document.Kind.RESIDENT_BILL
    )
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
    return manager, resident, bill


def test_void_hides_in_app_and_blocks_payment():
    manager, resident, bill = _setup()
    void_bill(manager, bill.pk, reason="Issued in error")
    bill.refresh_from_db()

    assert bill.status == Bill.Status.VOID
    assert bill.void_reason == "Issued in error"
    assert not NotificationDelivery.objects.filter(
        channel=NotificationDelivery.Channel.IN_APP,
        event_key=in_app_event_key(bill.pk),
    ).exists()
    with pytest.raises(BillVoidedError):
        confirm_payment(
            bill,
            source=Bill.PaymentSource.SELF_ATTESTED_DEMO,
            actor=resident,
            reference=bill.reference,
        )


def test_void_requires_reason():
    manager, _resident, bill = _setup()

    with pytest.raises(BillError):
        void_bill(manager, bill.pk, reason="  ")
