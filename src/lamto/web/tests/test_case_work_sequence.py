"""The case page offers work actions in the order the domain accepts them.

The page used to render Start work and the Publish progress form side by side
with nothing gating either, so a case could be completed in one click without
ever being started — and, because ``spending_proposal_cases()`` drops cases
whose reports have moved on, without any chance of ever proposing the spend.
"""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from lamto.accounts.models import Building, ManagementMembership, Unit, User
from lamto.maintenance.cases import start_case_work
from lamto.maintenance.models import (
    BuildingLocation, CaseReport, IssueReport, MaintenanceCase, TriageDecision,
)


class CaseWorkSequenceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.building = Building.objects.create(name="Sequence")
        cls.unit = Unit.objects.create(building=cls.building, label="A-1")
        cls.location = BuildingLocation.objects.create(building=cls.building, name="Lift")
        cls.manager = User.objects.create_user(email="seq-m@example.test", password="pw")
        cls.membership = ManagementMembership.objects.create(
            user=cls.manager, building=cls.building
        )

    def setUp(self):
        self.client.force_login(self.manager)
        session = self.client.session
        session["active_management_id"] = self.membership.pk
        session.save()

    def _case(self, suffix="a"):
        resident = User.objects.create_user(email=f"seq-{suffix}@example.test", password="pw")
        report = IssueReport.objects.create(
            reporter=resident, unit=self.unit, text="lift stuck",
            selected_location=self.location, location_path_snapshot="Sequence / Lift",
            status=IssueReport.Status.IN_REVIEW,
        )
        decision = TriageDecision.objects.create(
            report=report, operator=self.manager, category="Elevator", urgency="HIGH",
            location=self.location, management_queue="GENERAL", deadline_minutes=60,
        )
        case = MaintenanceCase.objects.create(
            decision=decision, building=self.building, category="Elevator", urgency="HIGH",
            location=self.location, management_queue="GENERAL",
            deadline_at=timezone.now() + timedelta(hours=1),
        )
        CaseReport.objects.create(case=case, report=report, grouped_by=self.manager)
        return case, report

    def _url(self, case):
        return reverse("web:case-detail", kwargs={"pk": case.pk})

    def test_unstarted_case_offers_start_work_only(self):
        case, _ = self._case("unstarted")
        body = self.client.get(self._url(case)).content.decode()
        self.assertIn('value="start_work"', body)
        self.assertNotIn('value="publish_progress"', body)
        self.assertNotIn('value="complete_work"', body)

    def test_started_case_offers_progress_and_completion(self):
        case, _ = self._case("started")
        start_case_work(case, self.manager)
        body = self.client.get(self._url(case)).content.decode()
        self.assertNotIn('value="start_work"', body)
        self.assertIn('value="publish_progress"', body)
        self.assertIn('value="complete_work"', body)

    def test_completing_an_unstarted_case_is_refused(self):
        case, report = self._case("posted")
        response = self.client.post(
            self._url(case),
            {"action": "complete_work", "cause": "worn cable", "result": "replaced"},
            follow=True,
        )
        case.refresh_from_db(); report.refresh_from_db()
        self.assertIsNone(case.completed_at)
        self.assertEqual(case.updates.count(), 0)
        self.assertEqual(report.status, IssueReport.Status.IN_REVIEW)
        self.assertContains(response, "Tạo đề xuất chi")

    def test_publishing_progress_on_an_unstarted_case_is_refused(self):
        case, _ = self._case("progress")
        self.client.post(
            self._url(case),
            {"action": "publish_progress", "cause": "looked", "result": "saw"},
            follow=True,
        )
        self.assertEqual(case.updates.count(), 0)
