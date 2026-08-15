"""GET /ledger and /ledger/{id} — published entries with proof (spec 3.3)."""

import json
import secrets
import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse
from knox.models import AuthToken

from lamto.evidence.models import BlockchainOutboxEvent, EvidenceLevel
from lamto.finance.models import PublishedLedgerEntry
from lamto.finance.proposals import create_standalone_proposal, decide_proposal, publish_proposal_version
from lamto.finance.settlements import record_settlement
from lamto.maintenance.cases import complete_proposal_work
from lamto.documents.models import Document
from lamto.testing.factories import PilotDomainDriver, seed_pilot_world

_TEMP_STORAGE = tempfile.mkdtemp(prefix="lamto-api-ledger-")


def problem(response):
    return json.loads(response.content)


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
class LedgerApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.seed = seed_pilot_world(
            building_name="API Ledger Building",
            email_prefix="apil",
            create_sample_report=False,
        )
        driver = PilotDomainDriver(cls.seed)
        driver.submit_report("Lobby lamp flickers", "Lift 2")
        driver.confirm_triage_case()
        driver.publish_proposal()
        driver.complete_assigned_work()
        driver.record_settlement()
        driver.confirm_all_chain_events()
        driver.publish_settlement_entry()
        driver.confirm_all_chain_events()
        cls.entry = PublishedLedgerEntry.objects.get(
            case__building=cls.seed.building
        )

    def _auth(self):
        _instance, token = AuthToken.objects.create(
            user=self.seed.residents[0]
        )
        return {"authorization": f"Token {token}"}

    def test_list_returns_published_entry_with_cursor_shape(self):
        response = self.client.get(reverse("api:ledger-list"), headers=self._auth())
        assert response.status_code == 200, response.content
        body = response.json()
        assert set(body) == {"next", "previous", "results"}
        assert len(body["results"]) == 1
        row = body["results"][0]
        assert row["id"] == self.entry.pk
        assert row["contractor_name"] == self.entry.contractor_name
        assert row["actual_cost_vnd"] == self.entry.actual_cost_vnd
        assert row["published_at"]
        assert row["evidence_level"] == EvidenceLevel.CHAIN_CONFIRMED
        assert row["integrity_status"] == self.entry.effective_integrity_status
        # List rows carry the same §6.3(6) story subject as the detail.
        assert row["what_was_fixed"] == "Cable secured"

    def test_list_period_filters(self):
        year = self.entry.published_at.year
        auth = self._auth()
        hit = self.client.get(
            reverse("api:ledger-list"),
            {"year": year, "month": self.entry.published_at.month},
            headers=auth,
        )
        assert len(hit.json()["results"]) == 1
        miss = self.client.get(
            reverse("api:ledger-list"), {"year": year - 1}, headers=auth
        )
        assert miss.json()["results"] == []

    def test_month_without_year_is_validation_failed(self):
        response = self.client.get(
            reverse("api:ledger-list"), {"month": 5}, headers=self._auth()
        )
        assert response.status_code == 400
        body = problem(response)
        assert body["code"] == "validation_failed"
        assert "month" in body["errors"]

    def test_detail_returns_payload_and_proof(self):
        response = self.client.get(
            reverse("api:ledger-detail", args=[self.entry.pk]), headers=self._auth()
        )
        assert response.status_code == 200, response.content
        body = response.json()
        assert set(body) == {
            "id", "contractor_name", "actual_cost_vnd", "published_at",
            "proposed_amount_vnd", "integrity_status", "what_was_fixed", "why",
            "payload", "verification", "approvers", "corrections",
            "documents", "proof",
        }
        assert body["approvers"] == []
        assert body["corrections"] == []
        assert body["id"] == self.entry.pk
        assert body["contractor_name"] == self.entry.contractor_name
        assert body["actual_cost_vnd"] == self.entry.actual_cost_vnd
        assert body["proposed_amount_vnd"] is not None
        # §6.3(6)/A1: plain-language story fields (not client-faked).
        assert body["what_was_fixed"] == "Cable secured"
        assert body["why"] == "Worn cable"
        assert body["actual_cost_vnd"] == self.entry.actual_cost_vnd
        assert set(body["payload"]) == {
            "report_id",
            "case_id",
            "proposal_id",
            "proposal_version",
            "proposed_amount_vnd",
            "actual_cost_vnd",
            "contractor_name",
            "document_hashes",
            "settlement",
        }
        assert "report_id" in body["payload"]
        assert body["verification"] is None
        assert body["documents"], "document hashes must be exposed"
        for doc in body["documents"]:
            assert set(doc) == {"label", "filename", "sha256", "download_url"}
            assert len(doc["sha256"]) == 64
            assert doc["download_url"]
        proof = body["proof"]
        assert proof["evidence_level"] == EvidenceLevel.CHAIN_CONFIRMED
        assert proof["anchoring_backend"] == "besu"
        assert proof["payload_hash"] == self.entry.settlement.outbox_event.payload_hash
        assert proof["proposal_version"]["evidence_level"] == EvidenceLevel.CHAIN_CONFIRMED
        assert proof["settlement"]["evidence_level"] == EvidenceLevel.CHAIN_CONFIRMED
        assert proof["events"], "outbox events must be listed in the proof"
        for event in proof["events"]:
            assert event["event_id"].startswith("0x")
            assert event["status"] == BlockchainOutboxEvent.Status.CONFIRMED
            assert event["evidence_level"] == EvidenceLevel.CHAIN_CONFIRMED

    def test_detail_unknown_pk_is_404_problem(self):
        response = self.client.get(
            reverse("api:ledger-detail", args=[999999]), headers=self._auth()
        )
        assert response.status_code == 404
        assert problem(response)["code"] == "not_found"

    def test_both_anchors_must_be_settled(self):
        event_ids = (
            self.entry.proposal.current_version.outbox_event_id,
            self.entry.settlement.outbox_event_id,
        )
        for event_id in event_ids:
            for status in (
                BlockchainOutboxEvent.Status.PENDING,
                BlockchainOutboxEvent.Status.FAILED,
                BlockchainOutboxEvent.Status.MISMATCH,
            ):
                with self.subTest(event_id=event_id, status=status):
                    BlockchainOutboxEvent.objects.filter(pk=event_id).update(status=status)
                    auth = self._auth()
                    assert self.client.get(reverse("api:ledger-list"), headers=auth).json()["results"] == []
                    assert self.client.get(reverse("api:ledger-detail", args=[self.entry.pk]), headers=auth).status_code == 404
                    BlockchainOutboxEvent.objects.filter(pk=event_id).update(status=BlockchainOutboxEvent.Status.CONFIRMED)

    def test_standalone_entry_list_detail_story_and_download(self):
        manager = self.seed.management_memberships[0]
        proposal = create_standalone_proposal(self.seed.building, manager)
        quotation = self.seed.document(Document.Kind.QUOTATION, manager.user, "standalone-q")
        publish_proposal_version(
            proposal, manager, amount_vnd=2_000_000, contractor_name="Standalone Co",
            purpose="Lobby repaint", proposed_action="Repaint lobby",
            expected_schedule="August", quotation_versions=[quotation],
            event_id="0x" + secrets.token_hex(32),
        )
        decide_proposal(proposal, manager.user, True)
        complete_proposal_work(proposal, manager.user, "Peeling paint", "Lobby repainted")
        transfer = self.seed.document(Document.Kind.PAYMENT_PROOF, manager.user, "standalone-transfer")
        settlement = record_settlement(
            proposal, manager, transfer=transfer,
            event_id="0x" + secrets.token_hex(32),
        )
        proposal.refresh_from_db()
        for event in (proposal.current_version.outbox_event, settlement.outbox_event):
            BlockchainOutboxEvent.objects.filter(pk=event.pk).update(status=BlockchainOutboxEvent.Status.CONFIRMED)
        entry = settlement.ledger_entry
        auth = self._auth()
        rows = self.client.get(reverse("api:ledger-list"), headers=auth).json()["results"]
        row = next(row for row in rows if row["id"] == entry.pk)
        assert row["what_was_fixed"] == "Lobby repainted"
        detail = self.client.get(reverse("api:ledger-detail", args=[entry.pk]), headers=auth)
        assert detail.status_code == 200
        body = detail.json()
        assert body["what_was_fixed"] == "Lobby repainted"
        assert body["why"] == "Peeling paint"
        assert body["proof"]["proposal_version"]["evidence_level"] == EvidenceLevel.CHAIN_CONFIRMED
        assert body["proof"]["settlement"]["evidence_level"] == EvidenceLevel.CHAIN_CONFIRMED
        assert self.client.get(body["documents"][0]["download_url"], headers=auth).status_code == 200
