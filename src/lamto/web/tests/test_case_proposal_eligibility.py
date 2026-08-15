from datetime import timedelta
import time

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex

from lamto.accounts.models import Building, ManagementMembership, Unit, User
from lamto.accounts.security import RECENT_REAUTH_KEY
from lamto.maintenance.cases import start_case_work
from lamto.maintenance.models import (
    BuildingLocation, CaseReport, IssueReport, MaintenanceCase, TriageDecision,
)
from lamto.web.action_inbox import action_items_for


class CaseProposalEligibilityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.building = Building.objects.create(name="Eligibility")
        cls.unit = Unit.objects.create(building=cls.building, label="A-1")
        cls.location = BuildingLocation.objects.create(building=cls.building, name="Lobby")
        cls.manager = User.objects.create_user(email="elig-m@example.test", password="pw")
        cls.membership = ManagementMembership.objects.create(user=cls.manager, building=cls.building)

    def _case(self, suffix, *, private=False):
        resident = User.objects.create_user(email=f"elig-{suffix}@example.test", password="pw")
        report = IssueReport.objects.create(
            reporter=resident, unit=self.unit, text=suffix, selected_location=self.location,
            location_path_snapshot="Eligibility / Lobby", is_private=private,
            status=IssueReport.Status.IN_REVIEW,
        )
        decision = TriageDecision.objects.create(
            report=report, operator=self.manager, category="General", urgency="HIGH",
            location=self.location, department="Ops", deadline_minutes=60,
        )
        case = MaintenanceCase.objects.create(
            decision=decision, building=self.building, category="General", urgency="HIGH",
            location=self.location, department="Ops",
            deadline_at=timezone.now() + timedelta(hours=1),
        )
        CaseReport.objects.create(case=case, report=report, grouped_by=self.manager)
        return case

    def test_only_public_spending_candidate_is_offered(self):
        eligible = self._case("spend")
        private = self._case("private", private=True)
        no_spend = self._case("no-spend")
        start_case_work(no_spend, self.manager)

        candidate_ids = {
            item.target_id for item in action_items_for(self.membership)
            if item.kind == "proposal_create"
        }
        self.assertEqual(candidate_ids, {eligible.pk})

        self.client.force_login(self.manager)
        device = TOTPDevice.objects.create(user=self.manager, name="t", confirmed=True, key=random_hex())
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session[RECENT_REAUTH_KEY] = time.time()
        session["active_management_id"] = self.membership.pk
        session.save()
        for case, offered in ((eligible, True), (private, False), (no_spend, False)):
            response = self.client.get(reverse("web:case-detail", kwargs={"pk": case.pk}))
            self.assertEqual(response.status_code, 200)
            body = response.content.decode()
        has_create = (
            "Create spending proposal" in body or "Tạo đề xuất chi" in body
        )
        self.assertEqual(has_create, offered)
