"""Tampering is detected by ledger integrity verification."""

from __future__ import annotations

import pytest
from django.core.files.storage import storages

pytestmark = pytest.mark.django_db

def test_tampered_document_blocks_publish(page, seeded_pilot):
    seeded_pilot.prepare_local_normal_work(page)
    seeded_pilot.complete_assigned_work()
    seeded_pilot.record_settlement_transfer()
    seeded_pilot.record_settlement_ack()
    seeded_pilot.confirm_all_chain_events()

    settlement = seeded_pilot._ctx["settlement"]
    storage = storages["private"]
    with storage.open(settlement.transfer.storage_key, "wb") as handle:
        handle.write(b"tampered-for-e2e")

    observation = seeded_pilot.verify_latest_ledger_entry().observation
    assert observation.result == observation.Result.MISMATCH
