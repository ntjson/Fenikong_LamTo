import tempfile
import uuid

from django.contrib.auth import get_user_model
from django.core.files.storage import storages
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings

from lamto.accounts.models import Building, ResidentOccupancy, Unit
from lamto.maintenance.models import BuildingLocation, IssueReport
from lamto.maintenance.reporting import (
    ReportClientRefConflict,
    submit_report_idempotent,
)

_TEMP = tempfile.mkdtemp(prefix="lamto-idem-")


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _TEMP}},
        "private": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _TEMP}},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class IdempotentSubmitTests(TestCase):
    def setUp(self):
        building = Building.objects.create(name="Idem B")
        self.resident = get_user_model().objects.create_user(
            email="idem-resident@example.test", password="secret", display_name="Resident"
        )
        self.unit = Unit.objects.create(building=building, label="A-1")
        ResidentOccupancy.objects.create(user=self.resident, unit=self.unit)
        self.location = BuildingLocation.objects.create(building=building, name="Lift")

    def test_first_submit_creates_then_retry_returns_same(self):
        ref = uuid.uuid4()
        report, created = submit_report_idempotent(
            self.resident, self.unit, "Lift jerks", self.location, [], ref
        )
        assert created is True
        again, created2 = submit_report_idempotent(
            self.resident, self.unit, "Lift jerks", self.location, [], ref
        )
        assert created2 is False
        assert again.pk == report.pk
        assert IssueReport.objects.filter(reporter=self.resident).count() == 1

    def test_same_ref_different_text_conflicts(self):
        ref = uuid.uuid4()
        submit_report_idempotent(self.resident, self.unit, "Lift jerks", self.location, [], ref)
        try:
            submit_report_idempotent(self.resident, self.unit, "Different text", self.location, [], ref)
            assert False, "expected ReportClientRefConflict"
        except ReportClientRefConflict:
            pass

    def test_same_ref_changed_privacy_conflicts(self):
        ref = uuid.uuid4()
        submit_report_idempotent(
            self.resident, self.unit, "Lift jerks", self.location, [], ref, is_private=False
        )
        with self.assertRaises(ReportClientRefConflict):
            submit_report_idempotent(
                self.resident, self.unit, "Lift jerks", self.location, [], ref, is_private=True
            )
