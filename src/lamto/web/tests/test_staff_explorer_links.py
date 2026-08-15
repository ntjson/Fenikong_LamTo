import secrets
import tempfile

from django.template.loader import render_to_string
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from lamto.evidence.models import BlockchainOutboxEvent, EvidenceType
from lamto.evidence.services import queue_platform_event
from lamto.finance.models import Proposal, Settlement
from lamto.maintenance.models import BuildingLocation, IssueReport, MaintenanceCase, TriageDecision, TriageJob, TriageSuggestion
from lamto.testing.factories import PilotDomainDriver, seed_pilot_world

_TEMP_STORAGE = tempfile.mkdtemp(prefix="lamto-staff-explorer-tests-")


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": _TEMP_STORAGE},
        },
        "private": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": _TEMP_STORAGE},
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
)
class StaffExplorerLinkTests(TestCase):
    def setUp(self):
        self.seed = seed_pilot_world(
            building_name="Explorer Tower",
            email_prefix="staff-explorer",
            create_opening_fund=False,
        )
        self.driver = PilotDomainDriver(self.seed)
        self.driver.confirm_triage_case()
        self.driver.publish_proposal()
        self.driver.complete_assigned_work()
        self.settlement = self.driver.record_settlement()
        self.proposal = self.seed.proposal
        self.proposal.refresh_from_db()
        (self.manager,) = self.seed.management_memberships
        self.client.force_login(self.manager.user)

    def test_proposal_detail_with_token_shows_badge_and_link_and_no_disclosure(self):
        self.assertTrue(self.proposal.public_token)
        explorer_url = reverse("explorer:detail", kwargs={"public_token": self.proposal.public_token})

        response = self.client.get(reverse("web:proposal-detail", kwargs={"pk": self.proposal.pk}))
        self.assertEqual(response.status_code, 200)

        # Explorer link is present with Vietnamese copy
        self.assertContains(response, f'href="{explorer_url}"')
        self.assertContains(response, "Trình khám phá bằng chứng")

        # Anchoring badge is present
        self.assertContains(response, "status-")

        # Raw-hash technical proof disclosure is gone
        self.assertNotContains(response, 'class="technical-proof"')
        self.assertNotContains(response, "Bằng chứng kỹ thuật")
        self.assertNotContains(response, 'id="snapshot-json"')

        # Under English locale override, the template uses English source msgids
        with translation.override("en"):
            html_en = render_to_string("web/staff/proposal_detail.html", response.context[0].flatten())
            self.assertIn(f'href="{explorer_url}"', html_en)
            self.assertIn("Evidence explorer", html_en)
            self.assertNotIn('class="technical-proof"', html_en)
            self.assertNotIn("Technical proof", html_en)

    def test_proposal_detail_without_token_keeps_disclosure_verbatim(self):
        # Simulate pre-feature proposal without public token
        Proposal.objects.filter(pk=self.proposal.pk).update(public_token=None)
        self.proposal.refresh_from_db()
        self.assertIsNone(self.proposal.public_token)

        response = self.client.get(reverse("web:proposal-detail", kwargs={"pk": self.proposal.pk}))
        self.assertEqual(response.status_code, 200)

        # Technical proof disclosure is preserved
        self.assertContains(response, 'class="technical-proof"')
        self.assertContains(response, "Bằng chứng kỹ thuật")
        self.assertContains(response, 'id="snapshot-json"')
        self.assertNotContains(response, "/e/")
        self.assertNotContains(response, "Trình khám phá bằng chứng")

    def test_settlement_detail_with_token_shows_badge_and_link_and_no_disclosure(self):
        self.assertTrue(self.proposal.public_token)
        explorer_url = reverse("explorer:detail", kwargs={"public_token": self.proposal.public_token})

        response = self.client.get(reverse("web:settlement-detail", kwargs={"pk": self.settlement.pk}))
        self.assertEqual(response.status_code, 200)

        # Explorer link is present with Vietnamese copy, pointing to the same explorer URL
        self.assertContains(response, f'href="{explorer_url}"')
        self.assertContains(response, "Trình khám phá bằng chứng")

        # Anchoring badge is present
        self.assertContains(response, "status-")

        # Raw-hash technical proof disclosure is gone
        self.assertNotContains(response, 'class="technical-proof"')
        self.assertNotContains(response, "Bằng chứng kỹ thuật")

        # Under English locale override, the template uses English source msgids
        with translation.override("en"):
            html_en = render_to_string("web/staff/settlement_detail.html", response.context[0].flatten())
            self.assertIn(f'href="{explorer_url}"', html_en)
            self.assertIn("Evidence explorer", html_en)
            self.assertNotIn('class="technical-proof"', html_en)
            self.assertNotIn("Technical proof", html_en)

    def test_settlement_detail_without_token_keeps_disclosure_verbatim(self):
        # Simulate pre-feature proposal without public token
        Proposal.objects.filter(pk=self.proposal.pk).update(public_token=None)
        self.proposal.refresh_from_db()
        self.assertIsNone(self.proposal.public_token)

        response = self.client.get(reverse("web:settlement-detail", kwargs={"pk": self.settlement.pk}))
        self.assertEqual(response.status_code, 200)

        # Technical proof disclosure is preserved
        self.assertContains(response, 'class="technical-proof"')
        self.assertContains(response, "Bằng chứng kỹ thuật")
        self.assertNotContains(response, "/e/")
        self.assertNotContains(response, "Trình khám phá bằng chứng")

    def test_case_detail_triage_confidence_keeps_technical_proof_disclosure(self):
        loc = BuildingLocation.objects.create(building=self.seed.building, name="Lobby")
        report = IssueReport.objects.create(
            reporter=self.seed.residents[0],
            unit=self.seed.unit,
            building=self.seed.building,
            text="Lift jerked",
            selected_location=loc,
            location_path_snapshot="Lobby",
            status=IssueReport.Status.IN_REVIEW,
        )
        job = TriageJob.objects.create(report=report)
        suggestion = TriageSuggestion.objects.create(
            job=job,
            category="ELEVATOR",
            interpreted_location="Lobby",
            urgency="HIGH",
            management_queue="GENERAL",
            deadline_minutes=120,
            confidence_percent=95,
            duplicate_report_ids=[],
            raw_response={},
            provider_request_id="req-123",
            elapsed_ms=10,
        )
        decision = TriageDecision.objects.create(
            report=report,
            suggestion=suggestion,
            operator=self.manager.user,
            category="ELEVATOR",
            urgency="HIGH",
            management_queue="GENERAL",
            location=loc,
            deadline_minutes=120,
        )
        response = self.client.get(reverse("web:staff-report-detail", kwargs={"pk": report.pk}))
        self.assertEqual(response.status_code, 200)
        # Triage confidence technical proof disclosure is preserved
        self.assertContains(response, 'class="technical-proof"')
        self.assertContains(response, "Bằng chứng kỹ thuật")
        self.assertContains(response, "95%")

    def test_exception_review_keeps_technical_proof_disclosure(self):
        event = queue_platform_event(
            "0x" + secrets.token_hex(32),
            EvidenceType.PROPOSAL_CREATED,
            {
                "proposal_id": 1,
                "proposal_version": 1,
                "record_id": 1,
                "amount_vnd": 1,
                "proposal_snapshot_hash": "1" * 64,
                "quotation_hash": "2" * 64,
                "building_id": self.seed.building.pk,
            },
            "0x" + "00" * 32,
            self.seed.building,
        )
        BlockchainOutboxEvent.objects.filter(pk=event.pk).update(
            status=BlockchainOutboxEvent.Status.FAILED, last_error="RPC unreachable"
        )
        response = self.client.get(
            reverse("web:exception-review", kwargs={"kind": "failed_outbox", "pk": event.pk})
        )
        self.assertEqual(response.status_code, 200)
        # Exception review disclosure is preserved
        self.assertContains(response, 'class="technical-proof"')
        self.assertContains(response, "Bằng chứng kỹ thuật")
