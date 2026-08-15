from unittest.mock import patch

import pytest
from django.urls import reverse

from lamto.accounts.models import (
    Building,
    ManagementMembership,
    RegistrationRequest,
    ResidentOccupancy,
    Unit,
    User,
)
from lamto.accounts.registration import submit_registration
from lamto.audit.models import AuditEvent


pytestmark = pytest.mark.django_db


def authenticate(client, user):
    client.force_login(user)


def setup_building(name, email):
    building = Building.objects.create(name=name)
    unit = Unit.objects.create(building=building, label="101")
    manager = User.objects.create_user(email=email, password="secret")
    membership = ManagementMembership.objects.create(user=manager, building=building)
    return membership, unit


def registration(
    unit,
    *,
    phone="0901234567",
    email="resident@example.test",
    name="Resident One",
):
    return submit_registration(
        full_name=name,
        phone=phone,
        email=email,
        password="correct horse battery staple",
        building_id=unit.building_id,
        unit_id=unit.pk,
    ).request


def test_list_contains_only_pending_requests_for_active_building(client):
    membership, unit = setup_building("Tower A", "manager-a@example.test")
    other_membership, other_unit = setup_building("Tower B", "manager-b@example.test")
    pending = registration(unit)
    decided = registration(
        unit,
        phone="0901234568",
        email="decided@example.test",
        name="Decided",
    )
    decided.status = RegistrationRequest.Status.REJECTED
    decided.save(update_fields=["status"])
    other = registration(other_unit, phone="0901234569", email="other@example.test", name="Other")
    authenticate(client, membership.user)

    response = client.get(reverse("web:staff-registration-list"))

    assert response.status_code == 200
    assert list(response.context["registrations"]) == [pending]
    assert pending.full_name.encode() in response.content
    assert decided.full_name.encode() not in response.content
    assert other.full_name.encode() not in response.content
    assert other_membership.building_id != membership.building_id


def test_detail_returns_404_for_another_building(client):
    membership, _unit = setup_building("Tower A", "manager-a@example.test")
    _other_membership, other_unit = setup_building("Tower B", "manager-b@example.test")
    request = registration(other_unit)
    authenticate(client, membership.user)

    assert (
        client.get(
            reverse("web:staff-registration-detail", args=[request.pk])
        ).status_code
        == 404
    )


@pytest.mark.parametrize("decision", ["approve", "reject"])
def test_cross_building_decision_returns_404_before_service(client, decision):
    membership, _unit = setup_building("Tower A", "manager-a@example.test")
    _other_membership, other_unit = setup_building("Tower B", "manager-b@example.test")
    request = registration(other_unit)
    authenticate(client, membership.user)
    data = {"reason": "No"} if decision == "reject" else {}

    with patch(
        f"lamto.web.registration_views.{decision}_registration"
    ) as service:
        response = client.post(
            reverse(f"web:staff-registration-{decision}", args=[request.pk]), data
        )

    assert response.status_code == 404
    service.assert_not_called()


@pytest.mark.parametrize("decision", ["approve", "reject"])
def test_any_active_management_member_can_decide(client, decision):
    membership, unit = setup_building("Tower A", "manager-a@example.test")
    second = User.objects.create_user(email="manager-2@example.test", password="secret")
    ManagementMembership.objects.create(user=second, building=membership.building)
    request = registration(unit)
    authenticate(client, second)
    data = {"reason": "Not eligible"} if decision == "reject" else {}

    response = client.post(
        reverse(f"web:staff-registration-{decision}", args=[request.pk]), data
    )

    request.refresh_from_db()
    expected = (
        RegistrationRequest.Status.APPROVED
        if decision == "approve"
        else RegistrationRequest.Status.REJECTED
    )
    assert request.status == expected
    assert response.url == reverse("web:staff-registration-list")


def test_reject_requires_non_blank_reason(client):
    membership, unit = setup_building("Tower A", "manager-a@example.test")
    request = registration(unit)
    authenticate(client, membership.user)

    response = client.post(
        reverse("web:staff-registration-reject", args=[request.pk]), {"reason": "   "}
    )

    request.refresh_from_db()
    assert response.status_code == 200
    body = response.content.decode()
    assert "Rejection reason is required" in body or "Cần lý do từ chối" in body
    assert request.status == RegistrationRequest.Status.PENDING


