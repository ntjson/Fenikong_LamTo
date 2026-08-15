from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from lamto.accounts.models import Building, ResidentOccupancy, Unit
from lamto.maintenance.models import (
    BuildingLocation,
    IssueReport,
    MaintenanceCase,
    TriageDecision,
)
from lamto.maintenance.reporting import submit_report


class CompositeTenantFkTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.building_a = Building.objects.create(name="Composite A")
        cls.building_b = Building.objects.create(name="Composite B")
        cls.unit_a = Unit.objects.create(building=cls.building_a, label="CA-1")
        cls.loc_a = BuildingLocation.objects.create(building=cls.building_a, name="A Lobby")
        cls.loc_b = BuildingLocation.objects.create(building=cls.building_b, name="B Lobby")
        cls.resident = get_user_model().objects.create_user(
            email="composite@example.test", password="x", display_name="C"
        )
        ResidentOccupancy.objects.create(user=cls.resident, unit=cls.unit_a)

    def test_submit_report_stamps_building(self):
        with transaction.atomic():
            report = submit_report(self.resident, self.unit_a, "TEST leak", self.loc_a, [])
        assert report.building_id == self.building_a.pk

    def test_report_with_cross_building_location_rejected_by_db(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                IssueReport.objects.create(
                    reporter=self.resident,
                    unit=self.unit_a,
                    building=self.building_a,
                    text="TEST cross",
                    selected_location=self.loc_b,
                    location_path_snapshot="x",
                )

    def test_case_with_cross_building_location_rejected_by_db(self):
        with transaction.atomic():
            report = submit_report(self.resident, self.unit_a, "TEST case", self.loc_a, [])
        decision = TriageDecision.objects.create(
            report=report,
            operator=self.resident,
            category="c",
            urgency="LOW",
            location=self.loc_a,
            department="d",
            deadline_minutes=60,
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                MaintenanceCase.objects.create(
                    decision=decision,
                    building=self.building_a,
                    category="c",
                    urgency="LOW",
                    location=self.loc_b,
                    department="d",
                    deadline_at=timezone.now(),
                )
