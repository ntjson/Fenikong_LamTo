import time

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex
from knox.models import AuthToken

from lamto.accounts.models import (
    Building,
    ManagementMembership,
    ResidentOccupancy,
    Unit,
    User,
)
from lamto.accounts.security import RECENT_REAUTH_KEY
from lamto.billing.models import Bill
from lamto.notifications.models import NotificationDelivery


pytestmark = pytest.mark.django_db


@override_settings(PUSH_ENABLED=False)
@override_settings(LANGUAGE_CODE="en-us")  # asserts English source strings
def test_full_bill_lifecycle():
    building = Building.objects.create(name="Tower A")
    manager = User.objects.create_user(email="m@x.test", password="secret")
    ManagementMembership.objects.create(user=manager, building=building)
    unit = Unit.objects.create(building=building, label="101")
    resident = User.objects.create_user(email="r@x.test", password="pw")
    ResidentOccupancy.objects.create(user=resident, unit=unit)
    co_resident = User.objects.create_user(email="co@x.test", password="pw")
    ResidentOccupancy.objects.create(user=co_resident, unit=unit)

    staff = Client()
    staff.force_login(manager)
    device = TOTPDevice.objects.create(
        user=manager, name="t", confirmed=True, key=random_hex()
    )
    session = staff.session
    session[DEVICE_ID_SESSION_KEY] = device.persistent_id
    session[RECENT_REAUTH_KEY] = time.time()
    session.save()

    pdf = SimpleUploadedFile(
        "bill.pdf", b"%PDF-1.4\n" + b"0" * 32, content_type="application/pdf"
    )
    assert staff.post(
        reverse("web:staff-bill-create"),
        {
            "resident": resident.pk,
            "title": "Phí 07/2026",
            "amount_vnd": "250000",
            "document": pdf,
        },
    ).status_code == 302
    bill = Bill.objects.get()
    assert NotificationDelivery.objects.filter(
        recipient=resident, channel=NotificationDelivery.Channel.IN_APP
    ).count() == 1
    assert not NotificationDelivery.objects.filter(recipient=co_resident).exists()

    _instance, token = AuthToken.objects.create(user=resident)
    api = Client()
    auth = {"authorization": f"Token {token}"}
    listing = api.get(reverse("api:bills-list"), headers=auth).json()["results"]
    assert [item["id"] for item in listing] == [bill.pk]
    detail = api.get(reverse("api:bills-detail", args=[bill.pk]), headers=auth)
    assert detail.status_code == 200
    assert "/api/v1/documents/" in detail.json()["document_download_url"]

    _instance, co_token = AuthToken.objects.create(user=co_resident)
    co_auth = {"authorization": f"Token {co_token}"}
    assert api.get(reverse("api:bills-list"), headers=co_auth).json()["results"] == []
    assert (
        api.get(reverse("api:bills-detail", args=[bill.pk]), headers=co_auth).status_code
        == 404
    )

    confirm_url = reverse("api:bills-confirm-payment", args=[bill.pk])
    wrong = api.post(
        confirm_url,
        {"reference": "wrong-reference"},
        content_type="application/json",
        headers=auth,
    )
    assert wrong.status_code == 400
    bill.refresh_from_db()
    assert bill.status == Bill.Status.ISSUED

    paid = api.post(
        confirm_url,
        {"reference": bill.reference},
        content_type="application/json",
        headers=auth,
    )
    assert paid.status_code == 200
    assert paid.json()["status"] == Bill.Status.PAID

    staff_detail = staff.get(reverse("web:staff-bill-detail", args=[bill.pk]))
    body = staff_detail.content.lower()
    assert b"paid" in body
    assert b"resident-reported" in body
    assert b"not bank-verified" in body

    second_pdf = SimpleUploadedFile(
        "b2.pdf", b"%PDF-1.4\n" + b"0" * 32, content_type="application/pdf"
    )
    assert staff.post(
        reverse("web:staff-bill-create"),
        {
            "resident": resident.pk,
            "title": "Void me",
            "amount_vnd": "1000",
            "document": second_pdf,
        },
    ).status_code == 302
    void_target = Bill.objects.exclude(pk=bill.pk).get()
    ids = [
        item["id"]
        for item in api.get(reverse("api:bills-list"), headers=auth).json()["results"]
    ]
    assert void_target.pk in ids
    assert staff.post(
        reverse("web:staff-bill-void", args=[void_target.pk]), {"reason": "error"}
    ).status_code == 302
    ids = [
        item["id"]
        for item in api.get(reverse("api:bills-list"), headers=auth).json()["results"]
    ]
    assert void_target.pk not in ids
    assert (
        api.post(
            reverse("api:bills-confirm-payment", args=[void_target.pk]),
            {"reference": void_target.reference},
            content_type="application/json",
            headers=auth,
        ).status_code
        == 404
    )
