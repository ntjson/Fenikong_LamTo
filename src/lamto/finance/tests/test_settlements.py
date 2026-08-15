import secrets
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from lamto.accounts.models import Building, ManagementMembership, User
from lamto.documents.models import Document, DocumentVersion
from lamto.evidence.models import EvidenceType
from lamto.finance.models import Proposal
from lamto.finance.proposals import create_standalone_proposal, publish_proposal_version
from lamto.finance.settlements import record_settlement
from lamto.maintenance.cases import close_expired_completed_cases


@override_settings(LANGUAGE_CODE="en-us")  # asserts English source strings
class SettlementTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.building = Building.objects.create(name="B1")
        cls.manager = User.objects.create_user(email="m@x.vn", password="pw")
        cls.membership = ManagementMembership.objects.create(user=cls.manager, building=cls.building)

    def document(self, kind, tag):
        doc = Document.objects.create(building=self.building, kind=kind)
        return DocumentVersion.objects.create(document=doc, version=1, storage_key=f"{tag}-o", provider_version_id=f"{tag}-o", filename="o.pdf", content_type="application/pdf", byte_size=1, sha256=secrets.token_hex(32), uploader=self.manager)

    def completed(self):
        proposal = create_standalone_proposal(self.building, self.membership)
        quote = self.document(Document.Kind.QUOTATION, "q")
        version = publish_proposal_version(proposal, self.membership, amount_vnd=100, contractor_name="Acme", purpose="Repair", proposed_action="Fix", expected_schedule="Now", quotation_versions=[quote], event_id="0x" + secrets.token_hex(32))
        proposal.status = Proposal.Status.COMPLETED
        proposal.completed_at = timezone.now()
        proposal.save(update_fields=["status", "completed_at"])
        return proposal, version

    def settle(self, proposal):
        proof = self.document(Document.Kind.PAYMENT_PROOF, secrets.token_hex(3))
        return record_settlement(proposal, self.membership, transfer=proof, event_id="0x" + secrets.token_hex(32))

    def test_transfer_evidence_settles_and_anchors(self):
        proposal, version = self.completed()

        settlement = self.settle(proposal)

        self.assertIsNotNone(settlement.settled_at)
        self.assertEqual(settlement.outbox_event.event_type, EvidenceType.SETTLEMENT)
        self.assertEqual(settlement.outbox_event.previous_hash, "0x" + version.outbox_event.payload_hash)
        self.assertTrue(settlement.outbox_event.signer_address)

    def test_amount_is_taken_from_the_frozen_proposal(self):
        proposal, version = self.completed()

        self.assertEqual(self.settle(proposal).amount_vnd, version.amount_vnd)

    def test_second_settlement_is_rejected(self):
        proposal, _ = self.completed()
        self.settle(proposal)
        with self.assertRaises(ValidationError):
            self.settle(proposal)

    def test_non_completed_rejected(self):
        proposal = create_standalone_proposal(self.building, self.membership)
        with self.assertRaises(ValidationError):
            self.settle(proposal)

    def test_later_settlement_postpones_close_and_is_not_counted(self):
        proposal, _ = self.completed()
        completed_at = timezone.now() - timedelta(days=15)
        Proposal.objects.filter(pk=proposal.pk).update(completed_at=completed_at)
        proposal.refresh_from_db()

        settlement = self.settle(proposal)

        self.assertEqual(close_expired_completed_cases(now=settlement.settled_at - timedelta(seconds=1)), 0)
        proposal.refresh_from_db()
        self.assertIsNone(proposal.closed_at)
