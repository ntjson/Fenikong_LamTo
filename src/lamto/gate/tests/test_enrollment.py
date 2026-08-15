import os

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from unittest.mock import patch

from lamto.gate.embedding import NoFaceDetected
from lamto.gate.enrollment import PhotoRejected, PlateAlreadyRegistered, revoke_face_enrollment, revoke_plate, submit_face_enrollment, submit_plate
from lamto.gate.models import FaceEnrollment, PendingEnrollmentPhoto, PhotoDeletion, ReviewStatus, VehiclePlate
from lamto.gate.plates import PlateFormatError
from lamto.gate.tests.fakes import FAKE_MODEL_NAME, face_bytes

pytestmark = pytest.mark.django_db


def _upload(payload: bytes, content_type="image/jpeg"):
    return SimpleUploadedFile("face.jpg", payload, content_type=content_type)


def test_submitting_a_face_stores_a_sealed_vector_and_a_pending_photo(occupancy, use_fake_embedder, gate_storage, clean_scanner):
    enrollment = submit_face_enrollment(occupancy, _upload(face_bytes("nguyen")), scanner=clean_scanner)
    assert enrollment.status == ReviewStatus.PENDING
    assert enrollment.model_name == FAKE_MODEL_NAME
    assert bytes(enrollment.embedding) != face_bytes("nguyen")
    photo = PendingEnrollmentPhoto.objects.get(enrollment=enrollment)
    assert photo.expires_at > enrollment.submitted_at
    assert os.path.exists(os.path.join(gate_storage, photo.storage_key))


def test_resubmitting_replaces_the_previous_pending_photo(occupancy, use_fake_embedder, gate_storage, clean_scanner):
    first = submit_face_enrollment(occupancy, _upload(face_bytes("one")), scanner=clean_scanner)
    first_key = PendingEnrollmentPhoto.objects.get(enrollment=first).storage_key
    submit_face_enrollment(occupancy, _upload(face_bytes("two")), scanner=clean_scanner)
    from lamto.gate.photos import process_photo_deletions
    process_photo_deletions()
    assert PendingEnrollmentPhoto.objects.count() == 1
    assert not os.path.exists(os.path.join(gate_storage, first_key))


def test_an_infected_image_is_rejected_and_stores_nothing(occupancy, use_fake_embedder, gate_storage, infected_scanner):
    with pytest.raises(PhotoRejected):
        submit_face_enrollment(occupancy, _upload(face_bytes("nguyen")), scanner=infected_scanner)
    assert not FaceEnrollment.objects.exists()
    assert not PendingEnrollmentPhoto.objects.exists()


def test_a_quality_failure_stores_nothing(occupancy, use_fake_embedder, gate_storage, clean_scanner):
    with pytest.raises(NoFaceDetected):
        submit_face_enrollment(occupancy, _upload(b"NOFACE"), scanner=clean_scanner)
    assert not FaceEnrollment.objects.exists()


def test_a_non_image_content_type_is_rejected(occupancy, use_fake_embedder, gate_storage, clean_scanner):
    with pytest.raises(PhotoRejected):
        submit_face_enrollment(occupancy, _upload(face_bytes("x"), "application/pdf"), scanner=clean_scanner)


def test_an_oversized_image_is_rejected(occupancy, use_fake_embedder, gate_storage, clean_scanner, settings):
    settings.GATE_MAX_FACE_UPLOAD_BYTES = 10
    with pytest.raises(PhotoRejected):
        submit_face_enrollment(occupancy, _upload(face_bytes("a-long-seed-value")), scanner=clean_scanner)


def test_revoking_a_face_removes_the_row_and_the_photo(occupancy, use_fake_embedder, gate_storage, clean_scanner):
    enrollment = submit_face_enrollment(occupancy, _upload(face_bytes("nguyen")), scanner=clean_scanner)
    key = PendingEnrollmentPhoto.objects.get(enrollment=enrollment).storage_key
    revoke_face_enrollment(occupancy)
    from lamto.gate.photos import process_photo_deletions
    process_photo_deletions()
    assert not FaceEnrollment.objects.exists()
    assert not os.path.exists(os.path.join(gate_storage, key))


def test_db_failure_compensates_the_newly_stored_photo(occupancy, use_fake_embedder, gate_storage, clean_scanner):
    with patch("lamto.gate.enrollment.PendingEnrollmentPhoto.objects.create", side_effect=IntegrityError):
        with pytest.raises(IntegrityError):
            submit_face_enrollment(occupancy, _upload(face_bytes("nguyen")), scanner=clean_scanner)
    assert not any(os.scandir(os.path.join(gate_storage, "gate/pending-enrollment")))
    assert not FaceEnrollment.objects.exists()


def test_resubmission_db_failure_preserves_previous_row_and_photo(occupancy, use_fake_embedder, gate_storage, clean_scanner):
    enrollment = submit_face_enrollment(occupancy, _upload(face_bytes("old")), scanner=clean_scanner)
    old_photo = PendingEnrollmentPhoto.objects.get(enrollment=enrollment)
    old_embedding = bytes(enrollment.embedding)
    with patch("lamto.gate.enrollment.PendingEnrollmentPhoto.objects.create", side_effect=IntegrityError):
        with pytest.raises(IntegrityError):
            submit_face_enrollment(occupancy, _upload(face_bytes("new")), scanner=clean_scanner)
    enrollment.refresh_from_db()
    assert bytes(enrollment.embedding) == old_embedding
    assert PendingEnrollmentPhoto.objects.get(enrollment=enrollment).storage_key == old_photo.storage_key
    assert os.path.exists(os.path.join(gate_storage, old_photo.storage_key))
    assert not PhotoDeletion.objects.exists()


def test_submitting_plates_normalizes_and_allows_several(occupancy):
    car = submit_plate(occupancy, "51F-123.45")
    bike = submit_plate(occupancy, "59x1 999.99")
    assert (car.plate, bike.plate) == ("51F12345", "59X199999")
    assert VehiclePlate.objects.filter(occupancy=occupancy).count() == 2


def test_resubmitting_the_same_plate_reuses_the_row(occupancy):
    assert submit_plate(occupancy, "51F12345").pk == submit_plate(occupancy, "51f 123 45").pk


def test_a_plate_approved_elsewhere_in_the_building_is_refused(occupancy, second_occupancy):
    approved = submit_plate(second_occupancy, "51F12345")
    VehiclePlate.objects.filter(pk=approved.pk).update(status=ReviewStatus.APPROVED)
    with pytest.raises(PlateAlreadyRegistered):
        submit_plate(occupancy, "51F12345")


def test_an_unusable_plate_is_refused(occupancy):
    with pytest.raises(PlateFormatError):
        submit_plate(occupancy, "!!")


def test_revoking_a_plate_deletes_it(occupancy):
    plate = submit_plate(occupancy, "51F12345")
    revoke_plate(occupancy, plate.pk)
    assert not VehiclePlate.objects.filter(pk=plate.pk).exists()
