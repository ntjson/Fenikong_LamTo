import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient

from lamto.gate.devices import issue_credential
from lamto.gate.models import GateDevice
from lamto.gate.tests.conftest import building, management  # noqa: F401

pytestmark = pytest.mark.django_db


@pytest.fixture
def reader(building, management):
    device = GateDevice.objects.create(
        building=building, label="North", direction=GateDevice.Direction.ENTRY
    )
    _, token = issue_credential(device, management)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"GateDevice {token}")
    return client


def test_missing_reader_credential_is_rejected():
    response = APIClient().post(
        reverse("api:gate-recognize-plate"), {"plate": "51F12345"}, format="json"
    )
    assert response.status_code == 401
    assert response.json()["code"] == "gate_device_unauthenticated"


def test_authenticated_reader_gets_its_server_configuration(reader):
    response = reader.get(reverse("api:gate-device"))
    assert response.status_code == 200
    assert response.json() == {"label": "North", "direction": "ENTRY"}


def test_reader_configuration_rejects_missing_credential():
    response = APIClient().get(reverse("api:gate-device"))
    assert response.status_code == 401


def test_reader_plate_endpoint_returns_unreadable_code(reader):
    response = reader.post(
        reverse("api:gate-recognize-plate"), {"plate": "!!"}, format="json"
    )
    assert response.status_code == 422
    assert response.json()["code"] == "gate_plate_unreadable"


def test_reader_face_upload_has_a_stable_size_error(reader, settings):
    settings.GATE_MAX_FACE_UPLOAD_BYTES = 3
    response = reader.post(reverse("api:gate-recognize-face"), {"photo": SimpleUploadedFile("face.jpg", b"1234", content_type="image/jpeg")}, format="multipart")
    assert response.status_code == 413
    assert response.json()["code"] == "gate_face_upload_too_large"


def test_successful_recognition_is_throttled_per_device(reader):
    assert reader.post(reverse("api:gate-recognize-plate"), {"plate": "51F12345"}, format="json").status_code == 200
    response = reader.post(reverse("api:gate-recognize-plate"), {"plate": "51F12345"}, format="json")
    assert response.status_code == 429
    assert response["Content-Type"].startswith("application/problem+json")
    assert response.json()["code"] == "gate_recognition_throttled"
