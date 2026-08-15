import io
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from lamto.documents.scanner import scan_with_clamav

from .crypto import seal_embedding
from .embedding import get_embedder
from .models import FaceEnrollment, PendingEnrollmentPhoto, ReviewStatus, VehiclePlate
from .photos import delete_pending_photo, queue_photo_deletion, store_pending_photo
from .plates import normalize_plate

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}


class PhotoRejected(ValueError):
    pass


class PlateAlreadyRegistered(ValueError):
    pass


def submit_face_enrollment(occupancy, uploaded_file, scanner=None):
    scanner = scanner or scan_with_clamav
    content_type = getattr(uploaded_file, "content_type", "") or ""
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise PhotoRejected("Only JPEG or PNG images are accepted.")
    data = uploaded_file.read()
    if len(data) > settings.GATE_MAX_FACE_UPLOAD_BYTES or not data:
        raise PhotoRejected("Image is too large or empty.")
    if not scanner(io.BytesIO(data)):
        raise PhotoRejected("Image failed the malware scan.")
    result = get_embedder().embed(data)
    now = timezone.now()
    key, version_id = store_pending_photo(io.BytesIO(data), content_type)
    try:
        with transaction.atomic():
            enrollment, _ = FaceEnrollment.objects.get_or_create(occupancy=occupancy)
            previous = PendingEnrollmentPhoto.objects.filter(enrollment=enrollment).first()
            if previous:
                queue_photo_deletion(previous)
            enrollment.embedding = seal_embedding(result.vector)
            enrollment.model_name = result.model_name
            enrollment.model_version = result.model_version
            enrollment.status = ReviewStatus.PENDING
            enrollment.submitted_at = now
            enrollment.reviewed_by = enrollment.reviewed_at = None
            enrollment.review_note = ""
            enrollment.save()
            PendingEnrollmentPhoto.objects.create(
                enrollment=enrollment, storage_key=key, provider_version_id=version_id,
                content_type=content_type, byte_size=len(data),
                expires_at=now + timedelta(hours=settings.GATE_ENROLLMENT_PHOTO_TTL_HOURS),
            )
    except Exception:
        delete_pending_photo(key, version_id)
        raise
    return enrollment


def revoke_face_enrollment(occupancy):
    with transaction.atomic():
        enrollment = FaceEnrollment.objects.filter(occupancy=occupancy).first()
        if enrollment is None:
            return
        photo = PendingEnrollmentPhoto.objects.filter(enrollment=enrollment).first()
        if photo:
            queue_photo_deletion(photo)
        enrollment.delete()


def submit_plate(occupancy, raw_plate):
    plate = normalize_plate(raw_plate)
    building = occupancy.unit.building
    if VehiclePlate.objects.filter(building=building, plate=plate, status=ReviewStatus.APPROVED).exclude(occupancy=occupancy).exists():
        raise PlateAlreadyRegistered("Plate is already registered in this building.")
    obj, created = VehiclePlate.objects.get_or_create(
        occupancy=occupancy, plate=plate,
        defaults={"building": building, "submitted_at": timezone.now()},
    )
    if not created and obj.status == ReviewStatus.REJECTED:
        obj.status = ReviewStatus.PENDING
        obj.reviewed_by = obj.reviewed_at = None
        obj.review_note = ""
        obj.submitted_at = timezone.now()
        obj.save()
    return obj


def revoke_plate(occupancy, plate_id):
    VehiclePlate.objects.filter(occupancy=occupancy, pk=plate_id).delete()
