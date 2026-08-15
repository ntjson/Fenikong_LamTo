import pytest
import threading
import tempfile
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test import TransactionTestCase, override_settings
from django.utils import timezone

from lamto.accounts.models import Building, ManagementMembership, ResidentOccupancy, Unit, User
from lamto.gate.enrollment import submit_face_enrollment, submit_plate
from django.db import IntegrityError
from lamto.gate.models import FaceEnrollment, PendingEnrollmentPhoto, PhotoDeletion, ReviewStatus, VehiclePlate
from lamto.gate.retention import purge_expired_enrollment_photos
from lamto.gate.review import ReviewNotPermitted, ReviewNotPossible, approve_face, approve_plate, reject_face, reject_plate, revoke_face
from lamto.gate.tests.fakes import face_bytes

pytestmark = pytest.mark.django_db


def _enrol(occupancy, clean_scanner, seed="nguyen"):
    return submit_face_enrollment(occupancy, SimpleUploadedFile("f.jpg", face_bytes(seed), content_type="image/jpeg"), scanner=clean_scanner)


def test_approving_a_face_keeps_the_vector_and_deletes_the_photo(occupancy, management, use_fake_embedder, gate_storage, clean_scanner):
    enrollment = _enrol(occupancy, clean_scanner)
    approve_face(enrollment, management)
    enrollment.refresh_from_db()
    assert enrollment.status == ReviewStatus.APPROVED
    assert enrollment.embedding is not None
    assert enrollment.reviewed_by_id == management.user_id
    assert enrollment.reviewed_at is not None
    assert not PendingEnrollmentPhoto.objects.exists()


def test_rejecting_a_face_deletes_the_vector_and_keeps_the_reason(occupancy, management, use_fake_embedder, gate_storage, clean_scanner):
    enrollment = _enrol(occupancy, clean_scanner)
    reject_face(enrollment, management, "Face not clearly visible.")
    enrollment.refresh_from_db()
    assert enrollment.status == ReviewStatus.REJECTED
    assert enrollment.embedding is None
    assert enrollment.review_note == "Face not clearly visible."
    assert not PendingEnrollmentPhoto.objects.exists()


def test_photo_delete_failure_leaves_committed_decision_and_cleanup(occupancy, management, use_fake_embedder, gate_storage, clean_scanner):
    enrollment = _enrol(occupancy, clean_scanner)
    with patch("lamto.gate.photos.delete_pending_photo", side_effect=OSError):
        approve_face(enrollment, management)
    enrollment.refresh_from_db()
    assert enrollment.status == ReviewStatus.APPROVED
    assert not PendingEnrollmentPhoto.objects.filter(enrollment=enrollment).exists()
    assert PhotoDeletion.objects.exists()


@pytest.mark.parametrize("decision", ["approve", "reject", "revoke"])
def test_review_db_failure_preserves_photo_and_enrollment(decision, occupancy, management, use_fake_embedder, gate_storage, clean_scanner):
    enrollment = _enrol(occupancy, clean_scanner)
    photo = PendingEnrollmentPhoto.objects.get(enrollment=enrollment)
    with patch("lamto.gate.photos.PhotoDeletion.objects.create", side_effect=IntegrityError), pytest.raises(IntegrityError):
        {"approve": lambda: approve_face(enrollment, management),
         "reject": lambda: reject_face(enrollment, management, "Bad photo"),
         "revoke": lambda: revoke_face(enrollment, management)}[decision]()
    enrollment.refresh_from_db()
    assert enrollment.status == ReviewStatus.PENDING
    assert enrollment.embedding is not None
    assert PendingEnrollmentPhoto.objects.filter(pk=photo.pk).exists()


def test_delete_failure_after_review_commit_leaves_durable_cleanup(occupancy, management, use_fake_embedder, gate_storage, clean_scanner):
    enrollment = _enrol(occupancy, clean_scanner)
    with patch("lamto.gate.photos.delete_pending_photo", side_effect=OSError):
        approve_face(enrollment, management)
    enrollment.refresh_from_db()
    assert enrollment.status == ReviewStatus.APPROVED
    assert not PendingEnrollmentPhoto.objects.exists()
    assert PhotoDeletion.objects.exists()


def test_rejecting_requires_a_reason(occupancy, management, use_fake_embedder, gate_storage, clean_scanner):
    with pytest.raises(ReviewNotPossible):
        reject_face(_enrol(occupancy, clean_scanner), management, "   ")


def test_a_face_cannot_be_approved_once_the_photo_is_gone(occupancy, management, use_fake_embedder, gate_storage, clean_scanner):
    enrollment = _enrol(occupancy, clean_scanner)
    PendingEnrollmentPhoto.objects.filter(enrollment=enrollment).delete()
    with pytest.raises(ReviewNotPossible):
        approve_face(enrollment, management)


