import secrets

from django.db import DatabaseError, IntegrityError, connection, transaction
from django.test import TestCase, override_settings

from lamto.accounts.models import Building
from lamto.evidence.chain import ChainRecord
from lamto.evidence.models import BlockchainOutboxEvent, EvidenceType
from lamto.evidence.services import EvidenceConflict, queue_platform_event
from lamto.evidence.signatures import platform_signer_address
from lamto.evidence.worker import process_outbox_event


DEV_KEY = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
ZERO = "0x" + "00" * 32


def payload(building):
    return {
        "proposal_id": 1, "proposal_version": 1, "record_id": 1,
        "amount_vnd": 1, "proposal_snapshot_hash": "1" * 64,
        "quotation_hash": "2" * 64,
        "building_id": building.pk,
    }


@override_settings(PLATFORM_SIGNER_PRIVATE_KEY=DEV_KEY)
class PlatformOutboxContractTests(TestCase):
    def setUp(self):
        self.building = Building.objects.create(name="Platform outbox")
        self.event_id = "0x" + secrets.token_hex(32)

    def queue(self):
        return queue_platform_event(
            self.event_id, EvidenceType.PROPOSAL_CREATED,
            payload(self.building), ZERO, self.building,
        )

    def test_queue_is_idempotent_and_conflicts_on_changed_identity(self):
        event = self.queue()
        self.assertEqual(self.queue().pk, event.pk)
        changed = payload(self.building) | {"amount_vnd": 2}
        with self.assertRaises(EvidenceConflict):
            queue_platform_event(
                self.event_id, EvidenceType.PROPOSAL_CREATED, changed, ZERO, self.building
            )

    def test_identity_and_building_are_immutable(self):
        event = self.queue()
        other = Building.objects.create(name="Other")
        with self.assertRaises(IntegrityError), transaction.atomic():
            BlockchainOutboxEvent.objects.filter(pk=event.pk).update(building=other)
        with self.assertRaises(IntegrityError), transaction.atomic():
            BlockchainOutboxEvent.objects.filter(pk=event.pk).update(payload_hash="f" * 64)

    def test_empty_signer_address_is_rejected(self):
        event = self.queue()
        with self.assertRaises(IntegrityError), transaction.atomic():
            BlockchainOutboxEvent.objects.filter(pk=event.pk).update(signer_address="")


@override_settings(PLATFORM_SIGNER_PRIVATE_KEY=DEV_KEY)
class RestrictedRuntimeInsertTests(TestCase):
    def test_writer_can_queue_only_through_platform_procedure(self):
        building = Building.objects.create(name="Restricted runtime")
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL ROLE lamto_writer")
        try:
            event = queue_platform_event(
                "0x" + secrets.token_hex(32), EvidenceType.PROPOSAL_CREATED,
                payload(building), ZERO, building,
            )
            self.assertEqual(event.signer_address, platform_signer_address())
            with self.assertRaises(DatabaseError), transaction.atomic():
                BlockchainOutboxEvent.objects.create(
                    event_id="0x" + secrets.token_hex(32), event_type=1,
                    payload=payload(building), payload_hash="1" * 64,
                    previous_hash=ZERO, signature="0x" + "1" * 130,
                    signer_address=platform_signer_address(), building=building,
                )
        finally:
            pass


class FakeClient:
    last_receipt = {"status": 1, "blockNumber": 7}

    def __init__(self, *, record=None, error=None):
        self.record = record
        self.error = error
        self.submissions = 0

    def find(self, event):
        if self.error:
            raise self.error
        return self.record

    def submit(self, event):
        self.submissions += 1
        return "0x" + "4" * 64


@override_settings(PLATFORM_SIGNER_PRIVATE_KEY=DEV_KEY)
class PlatformWorkerTests(TestCase):
    def setUp(self):
        building = Building.objects.create(name="Worker")
        self.event = queue_platform_event(
            "0x" + secrets.token_hex(32), EvidenceType.PROPOSAL_CREATED,
            payload(building), ZERO, building,
        )

    def test_submit_is_idempotent(self):
        client = FakeClient()
        result = process_outbox_event(self.event.pk, client)
        self.assertEqual(result.status, BlockchainOutboxEvent.Status.CONFIRMED)
        process_outbox_event(self.event.pk, client)
        self.assertEqual(client.submissions, 1)

    def test_retry_releases_lease(self):
        result = process_outbox_event(self.event.pk, FakeClient(error=RuntimeError("down")))
        self.assertEqual(result.status, BlockchainOutboxEvent.Status.PENDING)
        self.assertIsNone(result.lease_expires_at)
        self.assertEqual(result.attempts, 1)

    def test_mismatched_chain_record_is_terminal(self):
        record = ChainRecord("f" * 64, ZERO, 1, platform_signer_address(), 1)
        result = process_outbox_event(self.event.pk, FakeClient(record=record))
        self.assertEqual(result.status, BlockchainOutboxEvent.Status.MISMATCH)

    @override_settings(EVIDENCE_ANCHORING_BACKEND="disabled")
    def test_disabled_backend_settles_local(self):
        result = process_outbox_event(self.event.pk)
        self.assertEqual(result.status, BlockchainOutboxEvent.Status.LOCAL)
        self.assertEqual(result.transaction_hash, "")
