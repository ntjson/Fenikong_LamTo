"""Gate recognition records: enrolments, readers, and short-lived events.

Retention is the defining constraint. ``GateEvent`` rows are deleted whole
``GATE_EVENT_RETENTION_HOURS`` after ``occurred_at``; the pending review photo
has its own, independent TTL. Nothing in this app writes to ``lamto.audit`` —
a 24-hour event that leaves a permanent audit row is not a 24-hour event.

No gate capture image is ever stored. The only image that touches storage is
the enrolment review photo, and it lives until a manager decides or the TTL
expires, whichever comes first.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.utils import timezone

from lamto.accounts.models import Building, ResidentOccupancy


class ReviewStatus(models.TextChoices):
    PENDING = "PENDING", _("Pending review")
    APPROVED = "APPROVED", _("Approved")
    REJECTED = "REJECTED", _("Rejected")
    EXPIRED = "EXPIRED", _("Expired before review")


class FaceEnrollment(models.Model):
    """One face per resident occupancy.

    ``embedding`` holds a Fernet-sealed float32 vector. A rejected or expired
    enrolment keeps its row so the resident can read the reason, but the
    check constraint makes it impossible for that row to still hold a vector.
    """

    occupancy = models.OneToOneField(
        ResidentOccupancy, on_delete=models.CASCADE, related_name="face_enrollment"
    )
    embedding = models.BinaryField(
        null=True,
        blank=True,
        help_text="Fernet-sealed float32 vector; NULL once deleted.",
    )
    model_name = models.CharField(max_length=64, blank=True)
    model_version = models.CharField(max_length=64, blank=True)
    status = models.CharField(
        max_length=16, choices=ReviewStatus.choices, default=ReviewStatus.PENDING
    )
    submitted_at = models.DateTimeField(default=timezone.now)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    ~Q(status__in=[ReviewStatus.REJECTED, ReviewStatus.EXPIRED])
                    | Q(embedding__isnull=True)
                ),
                name="gate_no_embedding_when_not_live",
            )
        ]

    def __str__(self):
        return f"FaceEnrollment(occupancy={self.occupancy_id}, status={self.status})"


class VehiclePlate(models.Model):
    """A plate claimed by one occupancy. Many rows per resident is the feature.

    ``building`` is denormalized from ``occupancy.unit.building`` so the
    approved-uniqueness constraint can be expressed without an FK traversal.
    """

    occupancy = models.ForeignKey(
        ResidentOccupancy, on_delete=models.CASCADE, related_name="vehicle_plates"
    )
    building = models.ForeignKey(
        Building, on_delete=models.PROTECT, related_name="vehicle_plates"
    )
    plate = models.CharField(max_length=12, help_text="Normalized form only.")
    status = models.CharField(
        max_length=16, choices=ReviewStatus.choices, default=ReviewStatus.PENDING
    )
    submitted_at = models.DateTimeField(default=timezone.now)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["occupancy", "plate"], name="gate_plate_once_per_occupancy"
            ),
            models.UniqueConstraint(
                fields=["building", "plate"],
                condition=Q(status=ReviewStatus.APPROVED),
                name="gate_approved_plate_once_per_building",
            ),
        ]

    def __str__(self):
        return f"VehiclePlate({self.plate}, status={self.status})"


class PendingEnrollmentPhoto(models.Model):
    """The review image. Lives until a decision or ``expires_at``, never longer.

    ``provider_version_id`` matters: the private bucket is versioned, so a
    plain delete leaves a delete marker and keeps the object. Deletion must
    name the version.
    """

    enrollment = models.OneToOneField(
        FaceEnrollment, on_delete=models.CASCADE, related_name="pending_photo"
    )
    storage_key = models.CharField(max_length=512, unique=True)
    provider_version_id = models.CharField(max_length=512, blank=True)
    content_type = models.CharField(max_length=127)
    byte_size = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)


class PhotoDeletion(models.Model):
    """Durable storage deletion queued in the same transaction as its metadata change."""

    storage_key = models.CharField(max_length=512, unique=True)
    provider_version_id = models.CharField(max_length=512, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class GateDevice(models.Model):
    """A reader. Direction is declared, because one camera cannot infer it."""

    class Direction(models.TextChoices):
        ENTRY = "ENTRY", _("Entry")
        EXIT = "EXIT", _("Exit")

    building = models.ForeignKey(
        Building, on_delete=models.PROTECT, related_name="gate_devices"
    )
    label = models.CharField(max_length=120)
    direction = models.CharField(max_length=8, choices=Direction.choices)
    active = models.BooleanField(default=True)
    last_seen_hour = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "Truncated to the hour on purpose: enough to see a reader go dark, "
            "too coarse to place anyone at the gate."
        ),
    )

    def __str__(self):
        return f"{self.label} ({self.direction})"


class GateDeviceCredential(models.Model):
    """A reader token. Only the SHA-256 digest is stored.

    Rotation issues a new row and sets the previous row's ``expires_at`` to
    now + grace, so a device is reconfigured without a lockout. Revocation
    sets ``revoked_at`` and takes effect on the next request, no grace.
    Multiple live credentials per device is the mechanism, not an accident.
    """

    device = models.ForeignKey(
        GateDevice, on_delete=models.CASCADE, related_name="credentials"
    )
    token_sha256 = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )

    def is_valid(self, now=None) -> bool:
        now = now or timezone.now()
        if self.revoked_at is not None:
            return False
        return self.expires_at is None or self.expires_at > now


class GateEvent(models.Model):
    """One sighting. Deleted whole by the retention purge — never updated.

    Face events carry the audit metadata that makes a live match explainable
    while it is being disputed at the gate. Because the row dies within
    24-25 hours, this is not a calibration dataset.
    """

    class Kind(models.TextChoices):
        FACE = "FACE", _("Face")
        PLATE = "PLATE", _("Plate")

    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, related_name="gate_events"
    )
    device = models.ForeignKey(
        GateDevice, on_delete=models.CASCADE, related_name="events"
    )
    kind = models.CharField(max_length=8, choices=Kind.choices)
    direction = models.CharField(max_length=8, choices=GateDevice.Direction.choices)
    occurred_at = models.DateTimeField(default=timezone.now, db_index=True)
    matched_occupancy = models.ForeignKey(
        ResidentOccupancy,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="gate_events",
    )
    matched_plate = models.ForeignKey(
        VehiclePlate,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="gate_events",
    )
    raw_plate_text = models.CharField(max_length=64, blank=True)
    normalized_plate_text = models.CharField(max_length=12, blank=True)
    model_name = models.CharField(max_length=64, blank=True)
    model_version = models.CharField(max_length=64, blank=True)
    match_metric = models.CharField(max_length=16, blank=True)
    threshold_used = models.FloatField(null=True, blank=True)
    match_score = models.FloatField(null=True, blank=True)


class GatePurgeHeartbeat(models.Model):
    """Single row: when the retention job last completed successfully.

    A bare timestamp of a successful job run identifies nobody. Purge failure
    is a retention breach, so ops needs to see staleness.
    """

    last_success_at = models.DateTimeField()
    events_deleted = models.PositiveIntegerField(default=0)
    photos_deleted = models.PositiveIntegerField(default=0)
