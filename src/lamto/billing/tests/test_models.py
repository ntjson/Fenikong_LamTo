import pytest
from django.db import IntegrityError

from lamto.accounts.models import Building, ResidentOccupancy, Unit, User
from lamto.billing.models import Bill
from lamto.documents.models import Document, DocumentVersion


pytestmark = pytest.mark.django_db


def _bill_document(building):
    document = Document.objects.create(building=building, kind=Document.Kind.INVOICE)
    return DocumentVersion.objects.create(
        document=document,
        version=1,
        storage_key=f"k/{document.pk}",
        provider_version_id="v",
        filename="bill.pdf",
        content_type="application/pdf",
        byte_size=10,
        sha256="0" * 64,
        uploader=User.objects.create_user(email="up@x.test", password="pw"),
    )


def test_bill_defaults_and_reference_are_populated():
    building = Building.objects.create(name="Tower A")
    unit = Unit.objects.create(building=building, label="101")
    resident = User.objects.create_user(email="r@x.test", password="pw")
    ResidentOccupancy.objects.create(user=resident, unit=unit)
    bill = Bill.objects.create(
        building=building,
        resident=resident,
        title="Phí quản lý 07/2026",
        amount_vnd=250000,
        document=_bill_document(building),
        issued_by=resident,
    )
    assert bill.status == Bill.Status.ISSUED
    assert bill.payment_source == ""
    assert len(bill.reference) >= 16
    assert Bill.objects.get(pk=bill.pk).reference == bill.reference


def test_amount_must_be_positive():
    building = Building.objects.create(name="Tower A")
    resident = User.objects.create_user(email="r@x.test", password="pw")
    with pytest.raises(IntegrityError):
        Bill.objects.create(
            building=building,
            resident=resident,
            title="Bad",
            amount_vnd=0,
            document=_bill_document(building),
            issued_by=resident,
        )
