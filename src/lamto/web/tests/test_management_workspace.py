from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.utils import translation

from lamto.accounts.models import Building, ManagementMembership, ResidentOccupancy, Unit
from lamto.maintenance.models import (
    BuildingLocation,
    IssueReport,
    MaintenanceCase,
    TriageDecision,
    WorkUpdate,
)
from lamto.testing.factories import PilotDomainDriver, seed_pilot_world
from lamto.web.forms.staff import ConfirmTriageForm
from lamto.web.forms.staff import RecordSettlementForm


@override_settings(LANGUAGE_CODE="en-us")  # asserts English source strings
class ManagementWorkspaceTests(TestCase):
    def test_triage_queue_field_is_labeled_management_queue(self):
        self.assertEqual(ConfirmTriageForm().fields["management_queue"].label, "Management queue")

    def test_confirm_triage_form_groups_locations_by_area_and_labels_whole_area(self):
        building = Building.objects.create(name="Tower A")
        floor_2 = BuildingLocation.objects.create(building=building, name="Floor 2")
        lift_b = BuildingLocation.objects.create(building=building, parent=floor_2, name="Lift B")
        stair_b = BuildingLocation.objects.create(building=building, parent=floor_2, name="Stairwell B")

        floor_1 = BuildingLocation.objects.create(building=building, name="Floor 1")
        stair_a = BuildingLocation.objects.create(building=building, parent=floor_1, name="Stairwell A")
        lift_a = BuildingLocation.objects.create(building=building, parent=floor_1, name="Lift A")

        lobby = BuildingLocation.objects.create(building=building, name="Lobby")

        inactive_floor = BuildingLocation.objects.create(building=building, name="Old Floor", active=False)
        BuildingLocation.objects.create(building=building, parent=inactive_floor, name="Old Lift", active=True)

        form = ConfirmTriageForm(building_id=building.pk)
        choices = list(form.fields["location"].choices)

        expected_choices = [
            ("", "---------"),
            (
                "Floor 1",
                [
                    (floor_1.pk, "Floor 1 (whole area)"),
                    (lift_a.pk, "Lift A"),
                    (stair_a.pk, "Stairwell A"),
                ],
            ),
            (
                "Floor 2",
                [
                    (floor_2.pk, "Floor 2 (whole area)"),
                    (lift_b.pk, "Lift B"),
                    (stair_b.pk, "Stairwell B"),
                ],
            ),
            (lobby.pk, "Lobby"),
        ]
        self.assertEqual(choices, expected_choices)

        html = str(form["location"])
        self.assertIn('<optgroup label="Floor 1">', html)
        self.assertIn(f'<option value="{floor_1.pk}">Floor 1 (whole area)</option>', html)
        self.assertIn(f'<option value="{lift_a.pk}">Lift A</option>', html)
        self.assertIn(f'<option value="{lobby.pk}">Lobby</option>', html)
        self.assertNotIn("Old Floor", html)
        self.assertNotIn("Old Lift", html)

    def test_confirm_triage_form_auto_selects_single_choice(self):
        building = Building.objects.create(name="Tower B")
        lobby = BuildingLocation.objects.create(building=building, name="Lobby")

        form = ConfirmTriageForm(building_id=building.pk)
        self.assertEqual(form.initial.get("location"), lobby.pk)

        # If an area has a place (2 selectable options), no auto-selection
        BuildingLocation.objects.create(building=building, parent=lobby, name="Desk")
        multi_form = ConfirmTriageForm(building_id=building.pk)
        self.assertIsNone(multi_form.initial.get("location"))

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

    def _create_case(self, membership, reporter_email="reporter@example.test"):
        location = BuildingLocation.objects.create(
            building=membership.building, name="Lobby", active=True
        )
        resident = get_user_model().objects.create_user(
            email=reporter_email, password="secret", display_name="Reporter"
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
        return MaintenanceCase.objects.create(
            decision=decision,
            building=membership.building,
            category="Elevator",
            urgency="HIGH",
            location=location,
            management_queue="GENERAL",
            deadline_at=timezone.now(),
            active=True,
        )

    def test_case_detail_renders_empty_progress_state(self):
        membership = self.login_management()
        case = self._create_case(membership)

        response = self.client.get(reverse("web:case-detail", kwargs={"pk": case.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Case #{case.pk}")
        self.assertContains(response, "No progress updates yet.")

    def test_case_detail_renders_with_work_updates(self):
        membership = self.login_management()
        case = self._create_case(membership, reporter_email="reporter2@example.test")
        update = WorkUpdate.objects.create(
            case=case,
            author=membership.user,
            cause="Worn traction cable",
            result="Replaced cable and tested brakes",
        )

        response = self.client.get(reverse("web:case-detail", kwargs={"pk": case.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Case #{case.pk}")
        self.assertContains(response, "Worn traction cable")
        self.assertContains(response, "Replaced cable and tested brakes")
        self.assertContains(response, membership.user.display_name)
        self.assertNotContains(response, "No progress updates yet.")

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

    def test_staff_can_triage_report_with_place_or_area_location(self):
        membership = self.login_management()
        floor_3 = BuildingLocation.objects.create(building=membership.building, name="Floor 3")
        stair_c = BuildingLocation.objects.create(building=membership.building, parent=floor_3, name="Stairwell C")
        resident = get_user_model().objects.create_user(email="triage_user@example.test", password="secret")
        report = IssueReport.objects.create(
            reporter=resident,
            unit=Unit.objects.create(building=membership.building, label="B-1"),
            building=membership.building,
            text="Broken handrail",
            selected_location=stair_c,
            location_path_snapshot="Tower / Floor 3 / Stairwell C",
            status=IssueReport.Status.SUBMITTED,
        )

        detail_url = reverse("web:staff-report-detail", args=[report.pk])
        get_res = self.client.get(detail_url)
        self.assertEqual(get_res.status_code, 200)
        self.assertContains(get_res, '<optgroup label="Floor 3">')
        self.assertContains(get_res, f'<option value="{floor_3.pk}">Floor 3 (whole area)</option>')
        self.assertContains(get_res, f'<option value="{stair_c.pk}">Stairwell C</option>')

        post_res = self.client.post(detail_url, {
            "action": "confirm_triage",
            "category": "STRUCTURAL",
            "urgency": "HIGH",
            "location": stair_c.pk,
            "management_queue": "MAINTENANCE",
            "deadline_minutes": 1440,
        })
        self.assertEqual(post_res.status_code, 302)
        case = MaintenanceCase.objects.get(reports=report)
        self.assertEqual(case.location, stair_c)
        self.assertEqual(case.decision.location, stair_c)

        # Triage another report picking the area directly
        report_area = IssueReport.objects.create(
            reporter=resident,
            unit=Unit.objects.create(building=membership.building, label="B-2"),
            building=membership.building,
            text="Floor hallway light out",
            selected_location=floor_3,
            location_path_snapshot="Tower / Floor 3",
            status=IssueReport.Status.SUBMITTED,
        )
        post_area_res = self.client.post(reverse("web:staff-report-detail", args=[report_area.pk]), {
            "action": "confirm_triage",
            "category": "LIGHTING",
            "urgency": "MEDIUM",
            "location": floor_3.pk,
            "management_queue": "ELECTRICAL",
            "deadline_minutes": 2880,
        })
        self.assertEqual(post_area_res.status_code, 302)
        area_case = MaintenanceCase.objects.get(reports=report_area)
        self.assertEqual(area_case.location, floor_3)
        self.assertEqual(area_case.decision.location, floor_3)

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

    def test_settlement_page_uses_agreed_name_en_and_vi(self):
        fake_settlement = SimpleNamespace(
            pk=1,
            proposal=SimpleNamespace(
                current_version=SimpleNamespace(contractor_name="Acme", amount_vnd=1000000),
                public_token=None,
            ),
            amount_vnd=1000000,
            transfer_id=10,
            transfer=SimpleNamespace(filename="proof.pdf"),
            outbox_event=None,
        )
        with translation.override("en"):
            html_en = render_to_string(
                "web/staff/settlement_detail.html",
                {"settlement": fake_settlement},
            )
            self.assertIn("<dt>Transfer proof</dt>", html_en)
            self.assertNotIn("Transfer evidence", html_en)

        with translation.override("vi"):
            html_vi = render_to_string(
                "web/staff/settlement_detail.html",
                {"settlement": fake_settlement},
            )
            self.assertIn("<dt>Chứng từ thanh toán</dt>", html_vi)
            self.assertNotIn("Bằng chứng chuyển khoản", html_vi)
            self.assertNotIn("Chứng từ chuyển khoản", html_vi)
