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
from lamto.finance.settlements import record_acknowledgement, record_transfer
from lamto.maintenance.cases import close_expired_completed_cases


@override_settings(LANGUAGE_CODE="en-us")  # asserts English source strings
class SettlementTests(TestCase):
    def test_transfer_amount_must_match_frozen_proposal_amount(self):
        proposal, version = self.completed()
        proof = self.document(Document.Kind.PAYMENT_PROOF, "mismatch")

        with self.assertRaisesMessage(ValidationError, "must match the published proposal amount"):
            record_transfer(
                proposal, self.membership, amount_vnd=version.amount_vnd + 1,
                payee_name="Payee", bank_reference="REF", transfer=proof,
            )

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
        version = publish_proposal_version(proposal, self.membership, amount_vnd=100, contractor_name="Acme", fund_code="GENERAL", purpose="Repair", proposed_action="Fix", expected_schedule="Now", quotation_versions=[quote], event_id="0x" + secrets.token_hex(32))
        proposal.status = Proposal.Status.COMPLETED
        proposal.completed_at = timezone.now()
        proposal.save(update_fields=["status", "completed_at"])
        return proposal, version

    def transfer(self, proposal, amount=100):
        proof = self.document(Document.Kind.PAYMENT_PROOF, secrets.token_hex(3))
        return record_transfer(proposal, self.membership, amount_vnd=amount, payee_name="Acme", bank_reference=" bank  001 ", transfer=proof)

    def test_transfer_then_ack_settles_and_anchors(self):
        proposal, version = self.completed()
        settlement = self.transfer(proposal)
        self.assertIsNone(settlement.settled_at)
        proof = self.document(Document.Kind.PAYMENT_PROOF, "ack")
        settlement = record_acknowledgement(settlement, self.membership, ack=proof, event_id="0x" + secrets.token_hex(32))
        self.assertIsNotNone(settlement.settled_at)
        self.assertEqual(settlement.outbox_event.event_type, EvidenceType.SETTLEMENT)
        self.assertEqual(settlement.outbox_event.previous_hash, "0x" + version.outbox_event.payload_hash)
        self.assertTrue(settlement.outbox_event.signer_address)

    def test_second_settlement_is_rejected(self):
        proposal, _ = self.completed()
        self.transfer(proposal)
        with self.assertRaises(ValidationError):
            self.transfer(proposal)

    def test_ack_on_settled_settlement_is_rejected(self):
        proposal, _ = self.completed()
        settlement = self.transfer(proposal)
        proof = self.document(Document.Kind.PAYMENT_PROOF, "ack")
        record_acknowledgement(settlement, self.membership, ack=proof, event_id="0x" + secrets.token_hex(32))
        with self.assertRaises(ValidationError):
            record_acknowledgement(settlement, self.membership, ack=proof, event_id="0x" + secrets.token_hex(32))

    def test_amount_must_be_a_positive_integer(self):
        proposal, _ = self.completed()
        for invalid in (0, -1, True, "100"):
            with self.subTest(invalid=invalid), self.assertRaises(ValidationError):
                self.transfer(proposal, invalid)

    def test_settled_at_is_null_until_acknowledgement(self):
        proposal, _ = self.completed()
        self.assertIsNone(self.transfer(proposal).settled_at)

    def test_non_completed_rejected(self):
        proposal = create_standalone_proposal(self.building, self.membership)
        with self.assertRaises(ValidationError):
            self.transfer(proposal)

    def test_later_settlement_postpones_close_and_is_not_counted(self):
        proposal, _ = self.completed()
        completed_at = timezone.now() - timedelta(days=15)
        Proposal.objects.filter(pk=proposal.pk).update(completed_at=completed_at)
        proposal.refresh_from_db()
        settlement = self.transfer(proposal)
        proof = self.document(Document.Kind.PAYMENT_PROOF, "late-ack")
        settlement = record_acknowledgement(
            settlement,
            self.membership,
            ack=proof,
            event_id="0x" + secrets.token_hex(32),
        )

        self.assertEqual(close_expired_completed_cases(now=settlement.settled_at - timedelta(seconds=1)), 0)
        proposal.refresh_from_db()
        self.assertIsNone(proposal.closed_at)
