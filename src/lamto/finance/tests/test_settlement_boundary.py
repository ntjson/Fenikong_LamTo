import tempfile
from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase, override_settings

from lamto.finance.integrity import verify_published_entry
from lamto.finance.models import VerificationObservation
from lamto.finance.proposals import publish_proposal_version
from lamto.finance.publication import _collect_document_checks, _load_execution_chain
from lamto.finance.selectors import ledger_entry_proof
from lamto.testing.factories import PilotDomainDriver, new_event_id, seed_pilot_world


_STORAGE = tempfile.mkdtemp(prefix="lamto-settlement-boundary-")


@override_settings(STORAGES={
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _STORAGE}},
    "private": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _STORAGE}},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
})
class SettlementBoundaryTests(TestCase):
    def flow(self):
        seed = seed_pilot_world(building_name=f"Boundary {self._testMethodName}", create_sample_report=False)
        driver = PilotDomainDriver(seed)
        driver.prepare_local_normal_work()
        driver.complete_assigned_work()
        driver.record_settlement_transfer()
        settlement = driver.record_settlement_ack()
        driver.confirm_all_chain_events()
        return driver, settlement

    def test_settlement_documents_feed_publication_checks(self):
        driver, settlement = self.flow()
        proposal = driver.seed.proposal
        proposal.refresh_from_db()
        self.assertEqual(_load_execution_chain(proposal), settlement)
        gates = {gate for _document, _digest, gate in _collect_document_checks(proposal, proposal.current_version, settlement)}
        self.assertTrue({"SETTLEMENT_TRANSFER", "SETTLEMENT_ACK"}.issubset(gates))

    def test_publication_finalizes_and_integrity_traverses_settlement_chain(self):
        driver, settlement = self.flow()
        entry = driver.publish_settlement_entry()
        observation = verify_published_entry(entry.pk)
        checked = set(observation.checked_chain_event_ids)
        self.assertIn(driver.seed.proposal.current_version.outbox_event.event_id, checked)
        self.assertIn(settlement.outbox_event.event_id, checked)

    @override_settings(EVIDENCE_ANCHORING_BACKEND="besu")
    def test_integrity_reports_mismatch_in_an_older_proposal_version(self):
        seed = seed_pilot_world(
            building_name=f"Boundary {self._testMethodName}", create_sample_report=False
        )
        driver = PilotDomainDriver(seed)
        driver.prepare_local_normal_work()
        first = seed.proposal.current_version
        second = publish_proposal_version(
            seed.proposal,
            seed.management_memberships[0],
            amount_vnd=19_000_000,
            contractor_name="Replacement Contractor",
            fund_code="GENERAL",
            purpose="Elevator",
            proposed_action="Replace the affected equipment",
            expected_schedule="Within 21 days",
            quotation_versions=[driver._ctx["quotation"]],
            event_id=new_event_id(),
        )
        driver.complete_assigned_work()
        driver.record_settlement_transfer(amount_vnd=19_000_000)
        settlement = driver.record_settlement_ack()
        driver.confirm_all_chain_events()

        def chain_record(event):
            digest = "f" * 64 if event.pk == first.outbox_event_id else event.payload_hash
            return SimpleNamespace(payload_hash="0x" + digest)

        with patch("lamto.evidence.chain.EvidenceRegistryClient") as client:
            client.return_value.find.side_effect = chain_record
            observation = verify_published_entry(settlement.ledger_entry.pk)

        self.assertEqual(observation.result, VerificationObservation.Result.MISMATCH)
        self.assertEqual(
            observation.checked_chain_event_ids,
            [
                first.outbox_event.event_id,
                second.outbox_event.event_id,
                settlement.outbox_event.event_id,
            ],
        )
        self.assertEqual(observation.details["chain_checks"][0]["result"], "MISMATCH")

    def test_settlement_publishes_story_and_both_anchor_proofs(self):
        driver, settlement = self.flow()
        entry = settlement.ledger_entry
        proof = ledger_entry_proof(entry)
        self.assertEqual(entry.resident_payload["actual_cost_vnd"], settlement.amount_vnd)
        for key, event in (("proposal_version", entry.proposal.current_version.outbox_event), ("settlement", settlement.outbox_event)):
            self.assertEqual(proof[key]["event_id"], event.event_id)
            self.assertEqual(proof[key]["payload_hash"], event.payload_hash)
            self.assertTrue(proof[key]["evidence_level"])

    def test_pilot_settlement_flow_publishes_one_balanced_entry(self):
        driver, _settlement = self.flow()
        driver.publish_settlement_entry()
        self.assertEqual(driver.ledger_count(), 1)
        self.assertEqual(driver.fund_balance(), 100_000_000 - driver._ctx["amount_vnd"])
