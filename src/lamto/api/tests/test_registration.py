import json
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import pytest
from django.db import connection
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient

from lamto.accounts.models import (
    AuthThrottleBucket,
    Building,
    RegistrationRequest,
    ResidentOccupancy,
    Unit,
    User,
)
from lamto.accounts.registration import submit_registration


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def unit():
    return Unit.objects.create(
        building=Building.objects.create(name="Tower A"), label="101"
    )


def payload(unit, **overrides):
    data = {
        "full_name": "Nguyễn Văn An",
        "phone": "0901234567",
        "email": "",
        "password": "correct horse battery staple",
        "building_id": unit.building_id,
        "unit_id": unit.id,
    }
    data.update(overrides)
    return data


def problem(response):
    return json.loads(response.content)


def test_options_returns_only_buildings_and_units(api_client, unit):
    resident = User.objects.create_user(phone="0912345678", password="secret")
    ResidentOccupancy.objects.create(user=resident, unit=unit)

    response = api_client.get(reverse("api:registration-options"))

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": unit.building_id,
            "name": "Tower A",
            "units": [{"id": unit.id, "label": "101"}],
        }
    ]
    assert "resident" not in response.content.decode().lower()


def test_create_registration_returns_only_status_secret(api_client, unit):
    data = payload(unit)

    response = api_client.post(
        reverse("api:registration-create"), data, format="json"
    )

    assert response.status_code == 201
    assert set(response.json()) == {"status", "status_token", "phone"}
    assert response.json()["status"] == "PENDING"
    assert data["password"] not in response.content.decode()
    request = RegistrationRequest.objects.get()
    assert request.password_hash not in response.content.decode()
    assert response.json()["status_token"] not in repr(request)


def test_invalid_unit_building_returns_validation_problem(api_client, unit):
    other = Building.objects.create(name="Tower B")

    response = api_client.post(
        reverse("api:registration-create"),
        payload(unit, building_id=other.id),
        format="json",
    )

    assert response.status_code == 400
    assert problem(response)["code"] == "validation_failed"


def test_status_requires_exact_header_and_disables_storage(api_client, unit):
    submission = submit_registration(**payload(unit))

    missing = api_client.get(reverse("api:registration-status"))
    response = api_client.get(
        reverse("api:registration-status"),
        HTTP_X_REGISTRATION_STATUS_TOKEN=submission.status_token,
    )

    assert missing.status_code == 400
    assert problem(missing)["code"] == "validation_failed"
    assert missing["Cache-Control"] == "private, no-store"
    assert response.status_code == 200
    assert response["Cache-Control"] == "private, no-store"
    assert response.json() == {
        "status": "PENDING",
        "phone": "+84901234567",
        "building": "Tower A",
        "unit": "101",
    }
    body = response.content.decode()
    assert submission.status_token not in body
    assert submission.request.password_hash not in body


def test_invalid_status_token_disables_storage(api_client):
    response = api_client.get(
        reverse("api:registration-status"),
        HTTP_X_REGISTRATION_STATUS_TOKEN="invalid",
    )

    assert response.status_code == 404
    assert response["Cache-Control"] == "private, no-store"


@pytest.mark.parametrize(
    ("status", "reason", "has_reason"),
    [
        (RegistrationRequest.Status.PENDING, "", False),
        (RegistrationRequest.Status.APPROVED, "", False),
        (RegistrationRequest.Status.EXPIRED, "", False),
        (RegistrationRequest.Status.REJECTED, "Not a resident", True),
    ],
)
def test_status_exposes_reason_only_for_rejection(
    api_client, unit, status, reason, has_reason
):
    submission = submit_registration(**payload(unit))
    RegistrationRequest.objects.filter(pk=submission.request.pk).update(
        status=status, rejection_reason=reason, password_hash=""
    )

    response = api_client.get(
        reverse("api:registration-status"),
        HTTP_X_REGISTRATION_STATUS_TOKEN=submission.status_token,
    )

    assert response.status_code == 200
    assert ("rejection_reason" in response.json()) is has_reason
    assert "token" not in response.content.decode().lower()
    assert "password" not in response.content.decode().lower()


