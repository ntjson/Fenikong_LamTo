"""Evidence-level enum: total status mapping, no generic verified boolean (spec 5.1)."""

from django.test import SimpleTestCase

from lamto.evidence.models import (
    SETTLED_STATUSES,
    BlockchainOutboxEvent,
    EvidenceLevel,
    evidence_level,
    is_settled,
)

Status = BlockchainOutboxEvent.Status


class EvidenceLevelTests(SimpleTestCase):
    def test_status_to_level_mapping_is_total(self):
        expected = {
            Status.PENDING: EvidenceLevel.PENDING,
            Status.SUBMITTED: EvidenceLevel.PENDING,
            Status.FAILED: EvidenceLevel.PENDING,
            Status.LOCAL: EvidenceLevel.LOCAL_SIGNED,
            Status.CONFIRMED: EvidenceLevel.CHAIN_CONFIRMED,
            Status.MISMATCH: EvidenceLevel.MISMATCH,
        }
        self.assertEqual(set(expected), set(Status))
        for status, level in expected.items():
            self.assertEqual(evidence_level(status), level)
            # Raw DB string values map identically.
            self.assertEqual(evidence_level(str(status)), level)

    def test_is_settled_only_for_local_and_confirmed(self):
        self.assertEqual(
            {status for status in Status if is_settled(status)},
            {Status.LOCAL, Status.CONFIRMED},
        )
        self.assertEqual(set(SETTLED_STATUSES), {Status.LOCAL, Status.CONFIRMED})

    def test_event_property_reflects_current_status(self):
        event = BlockchainOutboxEvent(status=Status.LOCAL)
        self.assertEqual(event.evidence_level, EvidenceLevel.LOCAL_SIGNED)
        event.status = Status.CONFIRMED
        self.assertEqual(event.evidence_level, EvidenceLevel.CHAIN_CONFIRMED)
        # Spec 5.1: no generic verified boolean exists on the event.
        self.assertFalse(hasattr(event, "verified"))
