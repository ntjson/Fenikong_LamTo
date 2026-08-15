"""HTTP journey: password-only Management sessions complete sensitive work.

Ticket 02 — sensitive actions in each affected workflow family reach their
normal result (or normal domain validation result) under a plain password
Management session, with no MFA denial and no re-authentication redirect:

- proposals: creation of a case-backed spending proposal
- settlements: recording a transfer against a completed proposal
- Maintenance Fund: recording an inflow fund source
- gate: registering a reader and issuing its first credential

Each journey logs in through the password form, so the sensitive POST rides a
normal password-only Management session.
"""

import tempfile
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from lamto.finance.models import MaintenanceFundEntry, Proposal, Settlement
from lamto.gate.models import GateDevice
from lamto.testing.factories import PILOT_PASSWORD, PilotDomainDriver, new_event_id, seed_pilot_world

_TEMP = tempfile.mkdtemp(prefix="lamto-sens-")

REAUTH_PATH = "/s/security/reauth/"


def _pdf(name, body):
    return SimpleUploadedFile(
        name, b"%PDF-1.4\n" + body, content_type="application/pdf"
    )


@override_settings(
    ROOT_URLCONF="lamto.config.urls",
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": _TEMP},
        },
        "private": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": _TEMP},
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    },
)
class SensitiveActionsPasswordOnlyTests(TestCase):
    def setUp(self):
        self.seed = seed_pilot_world(
            building_name="Step-Up Removal B", email_prefix="su"
        )
        self.membership = self.seed.management_memberships[0]

    def login(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.membership.user.email, "password": PILOT_PASSWORD},
        )
        self.assertEqual(
            response.status_code, 302, "password login reaches the workspace"
        )
        return response

    def assert_no_reauth_detour(self, response):
        location = response.get("Location", "")
        self.assertNotIn(REAUTH_PATH, location)
        self.assertNotEqual(response.status_code, 403)

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_proposal_creation_submits_directly(self):
        driver = PilotDomainDriver(self.seed)
        driver.submit_report("Lift jerks", "Lift 2")
        driver.confirm_triage_case()
        self.login()

        response = self.client.post(
            reverse("web:proposal-create", kwargs={"pk": self.seed.case.pk}),
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

        proposal = Proposal.objects.get(case=self.seed.case)
        self.assertRedirects(
            response,
            reverse("web:proposal-detail", kwargs={"pk": proposal.pk}),
        )
        self.assert_no_reauth_detour(response)

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_settlement_transfer_submits_directly(self):
        driver = PilotDomainDriver(self.seed)
        driver.submit_report("Lift noise", "Lift 2")
        driver.confirm_triage_case()
        driver.publish_proposal()
        driver.complete_assigned_work()
        proposal = self.seed.proposal
        proposal.refresh_from_db()
        self.login()

        response = self.client.post(
            reverse(
                "web:settlement-record",
                kwargs={"pk": proposal.pk},
            ),
            {
                "event_id": new_event_id(),
                "proof_upload": _pdf("transfer.pdf", b"transfer"),
            },
        )

        settlement = Settlement.objects.get(proposal=self.seed.proposal)
        self.assertRedirects(
            response,
            reverse("web:settlement-detail", kwargs={"pk": settlement.pk}),
        )
        self.assert_no_reauth_detour(response)

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_fund_source_recording_submits_directly(self):
        self.login()

        response = self.client.post(
            reverse("web:fund-record"),
            {
                "entry_type": MaintenanceFundEntry.EntryType.INFLOW,
                "amount_vnd": 2_000_000,
                "evidence": _pdf("evidence.pdf", b"orig"),
            },
        )

        entry = MaintenanceFundEntry.objects.filter(
            fund__building=self.seed.building
        ).latest("pk")
        self.assertRedirects(response, reverse("web:fund-home"))
        self.assertEqual(entry.entry_type, MaintenanceFundEntry.EntryType.INFLOW)
        self.assertEqual(entry.amount_vnd, 2_000_000)
        self.assert_no_reauth_detour(response)

    def test_gate_reader_credential_issue_submits_directly(self):
        self.login()

        response = self.client.post(
            reverse("web:gate-devices"),
            {
                "action": "create",
                "label": "North",
                "direction": GateDevice.Direction.ENTRY,
            },
        )

        device = GateDevice.objects.get(building=self.seed.building, label="North")
        self.assertRedirects(response, reverse("web:gate-devices"))
        self.assertTrue(device.credentials.exists())
        self.assert_no_reauth_detour(response)
