import pytest

from lamto.gate.crypto import seal_embedding
from lamto.gate.devices import issue_credential
from lamto.gate.embedding import NoFaceDetected
from lamto.gate.models import FaceEnrollment, GateDevice, GateEvent, ReviewStatus, VehiclePlate
from lamto.gate.recognition import recognize_face, recognize_plate
from lamto.gate.tests.fakes import FAKE_MODEL_NAME, FAKE_MODEL_VERSION, face_bytes, fake_vector

pytestmark = pytest.mark.django_db


@pytest.fixture
def credential(building, management):
    device = GateDevice.objects.create(building=building, label="North", direction="ENTRY")
    return issue_credential(device, management)[0]


def test_face_read_logs_match_but_failed_read_does_not(credential, occupancy, use_fake_embedder):
    FaceEnrollment.objects.create(
        occupancy=occupancy, embedding=seal_embedding(fake_vector("nguyen")),
        model_name=FAKE_MODEL_NAME, model_version=FAKE_MODEL_VERSION,
        status=ReviewStatus.APPROVED,
    )
    outcome = recognize_face(credential, face_bytes("nguyen"))
    assert (outcome.matched, outcome.display_name, outcome.unit_label) == (True, "Nguyen A", "12A")
    assert GateEvent.objects.get().threshold_used == pytest.approx(0.38)
    with pytest.raises(NoFaceDetected):
        recognize_face(credential, b"NOFACE")
    assert GateEvent.objects.count() == 1


def test_plate_read_normalizes_and_logs(credential, occupancy):
    plate = VehiclePlate.objects.create(
        occupancy=occupancy, building=occupancy.unit.building, plate="51F12345",
        status=ReviewStatus.APPROVED,
    )
    outcome = recognize_plate(credential, "51F-123.45")
    event = GateEvent.objects.get(pk=outcome.event_id)
    assert outcome.matched and event.matched_plate == plate
    assert event.normalized_plate_text == "51F12345"


def test_face_model_mismatch_and_cross_building_plate_do_not_leak(credential, occupancy, use_fake_embedder):
    from lamto.accounts.models import Building
    FaceEnrollment.objects.create(occupancy=occupancy, embedding=seal_embedding(fake_vector("nguyen")), model_name=FAKE_MODEL_NAME, model_version="old", status=ReviewStatus.APPROVED)
    VehiclePlate.objects.create(occupancy=occupancy, building=occupancy.unit.building, plate="51F12345", status=ReviewStatus.APPROVED)
    other = Building.objects.create(name="Other")
    credential.device.building = other
    credential.device.save(update_fields=["building"])
    assert not recognize_face(credential, face_bytes("nguyen")).matched
    assert not recognize_plate(credential, "51F12345").matched