def test_duplicate_approval_is_safe(client):
    membership, unit = setup_building("Tower A", "manager-a@example.test")
    request = registration(unit)
    authenticate(client, membership.user)
    url = reverse("web:staff-registration-approve", args=[request.pk])

    client.post(url)
    response = client.post(url, follow=True)

    assert User.objects.filter(phone="0901234567").count() == 1
    body = response.content.decode()
    assert "already been decided" in body or "đã được quyết định" in body
    assert response.redirect_chain[-1][0] == reverse(
        "web:staff-registration-detail", args=[request.pk]
    )


def test_detail_does_not_render_secrets(client):
    membership, unit = setup_building("Tower A", "manager-a@example.test")
    request = registration(unit)
    authenticate(client, membership.user)

    response = client.get(reverse("web:staff-registration-detail", args=[request.pk]))

    assert request.password_hash.encode() not in response.content
    assert request.status_token_digest.encode() not in response.content


def test_public_registration_can_be_approved_end_to_end(client):
    membership, unit = setup_building("Tower A", "manager-a@example.test")
    other_membership, _ = setup_building("Tower B", "manager-b@example.test")
    password = "correct horse battery staple"

    submitted = client.post(
        reverse("api:registration-create"),
        {
            "full_name": "Resident Journey",
            "phone": "090 123 4567",
            "email": "journey@example.test",
            "password": password,
            "building_id": unit.building_id,
            "unit_id": unit.pk,
        },
        content_type="application/json",
    )
    assert submitted.status_code == 201
    status_token = submitted.json()["status_token"]
    request = RegistrationRequest.objects.get()

    authenticate(client, membership.user)
    queue = client.get(reverse("web:staff-registration-list"))
    inbox = client.get(reverse("web:action-inbox"))
    assert request in queue.context["registrations"]
    assert request.full_name.encode() in inbox.content

    authenticate(client, other_membership.user)
    other_queue = client.get(reverse("web:staff-registration-list"))
    other_inbox = client.get(reverse("web:action-inbox"))
    assert request not in other_queue.context["registrations"]
    assert not any(
        item.target_id == str(request.pk)
        for item in other_inbox.context["action_page"].object_list
    )

    authenticate(client, membership.user)
    approved = client.post(
        reverse("web:staff-registration-approve", args=[request.pk])
    )
    assert approved.status_code == 302
    status = client.get(
        reverse("api:registration-status"),
        HTTP_X_REGISTRATION_STATUS_TOKEN=status_token,
    )
    assert status.json()["status"] == "APPROVED"
    login = client.post(
        reverse("api:auth-login"),
        {"identifier": "0901234567", "password": password},
        content_type="application/json",
    )
    assert login.status_code == 200

    request.refresh_from_db()
    resident = User.objects.get(phone="0901234567")
    assert ResidentOccupancy.objects.filter(
        user=resident, unit=unit, active=True
    ).count() == 1
    assert request.password_hash == ""
    assert AuditEvent.objects.filter(
        action="registration.approved",
        actor=membership.user,
        target_id=str(request.pk),
        result="accepted",
    ).exists()


def test_rejected_public_registration_exposes_reason_and_allows_resubmission(client):
    membership, unit = setup_building("Tower A", "manager-a@example.test")
    submitted = client.post(
        reverse("api:registration-create"),
        {
            "full_name": "Rejected Resident",
            "phone": "090 123 4567",
            "email": "",
            "password": "correct horse battery staple",
            "building_id": unit.building_id,
            "unit_id": unit.pk,
        },
        content_type="application/json",
    )
    assert submitted.status_code == 201
    request = RegistrationRequest.objects.get()

    authenticate(client, membership.user)
    rejected = client.post(
        reverse("web:staff-registration-reject", args=[request.pk]),
        {"reason": "Lease could not be verified"},
    )
    assert rejected.status_code == 302
    status = client.get(
        reverse("api:registration-status"),
        HTTP_X_REGISTRATION_STATUS_TOKEN=submitted.json()["status_token"],
    )
    assert status.json()["status"] == "REJECTED"
    assert status.json()["rejection_reason"] == "Lease could not be verified"

    request.refresh_from_db()
    assert request.password_hash == ""
    assert AuditEvent.objects.filter(
        action="registration.rejected",
        actor=membership.user,
        target_id=str(request.pk),
        result="accepted",
    ).exists()
    resubmitted = client.post(
        reverse("api:registration-create"),
        {
            "full_name": "Rejected Resident",
            "phone": "+84 90 123 4567",
            "email": "",
            "password": "new correct horse battery staple",
            "building_id": unit.building_id,
            "unit_id": unit.pk,
        },
        content_type="application/json",
    )
    assert resubmitted.status_code == 201
    assert RegistrationRequest.objects.filter(phone="+84901234567").count() == 2
