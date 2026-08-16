import re

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from lamto.accounts.models import Building, Unit
from lamto.documents.models import DocumentVersion


class CaseCategory(models.TextChoices):
    ELEVATOR = "ELEVATOR", _("Elevator")
    WATER_LEAK = "WATER_LEAK", _("Water leak")
    ELECTRICAL_FAULT = "ELECTRICAL_FAULT", _("Electrical fault")
    HEATING_COOLING = "HEATING_COOLING", _("Heating / cooling")
    LIGHTING = "LIGHTING", _("Lighting")
    DOOR_LOCK = "DOOR_LOCK", _("Door / lock")
    APPLIANCE = "APPLIANCE", _("Appliance")
    STRUCTURAL = "STRUCTURAL", _("Structural")
    CLEANLINESS = "CLEANLINESS", _("Cleanliness")
    NOISE = "NOISE", _("Noise")
    OTHER = "OTHER", _("Other")


class ManagementQueue(models.TextChoices):
    """The team that handles a case (ADR 0003).

    Closed, like CaseCategory, so the label can be Vietnamese and the assistant
    cannot invent a queue by spelling one differently.
    """

    MAINTENANCE = "MAINTENANCE", _("Maintenance")
    PLUMBING = "PLUMBING", _("Plumbing")
    ELECTRICAL = "ELECTRICAL", _("Electrical")
    ELEVATOR = "ELEVATOR", _("Elevator")
    HVAC = "HVAC", _("HVAC")
    CLEANING = "CLEANING", _("Cleaning")
    SECURITY = "SECURITY", _("Security")
    LANDSCAPING = "LANDSCAPING", _("Landscaping")
    PEST_CONTROL = "PEST_CONTROL", _("Pest control")
    GENERAL = "GENERAL", _("General")


def normalize_category(value):
    """Map a code or legacy free-text label to a CaseCategory code (OTHER if unknown)."""
    code = re.sub(r"[^A-Z0-9]+", "_", str(value).upper()).strip("_")
    return code if code in CaseCategory.values else CaseCategory.OTHER.value


def normalize_management_queue(value):
    """Map a code or legacy free-text label to a queue code (GENERAL if unknown)."""
    code = re.sub(r"[^A-Z0-9]+", "_", str(value).upper()).strip("_")
    return code if code in ManagementQueue.values else ManagementQueue.GENERAL.value


class BuildingLocation(models.Model):
    building = models.ForeignKey(Building, on_delete=models.PROTECT)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["building", "parent", "name"],
                name="location_sibling_name_once",
                nulls_distinct=False,
            ),
            models.UniqueConstraint(fields=["id", "building"], name="location_id_building_key"),
        ]

    def clean(self):
        super().clean()
        if self.parent_id and self.parent.building_id != self.building_id:
            raise ValidationError({"parent": "Parent location must belong to the same building."})

    def __str__(self):
        return self.name

    @property
    def path_label(self):
        names = []
        location = self
        seen_locations = set()
        for _ in range(100):
            if location is None:
                return " / ".join([self.building.name, *reversed(names)])
            if location.pk in seen_locations:
                raise ValidationError("Location hierarchy contains a cycle.")
            seen_locations.add(location.pk)
            names.append(location.name)
            location = location.parent
        raise ValidationError("Location hierarchy exceeds the maximum depth.")


class IssueReport(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED", _("Submitted")
        IN_REVIEW = "IN_REVIEW", _("In review")
        NEEDS_INFO = "NEEDS_INFO", _("Needs information")
        DECLINED = "DECLINED", _("Declined")
        IN_PROGRESS = "IN_PROGRESS", _("In progress")
        PROPOSED = "PROPOSED", _("Proposed")
        COMPLETED = "COMPLETED", _("Completed")
        CLOSED = "CLOSED", _("Closed")

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    building = models.ForeignKey(
        Building, on_delete=models.PROTECT,
        editable=False, related_name="issue_reports",
    )
    text = models.TextField()
    selected_location = models.ForeignKey(BuildingLocation, on_delete=models.PROTECT)
    location_path_snapshot = models.CharField(max_length=1000)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SUBMITTED)
    is_private = models.BooleanField(default=False)
    declined_reason = models.TextField(blank=True)
    declined_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.PROTECT, related_name="declined_reports",
    )
    declined_at = models.DateTimeField(null=True, blank=True)
    client_ref = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["reporter", "client_ref"],
                condition=models.Q(client_ref__isnull=False),
                name="report_client_ref_once",
            )
        ]

    def save(self, *args, **kwargs):
        # Always stamp building from unit so ORM creates (and composite FKs)
        # stay consistent even when callers omit the denormalized column.
        if self.unit_id is not None:
            unit_building_id = getattr(self.unit, "building_id", None)
            if unit_building_id is None:
                unit_building_id = Unit.objects.filter(pk=self.unit_id).values_list(
                    "building_id", flat=True
                ).first()
            self.building_id = unit_building_id
        return super().save(*args, **kwargs)


