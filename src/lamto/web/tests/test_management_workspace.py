from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.utils import translation

from lamto.accounts.models import Building, ManagementMembership, ResidentOccupancy, Unit
from lamto.maintenance.models import BuildingLocation, IssueReport, MaintenanceCase, TriageDecision
from lamto.testing.factories import PilotDomainDriver, seed_pilot_world
from lamto.web.forms.staff import ConfirmTriageForm
from lamto.web.forms.staff import RecordSettlementForm


@override_settings(LANGUAGE_CODE="en-us")  # asserts English source strings
class ManagementWorkspaceTests(TestCase):
    def test_triage_queue_field_is_labeled_management_queue(self):
        self.assertEqual(ConfirmTriageForm().fields["management_queue"].label, "Management queue")

    def authenticate_management(self, membership):
        self.client.force_login(membership.user)

    def login_management(self):
        user = get_user_model().objects.create_user(
            email="manager@example.test", password="secret", display_name="Manager"
        )
        membership = ManagementMembership.objects.create(
            user=user, building=Building.objects.create(name="Tower")
        )
        self.authenticate_management(membership)
        return membership

    def test_management_can_open_every_navigation_area(self):
        membership = self.login_management()
        for name in (
            "staff-home",
            "action-inbox",
            "case-list",
            "proposal-list",
            "settlement-list",
            "export-home",
            "audit-export",
            "fund-home",
            "ops-health",
            "pilot-metrics",
            "standalone-proposal-create",
        ):
            with self.subTest(name=name):
                self.assertEqual(
                    self.client.get(reverse(f"web:{name}"), follow=True).status_code,
                    200,
                )
        inbox = self.client.get(reverse("web:action-inbox"))
        self.assertContains(inbox, f"Work assigned to Management at {membership.building.name}.")

    def test_resident_only_user_is_denied_management_routes(self):
        user = get_user_model().objects.create_user(
            email="resident@example.test", password="secret", display_name="Resident"
        )
        building = Building.objects.create(name="Resident Tower")
        ResidentOccupancy.objects.create(
            user=user,
            unit=Unit.objects.create(building=building, label="R-1"),
            active=True,
        )
        self.assertFalse(ManagementMembership.objects.filter(user=user).exists())
        self.client.force_login(user)
        for path in ("/s/", "/s/cases/", "/s/settlements/"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 403)

    def test_case_detail_renders(self):
        membership = self.login_management()
        location = BuildingLocation.objects.create(
            building=membership.building, name="Lobby", active=True
        )
        resident = get_user_model().objects.create_user(
            email="reporter@example.test", password="secret", display_name="Reporter"
        )
        report = IssueReport.objects.create(
            reporter=resident,
            unit=Unit.objects.create(building=membership.building, label="A-1"),
            text="Elevator shakes",
            selected_location=location,
            location_path_snapshot="Tower / Lobby",
        )
        decision = TriageDecision.objects.create(
            report=report,
            operator=membership.user,
            category="Elevator",
            urgency="HIGH",
            location=location,
            management_queue="GENERAL",
            deadline_minutes=120,
            differences={},
        )
        case = MaintenanceCase.objects.create(
            decision=decision,
            building=membership.building,
            category="Elevator",
            urgency="HIGH",
            location=location,
            management_queue="GENERAL",
            deadline_at=timezone.now(),
            active=True,
        )

        response = self.client.get(reverse("web:case-detail", kwargs={"pk": case.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Case #{case.pk}")

    def test_report_info_and_decline_actions(self):
        membership = self.login_management()
        location = BuildingLocation.objects.create(building=membership.building, name="Lobby")
        resident = get_user_model().objects.create_user(
            email="outcomes@example.test", password="secret", display_name="Resident"
        )
        unit = Unit.objects.create(building=membership.building, label="A-2")
        report = IssueReport.objects.create(
            reporter=resident, unit=unit, building=membership.building, text="Leak",
            selected_location=location, location_path_snapshot="Tower / Lobby",
            status=IssueReport.Status.IN_REVIEW,
        )
        url = reverse("web:staff-report-detail", kwargs={"pk": report.pk})
        self.client.post(url, {"action": "request_info", "message": "Which tap?"})
        report.refresh_from_db()
        self.assertEqual(report.status, IssueReport.Status.NEEDS_INFO)
        report.info_requests.update(resolved_at=timezone.now())
        self.client.post(url, {"action": "decline", "reason": "Already repaired", "confirm": "on"})
        report.refresh_from_db()
        self.assertEqual(report.status, IssueReport.Status.DECLINED)
        self.assertEqual(report.declined_reason, "Already repaired")

    def test_failed_triage_binds_only_triage_form(self):
        membership = self.login_management()
        location = BuildingLocation.objects.create(building=membership.building, name="Lobby")
        resident = get_user_model().objects.create_user(email="forms@example.test", password="secret")
        report = IssueReport.objects.create(
            reporter=resident, unit=Unit.objects.create(building=membership.building, label="A-3"),
            building=membership.building, text="Leak", selected_location=location,
            location_path_snapshot="Tower / Lobby", status=IssueReport.Status.IN_REVIEW,
        )

        response = self.client.post(reverse("web:staff-report-detail", args=[report.pk]), {
            "action": "confirm_triage", "category": "Plumbing", "urgency": "HIGH",
            "management_queue": "GENERAL", "deadline_minutes": 60,
        })

        self.assertTrue(response.context["form"].is_bound)
        self.assertFalse(response.context["info_form"].is_bound)
        self.assertFalse(response.context["decline_form"].is_bound)

    def test_settlement_form_accepts_a_new_upload_in_the_same_post(self):
        self.assertIn("proof_upload", RecordSettlementForm().fields)

    def test_manager_can_reach_the_payment_step(self):
        seed = seed_pilot_world(
            building_name="Payment Tower",
            email_prefix="workspace-payment",
            create_opening_fund=False,
        )
        driver = PilotDomainDriver(seed)
        driver.confirm_triage_case()
        driver.publish_proposal()
        driver.complete_assigned_work()
        settlement = driver.record_settlement()
        (manager,) = seed.management_memberships

        self.authenticate_management(manager)

        detail = self.client.get(reverse("web:settlement-detail", kwargs={"pk": settlement.pk}))
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.context["membership"], manager)
        self.assertEqual(detail.context["settlement"], settlement)

    def test_settlement_rows_lead_with_next_action(self):
        with translation.override("en"):
            html = render_to_string(
                "web/staff/settlement_detail.html",
                {
                    "list_mode": True,
                    "pending": [],
                    "settlements": [SimpleNamespace(pk=7, amount_vnd=250_000)],
                },
            )

        self.assertIn('<span class="task-action">Review settlement</span>', html)
        self.assertIn("Settlement #7", html)
