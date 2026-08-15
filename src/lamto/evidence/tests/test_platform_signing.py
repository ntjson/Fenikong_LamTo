import hashlib
import secrets

from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError

from lamto.accounts.models import Building
from lamto.evidence.models import BlockchainOutboxEvent, EvidenceType
from lamto.evidence.services import queue_platform_event
from lamto.evidence.signatures import (
    build_evidence_typed_data,
    platform_sign_evidence,
    platform_signer_address,
    recover_signer,
)


DEV_KEY = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
ZERO_HASH = "0x" + "0" * 64


@override_settings(PLATFORM_SIGNER_PRIVATE_KEY=DEV_KEY)
class PlatformSigningTests(TestCase):
    def test_signature_recovers_to_platform_address(self):
        event_id = "0x" + secrets.token_hex(32)
        payload_hash = hashlib.sha256(b"x").hexdigest()

        signature = platform_sign_evidence(event_id, 1, payload_hash, ZERO_HASH)
        typed = build_evidence_typed_data(event_id, 1, "0x" + payload_hash, ZERO_HASH)

        self.assertEqual(recover_signer(typed, signature), platform_signer_address())

    def test_queue_platform_event_persists_signed_row(self):
        building = Building.objects.create(name="B1")
        event_id = "0x" + secrets.token_hex(32)
        payload = {
            "proposal_id": 1,
            "proposal_version": 1,
            "record_id": 1,
            "case_id": 1,
            "report_id": 1,
            "amount_vnd": 1,
            "proposal_snapshot_hash": "0" * 64,
            "case_snapshot_hash": "0" * 64,
            "report_snapshot_hash": "0" * 64,
            "quotation_hash": "0" * 64,
        }

        event = queue_platform_event(
            event_id, EvidenceType.PROPOSAL_CREATED, payload, ZERO_HASH, building
        )

        self.assertEqual(event.signer_address, platform_signer_address())
        self.assertEqual(event.signer_address, platform_signer_address())
        self.assertEqual(event.status, BlockchainOutboxEvent.Status.PENDING)
        again = queue_platform_event(
            event_id, EvidenceType.PROPOSAL_CREATED, payload, ZERO_HASH, building
        )
        self.assertEqual(again.pk, event.pk)

    def test_only_proposals_and_settlements_are_queueable(self):
        building = Building.objects.create(name="B2")
        for event_type in (6, 7, 8, 9, 11):
            with self.assertRaises(ValidationError):
                queue_platform_event("0x" + secrets.token_hex(32), event_type, {}, ZERO_HASH, building)
