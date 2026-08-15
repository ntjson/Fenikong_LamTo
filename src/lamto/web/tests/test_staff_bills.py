import time
import tempfile
from xml.etree import ElementTree

import pytest
import qrcode
import qrcode.image.svg
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import storages
from django.test import override_settings
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex

from lamto.accounts.models import (
    Building,
    ManagementMembership,
    ResidentOccupancy,
    Unit,
    User,
)
from lamto.accounts.security import RECENT_REAUTH_KEY
from lamto.billing.models import Bill
from lamto.billing.services import BillError, confirm_payment, issue_bill
from lamto.documents.models import Document, DocumentVersion
from lamto.notifications.models import NotificationDelivery
from lamto.web import bill_views


pytestmark = pytest.mark.django_db

_TEMP = tempfile.mkdtemp(prefix="lamto-bills-")
_STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _TEMP}},
    "private": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _TEMP}},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


def setup_manager(client, name="Tower A"):
    building = Building.objects.create(name=name)
    manager = User.objects.create_user(email="manager@x.test", password="secret")
    ManagementMembership.objects.create(user=manager, building=building)
    client.force_login(manager)
    device = TOTPDevice.objects.create(
        user=manager, name="t", confirmed=True, key=random_hex()
    )
    session = client.session
    session[DEVICE_ID_SESSION_KEY] = device.persistent_id
    session[RECENT_REAUTH_KEY] = time.time()
    session.save()
    return building, manager


def _pdf():
    return SimpleUploadedFile(
        "bill.pdf", b"%PDF-1.4\n" + b"0" * 32, content_type="application/pdf"
    )


@override_settings(PUSH_ENABLED=False, STORAGES=_STORAGES)
def test_issue_creates_bill_and_delivery(client, monkeypatch):
    monkeypatch.setattr("lamto.web.staff_documents.scan_with_clamav", lambda _file: True)
    building, _manager = setup_manager(client)
    unit = Unit.objects.create(building=building, label="101")
    resident = User.objects.create_user(email="r@x.test", password="pw")
    ResidentOccupancy.objects.create(user=resident, unit=unit)

    response = client.post(
        reverse("web:staff-bill-create"),
        {
            "resident": resident.pk,
            "title": "Phí 07/2026",
            "amount_vnd": "250000",
            "note": "Hạn 25/07",
            "document": _pdf(),
        },
    )

    assert response.status_code == 302, response.context["form"].errors.as_json()
    bill = Bill.objects.get()
    assert (bill.resident_id, bill.amount_vnd, bill.status) == (
        resident.pk,
        250000,
        Bill.Status.ISSUED,
    )
    assert (
        NotificationDelivery.objects.filter(
            recipient=resident, channel=NotificationDelivery.Channel.IN_APP
        ).count()
        == 1
    )


def test_cross_building_resident_is_rejected(client):
    setup_manager(client)
    other = Building.objects.create(name="Tower B")
    other_unit = Unit.objects.create(building=other, label="9")
    stranger = User.objects.create_user(email="s@x.test", password="pw")
    ResidentOccupancy.objects.create(user=stranger, unit=other_unit)

    response = client.post(
        reverse("web:staff-bill-create"),
        {
            "resident": stranger.pk,
            "title": "x",
            "amount_vnd": "1000",
            "document": _pdf(),
        },
    )

    assert response.status_code == 200
    assert not Bill.objects.exists()


@override_settings(PUSH_ENABLED=False, STORAGES=_STORAGES)
def test_issue_failure_rolls_back_upload_and_deletes_blob(
    client, monkeypatch
):
    monkeypatch.setattr("lamto.web.staff_documents.scan_with_clamav", lambda _file: True)
    building, _manager = setup_manager(client)
    unit = Unit.objects.create(building=building, label="101")
    resident = User.objects.create_user(email="r@x.test", password="pw")
    ResidentOccupancy.objects.create(user=resident, unit=unit)
    real_issue_bill = bill_views.issue_bill
    real_upload_document = bill_views.upload_document
    uploaded = []

    def record_upload(*args, **kwargs):
        version = real_upload_document(*args, **kwargs)
        uploaded.append(version.storage_key)
        return version

    def fail_after_issue(*args, **kwargs):
        real_issue_bill(*args, **kwargs)
        raise BillError("Injected issuance failure.")

    monkeypatch.setattr(bill_views, "upload_document", record_upload)
    monkeypatch.setattr(bill_views, "issue_bill", fail_after_issue)

    response = client.post(
        reverse("web:staff-bill-create"),
        {
            "resident": resident.pk,
            "title": "Rollback",
            "amount_vnd": "1000",
            "document": _pdf(),
        },
    )

    assert response.status_code == 200
    assert b"Injected issuance failure." in response.content
    assert not Document.objects.exists()
    assert not DocumentVersion.objects.exists()
    assert not Bill.objects.exists()
    assert not NotificationDelivery.objects.exists()
    assert len(uploaded) == 1
    assert not storages["private"].exists(uploaded[0])


