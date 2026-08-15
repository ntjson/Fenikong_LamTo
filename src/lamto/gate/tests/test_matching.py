import numpy as np
import pytest

from lamto.gate.crypto import seal_embedding
from lamto.gate.matching import match_face, match_plate
from lamto.gate.models import FaceEnrollment, ReviewStatus, VehiclePlate
from lamto.gate.tests.fakes import FAKE_MODEL_NAME, FAKE_MODEL_VERSION, fake_vector

pytestmark = pytest.mark.django_db
MODEL = {"model_name": FAKE_MODEL_NAME, "model_version": FAKE_MODEL_VERSION}


def test_matching_is_scoped_and_thresholded(occupancy, second_occupancy, settings):
    FaceEnrollment.objects.create(
        occupancy=occupancy, embedding=seal_embedding(fake_vector("nguyen")),
        model_name=FAKE_MODEL_NAME, model_version=FAKE_MODEL_VERSION,
        status=ReviewStatus.APPROVED,
    )
    assert match_face(occupancy.unit.building, fake_vector("nguyen"), **MODEL).occupancy == occupancy
    assert match_face(occupancy.unit.building, fake_vector("stranger"), **MODEL).occupancy is None
    settings.GATE_FACE_MATCH_THRESHOLD = 1.01
    assert match_face(occupancy.unit.building, fake_vector("nguyen"), **MODEL).occupancy is None


def test_zero_vector_is_refused(occupancy):
    with pytest.raises(ValueError):
        match_face(occupancy.unit.building, np.zeros(512), **MODEL)


def test_only_approved_plate_in_building_matches(occupancy):
    plate = VehiclePlate.objects.create(
        occupancy=occupancy, building=occupancy.unit.building, plate="51F12345"
    )
    assert match_plate(occupancy.unit.building, plate.plate) is None
    plate.status = ReviewStatus.APPROVED
    plate.save(update_fields=["status"])
    assert match_plate(occupancy.unit.building, plate.plate) == plate


def test_plate_does_not_match_an_inactive_occupancy(occupancy):
    plate = VehiclePlate.objects.create(occupancy=occupancy, building=occupancy.unit.building, plate="51F12345", status=ReviewStatus.APPROVED)
    occupancy.active = False
    occupancy.save(update_fields=["active"])
    assert match_plate(occupancy.unit.building, plate.plate) is None
