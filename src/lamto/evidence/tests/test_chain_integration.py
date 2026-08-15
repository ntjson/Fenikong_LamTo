import os
import secrets
from unittest import skipUnless

from django.test import TestCase, override_settings

from lamto.accounts.models import Building
from lamto.evidence.models import BlockchainOutboxEvent, EvidenceType
from lamto.evidence.services import queue_platform_event
from lamto.evidence.worker import process_outbox_event
from lamto.testing.factories import (
    PilotDomainDriver,
    build_temp_storage_override,
    seed_pilot_world,
)


DEV_KEY = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"


@skipUnless(os.getenv("RUN_CHAIN_INTEGRATION"), "set RUN_CHAIN_INTEGRATION=1 for Besu")
@override_settings(PLATFORM_SIGNER_PRIVATE_KEY=DEV_KEY, EVIDENCE_ANCHORING_BACKEND="chain")
class PlatformChainIntegrationTests(TestCase):
    def test_platform_signed_proposal_reaches_chain(self):
        building = Building.objects.create(name="Chain integration")
        event = queue_platform_event(
            "0x" + secrets.token_hex(32), EvidenceType.PROPOSAL_CREATED,
            {
                "proposal_id": 1, "proposal_version": 1, "record_id": 1,
                "amount_vnd": 1, "proposal_snapshot_hash": "1" * 64,
                "quotation_hash": "2" * 64,
                "building_id": building.pk,
            },
            "0x" + "00" * 32, building,
        )
        self.assertEqual(
            process_outbox_event(event.pk).status,
            BlockchainOutboxEvent.Status.CONFIRMED,
        )

    def test_platform_signed_proposal_and_settlement_reach_chain(self):
        _location, storage_override = build_temp_storage_override()
        with storage_override:
            driver = PilotDomainDriver(seed_pilot_world(
                building_name="Chain settlement integration",
                create_opening_fund=False,
                create_sample_report=False,
            ))
            version = driver.publish_standalone_proposal()
            driver.decide_proposal()
            driver.publish_proposal_progress()
            driver.complete_proposal_work()
            driver.record_settlement_transfer()
            driver.pause_chain()
            settlement = driver.record_settlement_ack()

            proposal_event = process_outbox_event(version.outbox_event_id)
            settlement_event = process_outbox_event(settlement.outbox_event_id)

        self.assertEqual(proposal_event.status, BlockchainOutboxEvent.Status.CONFIRMED)
        self.assertEqual(settlement_event.status, BlockchainOutboxEvent.Status.CONFIRMED)