def test_resident_choices_are_active_building_scoped_and_deduplicated(client):
    building, _manager = setup_manager(client)
    first_unit = Unit.objects.create(building=building, label="101")
    second_unit = Unit.objects.create(building=building, label="102")
    active = User.objects.create_user(email="active@x.test", password="pw")
    inactive = User.objects.create_user(email="inactive@x.test", password="pw")
    ResidentOccupancy.objects.create(user=active, unit=first_unit)
    ResidentOccupancy.objects.create(user=active, unit=second_unit)
    ResidentOccupancy.objects.create(user=inactive, unit=first_unit, active=False)
    other = Building.objects.create(name="Tower B")
    other_unit = Unit.objects.create(building=other, label="9")
    outsider = User.objects.create_user(email="other@x.test", password="pw")
    ResidentOccupancy.objects.create(user=outsider, unit=other_unit)

    response = client.get(reverse("web:staff-bill-create"))

    assert list(response.context["form"].fields["resident"].choices) == [
        (str(active.pk), "active@x.test · 101")
    ]


def _document(building, manager, suffix):
    document = Document.objects.create(
        building=building, kind=Document.Kind.RESIDENT_BILL
    )
    return DocumentVersion.objects.create(
        document=document,
        version=1,
        storage_key=f"bills/{suffix}",
        provider_version_id=suffix,
        filename=f"{suffix}.pdf",
        content_type="application/pdf",
        byte_size=1,
        sha256=suffix.ljust(64, "0"),
        uploader=manager,
    )


def _issue(building, manager, resident, suffix="detail"):
    return issue_bill(
        manager,
        building.pk,
        resident.pk,
        title="Phí 07",
        amount_vnd=250000,
        document=_document(building, manager, suffix),
    )


def test_bill_list_is_building_scoped(client):
    building, manager = setup_manager(client)
    unit = Unit.objects.create(building=building, label="101")
    resident = User.objects.create_user(email="resident@x.test", password="pw")
    ResidentOccupancy.objects.create(user=resident, unit=unit)
    visible = Bill.objects.create(
        building=building,
        resident=resident,
        title="Visible bill",
        amount_vnd=1000,
        document=_document(building, manager, "visible"),
        issued_by=manager,
    )
    other = Building.objects.create(name="Tower B")
    hidden = Bill.objects.create(
        building=other,
        resident=resident,
        title="Hidden bill",
        amount_vnd=2000,
        document=_document(other, manager, "hidden"),
        issued_by=manager,
    )

    response = client.get(reverse("web:staff-bill-list"))

    assert list(response.context["bills"]) == [visible]
    assert visible.title.encode() in response.content
    assert hidden.title.encode() not in response.content


def test_bill_list_rows_navigate_to_detail(client):
    building, manager = setup_manager(client)
    unit = Unit.objects.create(building=building, label="101")
    resident = User.objects.create_user(email="resident@x.test", password="pw")
    ResidentOccupancy.objects.create(user=resident, unit=unit)
    bill = _issue(building, manager, resident, "list-link")
    detail_url = reverse("web:staff-bill-detail", args=[bill.pk])

    response = client.get(reverse("web:staff-bill-list"))

    assert f'<a class="task-row" href="{detail_url}">'.encode() in response.content
    assert client.get(detail_url).status_code == 200


def test_bill_amounts_use_grouped_vnd_format(client):
    building, manager = setup_manager(client)
    unit = Unit.objects.create(building=building, label="101")
    resident = User.objects.create_user(email="resident@x.test", password="pw")
    ResidentOccupancy.objects.create(user=resident, unit=unit)
    bill = _issue(building, manager, resident, "vnd-format")

    listing = client.get(reverse("web:staff-bill-list"))
    detail = client.get(reverse("web:staff-bill-detail", args=[bill.pk]))

    assert b'<span class="task-amount">250.000 VND</span>' in listing.content
    assert b"250.000 VND" in detail.content


