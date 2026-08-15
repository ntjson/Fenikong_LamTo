import tempfile
from pathlib import Path
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from lamto.finance.models import Proposal, ProposalVersion, Settlement
from lamto.documents.models import Document, DocumentVersion
from lamto.maintenance.models import IssueReport, WorkUpdate
from lamto.testing.factories import PilotDomainDriver, seed_pilot_world
from lamto.web.staff_documents import new_event_id

_TEMP = tempfile.mkdtemp(prefix="lamto-propcreate-")


def _pdf(name, body):
    return SimpleUploadedFile(name, b"%PDF-1.4\n" + body, content_type="application/pdf")


def _image(name, body):
    png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
        b"\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00"
        b"\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return SimpleUploadedFile(name, png + body, content_type="image/png")


@override_settings(
    LANGUAGE_CODE="en",
    ROOT_URLCONF="lamto.config.urls",
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _TEMP}},
        "private": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _TEMP}},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    },
)
class ProposalCreateTests(TestCase):
    def setUp(self):
        self.seed = seed_pilot_world(building_name="Prop Create B", email_prefix="pc")
        driver = PilotDomainDriver(self.seed)
        driver.submit_report("Lift jerks", "Lift 2")
        driver.confirm_triage_case()
        self.work = self.seed.case
        self.operator = self.seed.management_memberships[0]

    def _login_operator(self):
        self.client.force_login(self.operator.user)
        session = self.client.session
        session["active_management_id"] = self.operator.pk
        session.save()

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_publish_submits_platform_signed_version(self):
        self._login_operator()
        url = reverse("web:proposal-create", kwargs={"pk": self.work.pk})

        prepare = self.client.post(
            url,
            {
                "action": "prepare",
                "amount_vnd": 5_000_000,
                "contractor_name": "Acme Co",
                "purpose": "Elevator noise",
                "proposed_action": "Replace bearings",
                "expected_schedule": "August 2026",
                "quotation": _pdf("q.pdf", b"orig"),
                "confirm": "on",
            },
        )
        self.assertEqual(prepare.status_code, 302)
        proposal = Proposal.objects.get(case=self.work)
        version = ProposalVersion.objects.get(proposal=proposal)
        self.assertEqual(version.amount_vnd, 5_000_000)
        self.assertTrue(version.outbox_event.signer_address)
        self.work.refresh_from_db()

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_publish_requires_explicit_immutable_record_confirmation(self):
        self._login_operator()

        response = self.client.post(reverse("web:proposal-create", kwargs={"pk": self.work.pk}), {
            "amount_vnd": 5_000_000, "contractor_name": "Acme Co",
            "purpose": "Lift jerks",
            "proposed_action": "Replace bearings", "expected_schedule": "August 2026",
            "quotation": _pdf("q.pdf", b"orig"),
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cannot be edited")
        self.assertFalse(Proposal.objects.filter(case=self.work).exists())

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_case_backed_proceed_decision_starts_case_work(self):
        self._login_operator()
        self.client.post(reverse("web:proposal-create", kwargs={"pk": self.work.pk}), {
            "action": "prepare", "amount_vnd": 5_000_000, "contractor_name": "Acme Co",
            "purpose": "Lift jerks",
            "proposed_action": "Replace bearings", "expected_schedule": "August 2026",
            "quotation": _pdf("q.pdf", b"orig"),
            "confirm": "on",
        })
        proposal = Proposal.objects.get(case=self.work)

        response = self.client.post(
            reverse("web:proposal-detail", kwargs={"pk": proposal.pk}),
            {"action": "decide", "decision": "proceed", "note": "Proceed"},
        )

        self.assertRedirects(response, reverse("web:proposal-detail", kwargs={"pk": proposal.pk}))
        proposal.refresh_from_db()
        self.work.decision.report.refresh_from_db()
        self.assertEqual(proposal.status, Proposal.Status.IN_PROGRESS)
        self.assertEqual(self.work.decision.report.status, IssueReport.Status.IN_PROGRESS)

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_published_proposal_detail_names_frozen_record_and_existing_actions(self):
        self._login_operator()
        self.client.post(reverse("web:proposal-create", kwargs={"pk": self.work.pk}), {
            "amount_vnd": 5_000_000, "contractor_name": "Acme Co",
            "purpose": "Lift jerks",
            "proposed_action": "Replace bearings", "expected_schedule": "August 2026",
            "quotation": _pdf("q.pdf", b"orig"), "confirm": "on",
        })
        proposal = Proposal.objects.get(case=self.work)

        response = self.client.get(reverse("web:proposal-detail", kwargs={"pk": proposal.pk}))

        self.assertContains(response, 'name="action" value="decide"', html=False)
        self.assertContains(response, "The amount, contractor, scope, schedule, and quotation evidence are frozen.")
        self.assertContains(response, "Pending")
        self.assertTrue(response.context["publication_pending"])
        self.assertEqual(response.context["publication_snapshot"], proposal.current_version)

    def test_standalone_proposal_detail_does_not_link_to_missing_case(self):
        self._login_operator()
        driver = PilotDomainDriver(self.seed)
        driver.publish_standalone_proposal()

        response = self.client.get(reverse("web:proposal-detail", args=[self.seed.proposal.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Maintenance case")

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    @patch("lamto.web.views.proposals.publish_proposal_version", side_effect=ValidationError("Signing failed"))
    def test_failed_proposal_publication_removes_uploaded_quotation(self, _publish):
        self._login_operator()
        before_documents = Document.objects.count()
        before_files = {path for path in Path(_TEMP).rglob("*") if path.is_file()}

        response = self.client.post(reverse("web:proposal-create", args=[self.work.pk]), {
            "amount_vnd": 5_000_000, "contractor_name": "Acme Co",
            "quotation": _pdf("failed.pdf", b"failed"), "confirm": "on",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Signing failed")
        self.assertEqual(Document.objects.count(), before_documents)
        self.assertEqual({path for path in Path(_TEMP).rglob("*") if path.is_file()}, before_files)

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_standalone_progress_records_the_work_narrative(self):
        self._login_operator()
        driver = PilotDomainDriver(self.seed)
        driver.publish_standalone_proposal()
        driver.decide_proposal()

        response = self.client.post(reverse("web:proposal-detail", args=[self.seed.proposal.pk]), {
            "action": "progress", "cause": "Wear", "result": "Repair underway",
        })

        self.assertRedirects(response, reverse("web:proposal-detail", args=[self.seed.proposal.pk]))
        update = WorkUpdate.objects.get(proposal=self.seed.proposal)
        self.assertEqual((update.cause, update.result), ("Wear", "Repair underway"))

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_settlement_accepts_upload_in_same_post(self):
        self._login_operator()
        driver = PilotDomainDriver(self.seed)
        driver.publish_standalone_proposal()
        driver.decide_proposal()
        driver.complete_proposal_work()
        proposal = self.seed.proposal

        response = self.client.post(reverse("web:settlement-record", args=[proposal.pk]), {
            "event_id": new_event_id(),
            "proof_upload": _pdf("transfer.pdf", b"transfer"),
        })

        settlement = Settlement.objects.get(proposal=proposal)
        self.assertRedirects(response, reverse("web:settlement-detail", args=[settlement.pk]))
        self.assertEqual(settlement.transfer.document.kind, Document.Kind.PAYMENT_PROOF)
        self.assertIsNotNone(settlement.settled_at)

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_failed_and_mismatched_evidence_are_not_described_as_pending(self):
        from lamto.evidence.models import BlockchainOutboxEvent

        self._login_operator()
        self.client.post(reverse("web:proposal-create", args=[self.work.pk]), {
            "amount_vnd": 5_000_000, "contractor_name": "Acme Co",
            "quotation": _pdf("status.pdf", b"status"), "confirm": "on",
        })
        proposal = Proposal.objects.get(case=self.work)
        for status, copy in (
            (BlockchainOutboxEvent.Status.FAILED, "Evidence anchoring failed"),
            (BlockchainOutboxEvent.Status.MISMATCH, "Evidence mismatch detected"),
        ):
            with self.subTest(status=status):
                BlockchainOutboxEvent.objects.filter(pk=proposal.current_version.outbox_event_id).update(status=status)
                response = self.client.get(reverse("web:proposal-detail", args=[proposal.pk]))
                self.assertFalse(response.context["publication_pending"])
                self.assertContains(response, copy)
                self.assertContains(response, reverse("web:ops-health"))
                self.assertNotContains(response, "No further action is required")

    def test_manager_can_open_proposal_create(self):
        manager = self.seed.management_memberships[0]
        self.client.force_login(manager.user)
        resp = self.client.get(reverse("web:proposal-create", kwargs={"pk": self.work.pk}))
        self.assertEqual(resp.status_code, 200)

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_case_linked_proposal_in_progress_links_to_case_without_progress_form(self):
        self._login_operator()
        driver = PilotDomainDriver(self.seed)
        driver.publish_proposal()
        driver.decide_proposal(proceed=True)
        proposal = self.seed.proposal
        self.assertEqual(proposal.status, Proposal.Status.IN_PROGRESS)
        self.assertIsNotNone(proposal.case_id)

        response = self.client.get(reverse("web:proposal-detail", args=[proposal.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["action_panel"], "case")
        self.assertContains(response, "Work tracked on maintenance case")
        self.assertContains(response, reverse("web:case-detail", kwargs={"pk": proposal.case_id}))
        self.assertContains(response, "Open maintenance case")
        self.assertNotContains(response, 'name="action" value="progress"')
        self.assertNotContains(response, 'name="action" value="complete"')
        self.assertNotContains(response, "Publish work progress")

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_standalone_proposal_in_progress_can_complete_work_via_form(self):
        self._login_operator()
        driver = PilotDomainDriver(self.seed)
        driver.publish_standalone_proposal()
        driver.decide_proposal(proceed=True)
        proposal = self.seed.proposal
        self.assertEqual(proposal.status, Proposal.Status.IN_PROGRESS)
        self.assertIsNone(proposal.case_id)

        response = self.client.get(reverse("web:proposal-detail", args=[proposal.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["action_panel"], "progress")
        self.assertContains(response, "Publish work progress")
        self.assertContains(response, 'name="action" value="progress"')
        self.assertContains(response, 'name="action" value="complete"')

        post_response = self.client.post(
            reverse("web:proposal-detail", args=[proposal.pk]),
            {"action": "complete", "cause": "Normal wear", "result": "Equipment replaced"},
        )
        self.assertRedirects(post_response, reverse("web:proposal-detail", args=[proposal.pk]))
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, Proposal.Status.COMPLETED)
        self.assertIsNotNone(proposal.completed_at)

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_proposals_list_distinguishes_case_linked_and_standalone_in_progress_next_action(self):
        self._login_operator()
        driver = PilotDomainDriver(self.seed)
        driver.publish_proposal()
        driver.decide_proposal(proceed=True)
        case_proposal = self.seed.proposal

        driver.publish_standalone_proposal()
        driver.decide_proposal(proceed=True)
        standalone_proposal = self.seed.proposal

        response = self.client.get(reverse("web:proposal-list"))
        self.assertEqual(response.status_code, 200)

        items_by_url = {item["url"]: item for item in response.context["proposal_items"]}
        case_item = items_by_url[f"/s/proposals/{case_proposal.pk}/"]
        standalone_item = items_by_url[f"/s/proposals/{standalone_proposal.pk}/"]

        self.assertEqual(case_item["next_action"], "Follow work on case")
        self.assertEqual(standalone_item["next_action"], "Publish progress or complete")

    def test_proposal_form_renders_date_pickers_for_expected_schedule(self):
        self._login_operator()
        case_resp = self.client.get(reverse("web:proposal-create", kwargs={"pk": self.work.pk}))
        self.assertEqual(case_resp.status_code, 200)
        self.assertContains(case_resp, '<input type="date" name="expected_start"')
        self.assertContains(case_resp, '<input type="date" name="expected_end"')
        self.assertNotContains(case_resp, 'name="expected_schedule"')

        standalone_resp = self.client.get(reverse("web:standalone-proposal-create"))
        self.assertEqual(standalone_resp.status_code, 200)
        self.assertContains(standalone_resp, '<input type="date" name="expected_start"')
        self.assertContains(standalone_resp, '<input type="date" name="expected_end"')
        self.assertNotContains(standalone_resp, 'name="expected_schedule"')

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_proposal_create_with_start_and_end_dates_stores_dates_and_derived_schedule(self):
        self._login_operator()
        response = self.client.post(
            reverse("web:proposal-create", kwargs={"pk": self.work.pk}),
            {
                "action": "prepare",
                "amount_vnd": 5_000_000,
                "contractor_name": "Acme Co",
                "purpose": "Elevator noise",
                "proposed_action": "Replace bearings",
                "expected_start": "2026-08-01",
                "expected_end": "2026-08-15",
                "quotation": _pdf("q.pdf", b"orig"),
                "confirm": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        proposal = Proposal.objects.get(case=self.work)
        version = proposal.current_version
        import datetime
        self.assertEqual(version.expected_start, datetime.date(2026, 8, 1))
        self.assertEqual(version.expected_end, datetime.date(2026, 8, 15))
        self.assertEqual(version.expected_schedule, "01/08/2026 \u2013 15/08/2026")
        self.assertEqual(version.snapshot["expected_start"], "2026-08-01")
        self.assertEqual(version.snapshot["expected_end"], "2026-08-15")
        self.assertEqual(version.snapshot["expected_schedule"], "01/08/2026 \u2013 15/08/2026")

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_proposal_create_with_omitted_dates_falls_back_to_to_be_scheduled(self):
        self._login_operator()
        response = self.client.post(
            reverse("web:proposal-create", kwargs={"pk": self.work.pk}),
            {
                "action": "prepare",
                "amount_vnd": 5_000_000,
                "contractor_name": "Acme Co",
                "purpose": "Elevator noise",
                "proposed_action": "Replace bearings",
                "quotation": _pdf("q.pdf", b"orig"),
                "confirm": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        proposal = Proposal.objects.get(case=self.work)
        version = proposal.current_version
        self.assertIsNone(version.expected_start)
        self.assertIsNone(version.expected_end)
        self.assertEqual(version.expected_schedule, "To be scheduled")
        self.assertIsNone(version.snapshot["expected_start"])
        self.assertIsNone(version.snapshot["expected_end"])
        self.assertEqual(version.snapshot["expected_schedule"], "To be scheduled")

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_proposal_create_rejects_single_date_without_the_other(self):
        self._login_operator()
        # Start without end
        resp1 = self.client.post(
            reverse("web:proposal-create", kwargs={"pk": self.work.pk}),
            {
                "action": "prepare",
                "amount_vnd": 5_000_000,
                "contractor_name": "Acme Co",
                "purpose": "Elevator noise",
                "proposed_action": "Replace bearings",
                "expected_start": "2026-08-01",
                "quotation": _pdf("q.pdf", b"orig"),
                "confirm": "on",
            },
        )
        self.assertEqual(resp1.status_code, 200)
        self.assertFalse(Proposal.objects.filter(case=self.work).exists())

        # End without start
        resp2 = self.client.post(
            reverse("web:proposal-create", kwargs={"pk": self.work.pk}),
            {
                "action": "prepare",
                "amount_vnd": 5_000_000,
                "contractor_name": "Acme Co",
                "purpose": "Elevator noise",
                "proposed_action": "Replace bearings",
                "expected_end": "2026-08-15",
                "quotation": _pdf("q.pdf", b"orig"),
                "confirm": "on",
            },
        )
        self.assertEqual(resp2.status_code, 200)
        self.assertFalse(Proposal.objects.filter(case=self.work).exists())

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_proposal_create_rejects_end_date_before_start_date(self):
        self._login_operator()
        response = self.client.post(
            reverse("web:proposal-create", kwargs={"pk": self.work.pk}),
            {
                "action": "prepare",
                "amount_vnd": 5_000_000,
                "contractor_name": "Acme Co",
                "purpose": "Elevator noise",
                "proposed_action": "Replace bearings",
                "expected_start": "2026-08-15",
                "expected_end": "2026-08-01",
                "quotation": _pdf("q.pdf", b"orig"),
                "confirm": "on",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Proposal.objects.filter(case=self.work).exists())

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_proposal_create_accepts_past_dates(self):
        self._login_operator()
        response = self.client.post(
            reverse("web:proposal-create", kwargs={"pk": self.work.pk}),
            {
                "action": "prepare",
                "amount_vnd": 5_000_000,
                "contractor_name": "Acme Co",
                "purpose": "Elevator noise",
                "proposed_action": "Replace bearings",
                "expected_start": "2020-01-01",
                "expected_end": "2020-01-10",
                "quotation": _pdf("q.pdf", b"orig"),
                "confirm": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        proposal = Proposal.objects.get(case=self.work)
        self.assertEqual(proposal.current_version.expected_schedule, "01/01/2020 \u2013 10/01/2020")

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_standalone_proposal_requires_schedule_dates(self):
        self._login_operator()
        # Missing dates
        response = self.client.post(
            reverse("web:standalone-proposal-create"),
            {
                "amount_vnd": 5_000_000,
                "contractor_name": "Acme Co",
                "purpose": "Roof maintenance",
                "proposed_action": "Reseal roof",
                "quotation": _pdf("q.pdf", b"orig"),
                "confirm": "on",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Proposal.objects.filter(building=self.seed.building, case__isnull=True).exists())

        # Valid with dates
        valid_resp = self.client.post(
            reverse("web:standalone-proposal-create"),
            {
                "amount_vnd": 5_000_000,
                "contractor_name": "Acme Co",
                "purpose": "Roof maintenance",
                "proposed_action": "Reseal roof",
                "expected_start": "2026-09-01",
                "expected_end": "2026-09-10",
                "quotation": _pdf("q.pdf", b"orig"),
                "confirm": "on",
            },
        )
        self.assertEqual(valid_resp.status_code, 302)
        standalone = Proposal.objects.get(building=self.seed.building, case__isnull=True)
        self.assertEqual(standalone.current_version.expected_schedule, "01/09/2026 \u2013 10/09/2026")

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_proposal_detail_summary_shows_expected_schedule(self):
        self._login_operator()
        self.client.post(
            reverse("web:proposal-create", kwargs={"pk": self.work.pk}),
            {
                "action": "prepare",
                "amount_vnd": 5_000_000,
                "contractor_name": "Acme Co",
                "purpose": "Elevator noise",
                "proposed_action": "Replace bearings",
                "expected_start": "2026-08-01",
                "expected_end": "2026-08-15",
                "quotation": _pdf("q.pdf", b"orig"),
                "confirm": "on",
            },
        )
        proposal = Proposal.objects.get(case=self.work)
        response = self.client.get(reverse("web:proposal-detail", kwargs={"pk": proposal.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Expected schedule")
        self.assertContains(response, "01/08/2026 \u2013 15/08/2026")


def test_decision_form_requires_explicit_choice_and_decline_note():
    from lamto.web.forms.staff import ProposalDecisionForm

    # Untouched form is invalid: NOT_PROCEEDING must never be a silent default.
    assert not ProposalDecisionForm({}).is_valid()
    declined = ProposalDecisionForm({"decision": "decline", "note": " "})
    assert not declined.is_valid()
    assert "note" in declined.errors
    assert ProposalDecisionForm({"decision": "decline", "note": "Giá quá cao"}).is_valid()
    assert ProposalDecisionForm({"decision": "proceed"}).is_valid()
