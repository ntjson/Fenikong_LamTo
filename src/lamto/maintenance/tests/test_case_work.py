from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from lamto.accounts.models import Building, ManagementMembership, ResidentOccupancy, Unit, User
from lamto.maintenance.cases import (
    close_expired_completed_cases, complete_case_work, publish_progress, start_case_work,
)
from lamto.maintenance.models import (
    BuildingLocation, CaseReport, IssueReport, MaintenanceCase, TriageDecision,
)
from lamto.maintenance.ratings import rate_completed_case


class CaseWorkTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.building = Building.objects.create(name="B1")
        cls.unit = Unit.objects.create(building=cls.building, label="A-101")
        cls.location = BuildingLocation.objects.create(building=cls.building, name="Lobby")
        cls.resident = User.objects.create_user(email="r@x.vn", password="pw", display_name="R")
        ResidentOccupancy.objects.create(user=cls.resident, unit=cls.unit)
        cls.manager = User.objects.create_user(email="m@x.vn", password="pw", display_name="M")
        ManagementMembership.objects.create(user=cls.manager, building=cls.building)

    def _case(self):
        report = IssueReport.objects.create(
            reporter=self.resident, unit=self.unit, text="Leak",
            selected_location=self.location, location_path_snapshot="B1 / Lobby",
            status=IssueReport.Status.IN_REVIEW,
        )
        decision = TriageDecision.objects.create(
            report=report, operator=self.manager, category="Plumbing", urgency="HIGH",
            location=self.location, department="Water", deadline_minutes=1440,
        )
        case = MaintenanceCase.objects.create(
            decision=decision, building=self.building, category="Plumbing",
            urgency="HIGH", location=self.location, department="Water",
            deadline_at=timezone.now() + timedelta(days=1),
        )
        CaseReport.objects.create(case=case, report=report, grouped_by=self.manager)
        return case, report

    def test_c_path_start_progress_complete_rate(self):
        case, report = self._case()
        start_case_work(case, self.manager)
        report.refresh_from_db()
        self.assertEqual(report.status, IssueReport.Status.IN_PROGRESS)
        publish_progress(case, self.manager, "Opened wall", "Found burst pipe")
        self.assertEqual(case.updates.count(), 1)
        self.assertEqual(case.updates.first().author, self.manager)
        complete_case_work(case, self.manager, "Replaced pipe", "Water restored")
        case.refresh_from_db(); report.refresh_from_db()
        self.assertIsNotNone(case.completed_at)
        self.assertEqual(report.status, IssueReport.Status.COMPLETED)
        rating = rate_completed_case(self.resident, case, satisfied=True, comment="OK")
        self.assertTrue(rating.satisfied)
        report.refresh_from_db(); case.refresh_from_db()
        self.assertEqual(report.status, IssueReport.Status.CLOSED)
        self.assertIsNotNone(case.closed_at)

    def test_cannot_rate_before_completion(self):
        case, _ = self._case(); start_case_work(case, self.manager)
        with self.assertRaises(ValidationError):
            rate_completed_case(self.resident, case, satisfied=False)

    def test_fourteen_day_auto_close(self):
        case, report = self._case(); start_case_work(case, self.manager)
        complete_case_work(case, self.manager, "Done", "Done")
        MaintenanceCase.objects.filter(pk=case.pk).update(completed_at=timezone.now() - timedelta(days=15))
        self.assertEqual(close_expired_completed_cases(), 1)
        report.refresh_from_db(); case.refresh_from_db()
        self.assertEqual(report.status, IssueReport.Status.CLOSED)
        self.assertIsNotNone(case.closed_at)

    def test_progress_requires_active_uncompleted_case(self):
        case, _ = self._case(); start_case_work(case, self.manager)
        complete_case_work(case, self.manager, "Done", "Done")
        with self.assertRaises(ValidationError):
            publish_progress(case, self.manager, "More", "Work")