class ReportPhoto(models.Model):
    report = models.ForeignKey(IssueReport, on_delete=models.PROTECT, related_name="photos")
    version = models.ForeignKey(DocumentVersion, on_delete=models.PROTECT)
    # Denormalized content digest for DB-level same-bytes idempotency per report
    # (unique with report). Populated from version.sha256 on create.
    content_sha = models.CharField(max_length=64)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["report", "version"], name="report_photo_once"),
            models.UniqueConstraint(
                fields=["report", "content_sha"], name="report_photo_content_sha_once"
            ),
        ]


class TriageJob(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        PROCESSING = "PROCESSING", _("Processing")
        SUCCEEDED = "SUCCEEDED", _("Succeeded")
        NEEDS_MANUAL = "NEEDS_MANUAL", _("Needs manual triage")

    report = models.OneToOneField(IssueReport, on_delete=models.PROTECT, related_name="triage_job")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    failure_reason = models.CharField(max_length=255, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)


class TriageSuggestion(models.Model):
    job = models.OneToOneField(TriageJob, on_delete=models.PROTECT, related_name="suggestion")
    category = models.CharField(max_length=128, choices=CaseCategory.choices)
    interpreted_location = models.CharField(max_length=1000)
    urgency = models.CharField(max_length=16)
    confidence_percent = models.PositiveSmallIntegerField()
    duplicate_report_ids = models.JSONField(default=list)
    management_queue = models.CharField(max_length=32, choices=ManagementQueue.choices)
    deadline_minutes = models.PositiveIntegerField()
    missing_information = models.JSONField(default=list)
    raw_response = models.JSONField()
    provider_request_id = models.CharField(max_length=255)
    validation_metadata = models.JSONField(default=dict)
    elapsed_ms = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class TriageDecision(models.Model):
    report = models.OneToOneField(IssueReport, on_delete=models.PROTECT, related_name="triage_decision")
    suggestion = models.ForeignKey(TriageSuggestion, null=True, blank=True, on_delete=models.PROTECT)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    category = models.CharField(max_length=128, choices=CaseCategory.choices)
    urgency = models.CharField(max_length=16)
    location = models.ForeignKey(BuildingLocation, on_delete=models.PROTECT)
    management_queue = models.CharField(max_length=32, choices=ManagementQueue.choices)
    deadline_minutes = models.PositiveIntegerField()
    differences = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class MaintenanceCase(models.Model):
    decision = models.OneToOneField(TriageDecision, on_delete=models.PROTECT, related_name="case")
    building = models.ForeignKey(Building, on_delete=models.PROTECT)
    category = models.CharField(max_length=128, choices=CaseCategory.choices)
    urgency = models.CharField(max_length=16)
    location = models.ForeignKey(BuildingLocation, on_delete=models.PROTECT)
    management_queue = models.CharField(max_length=32, choices=ManagementQueue.choices)
    deadline_at = models.DateTimeField()
    active = models.BooleanField(default=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    reports = models.ManyToManyField(IssueReport, through="CaseReport", related_name="maintenance_cases")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def verification_label(self):
        try:
            proposal = self.proposal
        except ObjectDoesNotExist:
            return None
        version = getattr(proposal, "current_version", None) if proposal else None
        if version is None:
            return None
        return version.verification_label


class CaseReport(models.Model):
    case = models.ForeignKey(MaintenanceCase, on_delete=models.PROTECT, related_name="case_reports")
    report = models.ForeignKey(IssueReport, on_delete=models.PROTECT, related_name="case_reports")
    grouped_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["case", "report"], name="case_report_once")
        ]


class InfoRequest(models.Model):
    """Outcome A: one simple information-request loop per report at a time."""

    report = models.ForeignKey(IssueReport, on_delete=models.PROTECT, related_name="info_requests")
    message = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    reply_text = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["report"],
                condition=models.Q(resolved_at__isnull=True),
                name="one_open_info_request_per_report",
            )
        ]


class AppendOnlyModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Work updates are append-only.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Work updates are append-only.")


class WorkUpdate(AppendOnlyModel):
    case = models.ForeignKey(MaintenanceCase, null=True, blank=True, on_delete=models.PROTECT, related_name="updates")
    proposal = models.ForeignKey("finance.Proposal", null=True, blank=True, on_delete=models.PROTECT, related_name="updates")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.PROTECT, related_name="work_updates",
    )
    cause = models.TextField()
    result = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.CheckConstraint(
            condition=(models.Q(case__isnull=False, proposal__isnull=True) | models.Q(case__isnull=True, proposal__isnull=False)),
            name="work_update_case_xor_proposal",
        )]


class CompletionRating(models.Model):
    resident = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="completion_ratings",
    )
    case = models.ForeignKey(
        MaintenanceCase,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="completion_ratings",
    )
    proposal = models.ForeignKey(
        "finance.Proposal", null=True, blank=True, on_delete=models.PROTECT,
        related_name="completion_ratings",
    )
    satisfied = models.BooleanField()
    comment = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["resident", "case"],
                condition=models.Q(case__isnull=False),
                name="completion_rating_once_per_resident_case",
            ),
            models.UniqueConstraint(
                fields=["resident", "proposal"], condition=models.Q(proposal__isnull=False),
                name="completion_rating_once_per_resident_proposal",
            ),
            models.CheckConstraint(
                condition=(models.Q(case__isnull=False, proposal__isnull=True) | models.Q(case__isnull=True, proposal__isnull=False)),
                name="completion_rating_case_xor_proposal",
            ),
        ]