def test_bill_qr_svg_encodes_lamto_bill_payload():
    from lamto.billing.qr import bill_qr_svg

    expected = qrcode.make(
        "lamto-bill:bill-reference",
        image_factory=qrcode.image.svg.SvgPathImage,
        box_size=10,
        border=2,
    ).to_string()

    actual_path = ElementTree.fromstring(bill_qr_svg("bill-reference")).find(
        "{http://www.w3.org/2000/svg}path"
    )
    expected_path = ElementTree.fromstring(expected).find(
        "{http://www.w3.org/2000/svg}path"
    )

    assert actual_path is not None
    assert expected_path is not None
    assert actual_path.attrib["d"] == expected_path.attrib["d"]


def test_detail_shows_qr_and_honest_resident_reported_copy_when_paid(client):
    building, manager = setup_manager(client)
    unit = Unit.objects.create(building=building, label="101")
    resident = User.objects.create_user(email="r@x.test", password="pw")
    ResidentOccupancy.objects.create(user=resident, unit=unit)
    bill = _issue(building, manager, resident)

    response = client.get(reverse("web:staff-bill-detail", args=[bill.pk]))

    assert response.status_code == 200
    assert b"<svg" in response.content

    confirm_payment(
        bill,
        source=Bill.PaymentSource.SELF_ATTESTED_DEMO,
        actor=resident,
        reference=bill.reference,
    )
    paid = client.get(reverse("web:staff-bill-detail", args=[bill.pk]))

    paid_body = paid.content.decode().lower()
    assert "resident-reported" in paid_body or "cư dân tự báo" in paid_body
    assert "not bank-verified" in paid_body or "chưa xác minh ngân hàng" in paid_body


def test_void_marks_bill_void(client):
    building, manager = setup_manager(client)
    unit = Unit.objects.create(building=building, label="101")
    resident = User.objects.create_user(email="r@x.test", password="pw")
    ResidentOccupancy.objects.create(user=resident, unit=unit)
    bill = _issue(building, manager, resident)

    response = client.post(
        reverse("web:staff-bill-void", args=[bill.pk]),
        {"reason": "Issued in error", "confirm": "on"},
    )

    assert response.status_code == 302
    bill.refresh_from_db()
    assert bill.status == Bill.Status.VOID


def test_void_requires_in_page_confirmation(client):
    building, manager = setup_manager(client)
    unit = Unit.objects.create(building=building, label="101")
    resident = User.objects.create_user(email="confirm@x.test", password="pw")
    ResidentOccupancy.objects.create(user=resident, unit=unit)
    bill = _issue(building, manager, resident, "confirm")

    response = client.post(
        reverse("web:staff-bill-void", args=[bill.pk]),
        {"reason": "Issued in error"},
    )

    assert response.status_code == 200
    assert b"confirm" in response.content.lower()
    assert b'id="id_confirm-error"' in response.content
    assert b'aria-describedby="id_confirm-error"' in response.content
    assert b"onsubmit=" not in response.content
    bill.refresh_from_db()
    assert bill.status == Bill.Status.ISSUED


def test_void_confirmation_renders_vietnamese_catalogue(client):
    building, manager = setup_manager(client)
    unit = Unit.objects.create(building=building, label="101")
    resident = User.objects.create_user(email="vi@x.test", password="pw")
    ResidentOccupancy.objects.create(user=resident, unit=unit)
    bill = _issue(building, manager, resident, "vi-confirm")
    client.cookies[settings.LANGUAGE_COOKIE_NAME] = "vi"

    response = client.get(reverse("web:staff-bill-detail", args=[bill.pk]))

    assert "Việc hủy sẽ đóng hóa đơn và không thể hoàn tác.".encode() in response.content
    assert "Tôi hiểu rằng việc hủy hóa đơn này không thể hoàn tác.".encode() in response.content


def test_bill_detail_and_void_are_building_scoped(client):
    building, manager = setup_manager(client)
    other = Building.objects.create(name="Tower B")
    unit = Unit.objects.create(building=other, label="9")
    resident = User.objects.create_user(email="other@x.test", password="pw")
    ResidentOccupancy.objects.create(user=resident, unit=unit)
    bill = Bill.objects.create(
        building=other,
        resident=resident,
        title="Other bill",
        amount_vnd=250000,
        document=_document(other, manager, "other"),
        issued_by=manager,
    )

    detail = client.get(reverse("web:staff-bill-detail", args=[bill.pk]))
    void = client.post(
        reverse("web:staff-bill-void", args=[bill.pk]),
        {"reason": "Not ours", "confirm": "on"},
    )

    assert detail.status_code == 404
    assert void.status_code == 404
    bill.refresh_from_db()
    assert bill.status == Bill.Status.ISSUED