def test_existing_user_and_pending_duplicate_have_identical_conflict(api_client, unit):
    User.objects.create_user(phone="0901234567", password="existing")
    existing = api_client.post(
        reverse("api:registration-create"), payload(unit), format="json"
    )
    User.objects.all().delete()
    submit_registration(**payload(unit))
    duplicate = api_client.post(
        reverse("api:registration-create"), payload(unit), format="json"
    )

    fields = ("status", "code", "title", "detail")
    assert existing.status_code == duplicate.status_code == 409
    assert {key: problem(existing)[key] for key in fields} == {
        key: problem(duplicate)[key] for key in fields
    }


@pytest.mark.parametrize("same_phone", [True, False])
def test_sixth_attempt_is_throttled_per_phone_and_ip(api_client, unit, same_phone):
    for attempt in range(5):
        response = api_client.post(
            reverse("api:registration-create"),
            payload(
                unit,
                phone="0901234567" if same_phone else f"09012345{attempt:02d}",
                unit_id=999999,
            ),
            format="json",
            REMOTE_ADDR=f"203.0.113.{attempt}" if same_phone else "203.0.113.10",
        )
        assert response.status_code == 400

    response = api_client.post(
        reverse("api:registration-create"),
        payload(
            unit,
            phone="0901234567" if same_phone else "0901234599",
            unit_id=999999,
        ),
        format="json",
        REMOTE_ADDR="203.0.113.99" if same_phone else "203.0.113.10",
    )

    assert response.status_code == 429
    assert problem(response)["code"] == "throttled"


def test_attempts_are_recorded_before_submission(api_client, unit):
    with patch(
        "lamto.api.registration_views.submit_registration",
        side_effect=RuntimeError("service called"),
    ), pytest.raises(RuntimeError, match="service called"):
        api_client.post(
            reverse("api:registration-create"), payload(unit), format="json"
        )

    assert AuthThrottleBucket.objects.count() == 2


def test_serializer_invalid_attempts_throttle_usable_phone(api_client):
    for attempt in range(5):
        response = api_client.post(
            reverse("api:registration-create"),
            {"phone": "090 123 4567"},
            format="json",
            REMOTE_ADDR=f"203.0.113.{attempt}",
        )
        assert response.status_code == 400

    response = api_client.post(
        reverse("api:registration-create"),
        {"phone": "+84 90 123 4567"},
        format="json",
        REMOTE_ADDR="203.0.113.99",
    )

    assert response.status_code == 429


def test_malformed_json_attempts_are_throttled_by_ip(api_client):
    for _ in range(5):
        response = api_client.generic(
            "POST",
            reverse("api:registration-create"),
            "{",
            content_type="application/json",
            REMOTE_ADDR="203.0.113.20",
        )
        assert response.status_code == 400

    response = api_client.generic(
        "POST",
        reverse("api:registration-create"),
        "{",
        content_type="application/json",
        REMOTE_ADDR="203.0.113.20",
    )

    assert response.status_code == 429


def test_registration_throttle_ignores_untrusted_forwarded_for(api_client, unit):
    for attempt in range(5):
        response = api_client.post(
            reverse("api:registration-create"),
            payload(unit, phone=f"09012345{attempt:02d}", unit_id=999999),
            format="json",
            REMOTE_ADDR="203.0.113.30",
            HTTP_X_FORWARDED_FOR=f"198.51.100.{attempt}",
        )
        assert response.status_code == 400

    response = api_client.post(
        reverse("api:registration-create"),
        payload(unit, phone="0901234599", unit_id=999999),
        format="json",
        REMOTE_ADDR="203.0.113.30",
        HTTP_X_FORWARDED_FOR="198.51.100.99",
    )
    assert response.status_code == 429


class RegistrationThrottleRaceTests(TransactionTestCase):
    def _fixture_teardown(self):
        pass

    def tearDown(self):
        AuthThrottleBucket.objects.all().delete()
        Unit.objects.all().delete()
        Building.objects.all().delete()

    def test_concurrent_attempts_cannot_exceed_limit(self):
        unit = Unit.objects.create(
            building=Building.objects.create(name="Race tower"), label="101"
        )

        def attempt(index):
            connection.close()
            try:
                return APIClient().post(
                    reverse("api:registration-create"),
                    payload(unit, unit_id=999999),
                    format="json",
                    REMOTE_ADDR=f"203.0.113.{index}",
                ).status_code
            finally:
                connection.close()

        with ThreadPoolExecutor(max_workers=10) as pool:
            statuses = list(pool.map(attempt, range(10)))

        assert statuses.count(400) == 5
        assert statuses.count(429) == 5
