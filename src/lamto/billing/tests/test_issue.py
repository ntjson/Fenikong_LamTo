import pytest
from django.test import override_settings
from django.utils import timezone

from lamto.accounts.models import (
    Building,
    ManagementMembership,
    ResidentOccupancy,
    Unit,
    User,
)
from lamto.audit.models import AuditEvent
from lamto.billing.models import Bill
from lamto.billing.services import BillError, EVENT_BILL_ISSUED, in_app_event_key, issue_bill
from lamto.documents.models import Document, DocumentVersion
from lamto.notifications.models import Device, NotificationDelivery, NotificationPreference


pytestmark = pytest.mark.django_db


def _doc(building, uploader, *, kind=Document.Kind.RESIDENT_BILL):
    document = Document.objects.create(building=building, kind=kind)
    return DocumentVersion.objects.create(
        document=document,
        version=1,
        storage_key=f"k/{document.pk}",
        provider_version_id="v",
        filename="bill.pdf",
        content_type="application/pdf",
        byte_size=10,
        sha256="0" * 64,
        uploader=uploader,
    )


@override_settings(PUSH_ENABLED=True)
def test_issue_bill_targets_only_the_named_resident():
    building = Building.objects.create(name="Tower A")
    manager = User.objects.create_user(email="m@x.test", password="pw")
    ManagementMembership.objects.create(user=manager, building=building)
    unit = Unit.objects.create(building=building, label="101")
    resident = User.objects.create_user(email="r@x.test", password="pw")
    co_resident = User.objects.create_user(email="c@x.test", password="pw")
    ResidentOccupancy.objects.create(user=resident, unit=unit)
    ResidentOccupancy.objects.create(user=co_resident, unit=unit)
    Device.objects.create(
        user=resident,
        install_id="i",
        fcm_token="t",
        platform=Device.Platform.ANDROID,
        last_seen_at=timezone.now(),
    )

    bill = issue_bill(
        manager,
        building.pk,
        resident.pk,
        title="Phí 07/2026",
        amount_vnd=250000,
        document=_doc(building, manager),
    )

    assert bill.status == Bill.Status.ISSUED
    in_app = NotificationDelivery.objects.filter(
        channel=NotificationDelivery.Channel.IN_APP,
        event_key=in_app_event_key(bill.pk),
    )
    assert list(in_app.values_list("recipient_id", flat=True)) == [resident.pk]
    assert in_app.get().status == NotificationDelivery.Status.AVAILABLE
    push = NotificationDelivery.objects.filter(
        channel=NotificationDelivery.Channel.PUSH,
        event_code=EVENT_BILL_ISSUED,
    )
    assert list(push.values_list("recipient_id", flat=True)) == [resident.pk]
    assert not NotificationDelivery.objects.filter(
        channel=NotificationDelivery.Channel.EMAIL,
        event_code=EVENT_BILL_ISSUED,
    ).exists()
    assert AuditEvent.objects.filter(
        target_type="Bill",
        target_id=str(bill.pk),
        action="bill.issued",
    ).exists()


@override_settings(LANGUAGE_CODE="en-us")  # asserts English source strings
def test_issue_bill_rejects_resident_without_active_occupancy():
    building = Building.objects.create(name="Tower A")
    manager = User.objects.create_user(email="m@x.test", password="pw")
    ManagementMembership.objects.create(user=manager, building=building)
    stranger = User.objects.create_user(email="s@x.test", password="pw")
    with pytest.raises(BillError, match="active occupancy"):
        issue_bill(
            manager,
            building.pk,
            stranger.pk,
            title="x",
            amount_vnd=1000,
            document=_doc(building, manager),
        )


@override_settings(LANGUAGE_CODE="en-us")  # asserts English source strings
def test_issue_bill_rejects_missing_resident():
    building = Building.objects.create(name="Tower A")
    manager = User.objects.create_user(email="m@x.test", password="pw")
    ManagementMembership.objects.create(user=manager, building=building)

    with pytest.raises(BillError, match="Resident does not exist"):
        issue_bill(
            manager,
            building.pk,
            999999,
            title="x",
            amount_vnd=1000,
            document=_doc(building, manager),
        )


@override_settings(LANGUAGE_CODE="en-us")  # asserts English source strings
def test_issue_bill_rejects_non_bill_document():
    building = Building.objects.create(name="Tower A")
    manager = User.objects.create_user(email="m@x.test", password="pw")
    ManagementMembership.objects.create(user=manager, building=building)
    unit = Unit.objects.create(building=building, label="101")
    resident = User.objects.create_user(email="r@x.test", password="pw")
    ResidentOccupancy.objects.create(user=resident, unit=unit)

    with pytest.raises(BillError, match="resident bill"):
        issue_bill(
            manager,
            building.pk,
            resident.pk,
            title="x",
            amount_vnd=1000,
            document=_doc(building, manager, kind=Document.Kind.INVOICE),
        )


@override_settings(LANGUAGE_CODE="en-us")  # asserts English source strings
def test_issue_bill_rejects_document_from_another_building():
    building = Building.objects.create(name="Tower A")
    other_building = Building.objects.create(name="Tower B")
    manager = User.objects.create_user(email="m@x.test", password="pw")
    ManagementMembership.objects.create(user=manager, building=building)
    unit = Unit.objects.create(building=building, label="101")
    resident = User.objects.create_user(email="r@x.test", password="pw")
    ResidentOccupancy.objects.create(user=resident, unit=unit)

    with pytest.raises(BillError, match="target building"):
        issue_bill(
            manager,
            building.pk,
            resident.pk,
            title="x",
            amount_vnd=1000,
            document=_doc(other_building, manager),
        )


@override_settings(PUSH_ENABLED=True)
def test_issue_bill_respects_resident_push_opt_out():
    building = Building.objects.create(name="Tower A")
    manager = User.objects.create_user(email="m@x.test", password="pw")
    ManagementMembership.objects.create(user=manager, building=building)
    unit = Unit.objects.create(building=building, label="101")
    resident = User.objects.create_user(email="r@x.test", password="pw")
    ResidentOccupancy.objects.create(user=resident, unit=unit)
    Device.objects.create(
        user=resident,
        install_id="i",
        fcm_token="t",
        platform=Device.Platform.ANDROID,
        last_seen_at=timezone.now(),
    )
    NotificationPreference.objects.create(
        user=resident,
        event_code=EVENT_BILL_ISSUED,
        push_enabled=False,
    )

    bill = issue_bill(
        manager,
        building.pk,
        resident.pk,
        title="x",
        amount_vnd=1000,
        document=_doc(building, manager),
    )

    assert NotificationDelivery.objects.filter(
        recipient=resident,
        channel=NotificationDelivery.Channel.IN_APP,
        event_key=in_app_event_key(bill.pk),
    ).exists()
    assert not NotificationDelivery.objects.filter(
        recipient=resident,
        channel=NotificationDelivery.Channel.PUSH,
        event_code=EVENT_BILL_ISSUED,
    ).exists()