def test_a_face_without_an_embedding_cannot_be_approved(occupancy, management, use_fake_embedder, gate_storage, clean_scanner):
    enrollment = _enrol(occupancy, clean_scanner)
    FaceEnrollment.objects.filter(pk=enrollment.pk).update(embedding=None)
    enrollment.refresh_from_db()
    with pytest.raises(ReviewNotPossible):
        approve_face(enrollment, management)


class FaceReviewRaceTests(TransactionTestCase):
    def _fixture_teardown(self):
        pass

    def setUp(self):
        location = tempfile.mkdtemp(prefix="lamto-gate-race-")
        self.settings = override_settings(
            GATE_FACE_EMBEDDER="lamto.gate.tests.fakes.FakeEmbedder",
            GATE_EMBEDDING_KEY="gate-test-key",
            GATE_FACE_CALIBRATED=True,
            STORAGES={
                "default": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": location}},
                "private": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": location}},
                "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
            },
        )
        self.settings.enable()
        building = Building.objects.create(name="Gate race building")
        unit = Unit.objects.create(building=building, label="R1")
        resident = User.objects.create(email="race-resident@example.com", display_name="Resident")
        manager = User.objects.create(email="race-manager@example.com", display_name="Manager")
        self.occupancy = ResidentOccupancy.objects.create(user=resident, unit=unit)
        self.management = ManagementMembership.objects.create(user=manager, building=building)

    def tearDown(self):
        self.settings.disable()

    def test_expiry_holds_enrollment_lock_until_approval_rechecks(self):
        enrollment = _enrol(self.occupancy, lambda file_obj: True)
        PendingEnrollmentPhoto.objects.filter(enrollment=enrollment).update(expires_at=timezone.now())
        expiry_has_lock = threading.Event()
        release_expiry = threading.Event()

        def pause_deletion(photo):
            expiry_has_lock.set()
            assert release_expiry.wait(10)
            from lamto.gate.photos import queue_photo_deletion
            return queue_photo_deletion(photo)

        def expire():
            connection.close()
            try:
                with patch("lamto.gate.retention.queue_photo_deletion", side_effect=pause_deletion):
                    purge_expired_enrollment_photos()
            finally:
                connection.close()

        def approve():
            connection.close()
            try:
                return approve_face(FaceEnrollment.objects.get(pk=enrollment.pk), ManagementMembership.objects.get(pk=self.management.pk))
            finally:
                connection.close()

        with ThreadPoolExecutor(max_workers=2) as pool:
            expiry = pool.submit(expire)
            assert expiry_has_lock.wait(10)
            approval = pool.submit(approve)
            with pytest.raises(TimeoutError):
                approval.result(timeout=0.2)
            release_expiry.set()
            expiry.result(timeout=10)
            with pytest.raises(ReviewNotPossible):
                approval.result(timeout=10)

        enrollment.refresh_from_db()
        assert enrollment.status == ReviewStatus.EXPIRED
        assert enrollment.embedding is None


def test_a_manager_from_another_building_cannot_decide(occupancy, use_fake_embedder, gate_storage, clean_scanner):
    other_building = Building.objects.create(name="Other Building")
    outsider = ManagementMembership.objects.create(user=User.objects.create(email="out@example.com", display_name="Out"), building=other_building)
    with pytest.raises(ReviewNotPermitted):
        approve_face(_enrol(occupancy, clean_scanner), outsider)


def test_revoking_an_approved_face_deletes_the_vector(occupancy, management, use_fake_embedder, gate_storage, clean_scanner):
    enrollment = _enrol(occupancy, clean_scanner)
    approve_face(enrollment, management)
    revoke_face(enrollment, management)
    enrollment.refresh_from_db()
    assert enrollment.status == ReviewStatus.REJECTED
    assert enrollment.embedding is None


def test_approving_a_plate_marks_it_and_attributes_the_decision(occupancy, management):
    plate = submit_plate(occupancy, "51F12345")
    approve_plate(plate, management)
    plate.refresh_from_db()
    assert plate.status == ReviewStatus.APPROVED
    assert plate.reviewed_by_id == management.user_id


def test_approving_a_plate_another_resident_already_holds_fails(occupancy, second_occupancy, management):
    approve_plate(submit_plate(second_occupancy, "51F12345"), management)
    clash = VehiclePlate.objects.create(occupancy=occupancy, building=occupancy.unit.building, plate="51F12345")
    with pytest.raises(ReviewNotPossible):
        approve_plate(clash, management)


def test_rejecting_a_plate_records_the_reason(occupancy, management):
    plate = submit_plate(occupancy, "51F12345")
    reject_plate(plate, management, "Not a resident vehicle.")
    plate.refresh_from_db()
    assert plate.status == ReviewStatus.REJECTED
    assert plate.review_note == "Not a resident vehicle."
