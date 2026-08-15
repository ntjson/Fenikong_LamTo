
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex

from lamto.accounts.models import (
    Building,
    ManagementMembership,
    Unit,
)
from lamto.finance.models import Proposal
from lamto.maintenance.models import (
    BuildingLocation,
    IssueReport,
    MaintenanceCase,
    TriageDecision,
)


@override_settings(ROOT_URLCONF="lamto.config.urls")
@override_settings(LANGUAGE_CODE="en-us")  # asserts English source strings
class ListPatternTests(TestCase):
    def _login(self, user, membership):
        self.client.force_login(user)
        device = TOTPDevice.objects.create(
            user=user, name="t", confirmed=True, key=random_hex()
        )
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session["active_management_id"] = membership.pk
        session.save()

    def _case_world(self, *, email_prefix="lp", **_legacy_role):
        building = Building.objects.create(name=f"List {email_prefix}")
        location = BuildingLocation.objects.create(
            building=building, name="Lobby", active=True
        )
        user = get_user_model().objects.create_user(
            email=f"{email_prefix}@example.test", password="secret", display_name="U"
        )
        membership = ManagementMembership.objects.create(user=user, building=building)
        unit = Unit.objects.create(building=building, label="A-1")
        resident = get_user_model().objects.create_user(
            email=f"{email_prefix}-r@example.test", password="secret", display_name="R"
        )
        report = IssueReport.objects.create(
            reporter=resident,
            unit=unit,
            text="x",
            selected_location=location,
            location_path_snapshot="x",
        )
        decision = TriageDecision.objects.create(
            report=report,
            operator=user,
            category="c",
            urgency="HIGH",
            location=location,
            department="Ops",
            deadline_minutes=60,
            differences={},
        )
        case = MaintenanceCase.objects.create(
            decision=decision,
            building=building,
            category="c",
            urgency="HIGH",
            location=location,
            department="Ops",
            deadline_at=timezone.now(),
            active=True,
        )
        return building, location, user, membership, case

    def test_case_list_filters_active_cases_by_urgency(self):
        building, location, user, membership, high_case = self._case_world(
            email_prefix="cases",
        )
        # Second case with LOW urgency (needs its own decision for OneToOne).
        unit2 = Unit.objects.create(building=building, label="B-2")
        resident2 = get_user_model().objects.create_user(
            email="cases-r2@example.test", password="secret", display_name="R2"
        )
        report2 = IssueReport.objects.create(
            reporter=resident2,
            unit=unit2,
            text="low",
            selected_location=location,
            location_path_snapshot="low",
        )
        decision2 = TriageDecision.objects.create(
            report=report2,
            operator=user,
            category="c",
            urgency="LOW",
            location=location,
            department="Ops",
            deadline_minutes=60,
            differences={},
        )
        low_case = MaintenanceCase.objects.create(
            decision=decision2,
            building=building,
            category="c",
            urgency="LOW",
            location=location,
            department="Ops",
            deadline_at=timezone.now(),
            active=True,
        )
        self._login(user, membership)

        all_resp = self.client.get(reverse("web:case-list"))
        self.assertEqual(all_resp.status_code, 200)
        self.assertContains(all_resp, "queue-toolbar")
        self.assertContains(all_resp, f"Case #{high_case.pk}")
        self.assertContains(all_resp, f"Case #{low_case.pk}")

        filtered = self.client.get(reverse("web:case-list"), {"status": "HIGH"})
        self.assertContains(filtered, f"Case #{high_case.pk}")
        self.assertNotContains(filtered, f"Case #{low_case.pk}")

        cleared = self.client.get(reverse("web:case-list"))
        self.assertContains(cleared, f"Case #{low_case.pk}")

        urgent = self.client.get(reverse("web:case-list"), {"status": "urgent"})
        self.assertContains(urgent, f"Case #{high_case.pk}")
        self.assertNotContains(urgent, f"Case #{low_case.pk}")
        self.assertContains(urgent, "Routine")
        self.assertContains(urgent, "Urgent")

    def test_proposal_list_filters_by_status(self):
        building, _loc, user, membership, case = self._case_world(
            email_prefix="prop",
        )
        draft = Proposal.objects.create(
            case=case,
            creator_membership=membership,
            status=Proposal.Status.DRAFT,
        )
        report2 = IssueReport.objects.create(
            reporter=case.decision.report.reporter,
            unit=case.decision.report.unit,
            text="y",
            selected_location=case.location,
            location_path_snapshot="y",
        )
        decision2 = TriageDecision.objects.create(
            report=report2, operator=user, category="c", urgency="HIGH",
            location=case.location, department="Ops", deadline_minutes=60,
        )
        case2 = MaintenanceCase.objects.create(
            decision=decision2, building=building, category="c", urgency="HIGH",
            location=case.location, department="Ops", deadline_at=timezone.now(),
        )
        in_review = Proposal.objects.create(
            case=case2,
            creator_membership=membership,
            status=Proposal.Status.PUBLISHED,
        )
        self._login(user, membership)

        all_resp = self.client.get(reverse("web:proposal-list"))
        self.assertEqual(all_resp.status_code, 200)
        self.assertContains(all_resp, "queue-toolbar")
        self.assertContains(all_resp, f"Proposal #{draft.pk}")
        self.assertContains(all_resp, f"Proposal #{in_review.pk}")

        filtered = self.client.get(
            reverse("web:proposal-list"), {"status": Proposal.Status.DRAFT}
        )
        self.assertContains(filtered, f"Proposal #{draft.pk}")
        self.assertNotContains(filtered, f"Proposal #{in_review.pk}")

        review = self.client.get(
            reverse("web:proposal-list"), {"status": Proposal.Status.PUBLISHED}
        )
        self.assertNotContains(review, f"Proposal #{draft.pk}")
        self.assertContains(review, f"Proposal #{in_review.pk}")
        self.assertIn('id="record-filter"', review.content.decode())
        self.assertTrue(
            'Status' in review.content.decode() or 'Trạng thái' in review.content.decode()
        )
        body = review.content.decode()
        for en, vi in (
            ("Draft", "Nháp"),
            ("Published", "Đã công bố"),
            ("Not proceeding", "Không triển khai"),
            ("In progress", "Đang thực hiện"),
            ("Completed", "Hoàn tất"),
            ("Closed", "Đã đóng"),
        ):
            self.assertTrue(en in body or vi in body, en)
        self.assertNotContains(review, "Review and decide")
        self.assertNotContains(review, "Authorized")
