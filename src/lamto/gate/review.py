from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import FaceEnrollment, PendingEnrollmentPhoto, ReviewStatus, VehiclePlate
from .photos import queue_photo_deletion


class ReviewNotPermitted(PermissionDenied):
    pass


class ReviewNotPossible(ValueError):
    pass


def _assert_manages(membership, building_id):
    if membership.building_id != building_id or not membership.active:
        raise ReviewNotPermitted("Registration belongs to another building.")


def _drop_photo(enrollment):
    photo = PendingEnrollmentPhoto.objects.filter(enrollment=enrollment).first()
    if photo:
        queue_photo_deletion(photo)


def approve_face(enrollment, membership):
    _assert_manages(membership, enrollment.occupancy.unit.building_id)
    with transaction.atomic():
        enrollment = FaceEnrollment.objects.select_for_update().get(pk=enrollment.pk)
        if enrollment.status != ReviewStatus.PENDING:
            raise ReviewNotPossible(_("Only a pending enrolment can be approved."))
        if enrollment.embedding is None:
            raise ReviewNotPossible(_("The face embedding is missing; the resident must resubmit."))
        if not PendingEnrollmentPhoto.objects.select_for_update().filter(enrollment=enrollment).exists():
            raise ReviewNotPossible(_("The review photo has expired; the resident must resubmit."))
        enrollment.status = ReviewStatus.APPROVED
        enrollment.reviewed_by = membership.user
        enrollment.reviewed_at = timezone.now()
        enrollment.review_note = ""
        enrollment.save(update_fields=["status", "reviewed_by", "reviewed_at", "review_note"])
        _drop_photo(enrollment)
    return enrollment


def _close_face(enrollment, membership, note):
    with transaction.atomic():
        enrollment.status = ReviewStatus.REJECTED
        enrollment.embedding = None
        enrollment.reviewed_by = membership.user
        enrollment.reviewed_at = timezone.now()
        enrollment.review_note = note[:255]
        enrollment.save(update_fields=["status", "embedding", "reviewed_by", "reviewed_at", "review_note"])
        _drop_photo(enrollment)
    return enrollment


def reject_face(enrollment, membership, note):
    _assert_manages(membership, enrollment.occupancy.unit.building_id)
    if not (note or "").strip():
        raise ReviewNotPossible(_("A rejection reason is required."))
    if enrollment.status not in {ReviewStatus.PENDING, ReviewStatus.APPROVED}:
        raise ReviewNotPossible(_("This enrolment has already been closed."))
    return _close_face(enrollment, membership, note.strip())


def revoke_face(enrollment, membership):
    _assert_manages(membership, enrollment.occupancy.unit.building_id)
    return _close_face(enrollment, membership, "Revoked by management.")


def approve_plate(plate, membership):
    _assert_manages(membership, plate.building_id)
    if plate.status == ReviewStatus.APPROVED:
        return plate
    if VehiclePlate.objects.filter(building_id=plate.building_id, plate=plate.plate, status=ReviewStatus.APPROVED).exclude(pk=plate.pk).exists():
        raise ReviewNotPossible(_("Another resident already holds this plate in this building."))
    plate.status = ReviewStatus.APPROVED
    plate.reviewed_by = membership.user
    plate.reviewed_at = timezone.now()
    plate.review_note = ""
    plate.save(update_fields=["status", "reviewed_by", "reviewed_at", "review_note"])
    return plate


def reject_plate(plate, membership, note):
    _assert_manages(membership, plate.building_id)
    if not (note or "").strip():
        raise ReviewNotPossible(_("A rejection reason is required."))
    plate.status = ReviewStatus.REJECTED
    plate.reviewed_by = membership.user
    plate.reviewed_at = timezone.now()
    plate.review_note = note.strip()[:255]
    plate.save(update_fields=["status", "reviewed_by", "reviewed_at", "review_note"])
    return plate


def revoke_plate_as_manager(plate, membership):
    return reject_plate(plate, membership, "Revoked by management.")
