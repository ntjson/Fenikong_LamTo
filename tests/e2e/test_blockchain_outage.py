"""Chain paused: the off-chain ledger still publishes once settlement is recorded."""

from __future__ import annotations

import pytest
from django.test import override_settings

pytestmark = pytest.mark.django_db


@override_settings(LANGUAGE_CODE="en-us")  # asserts English source strings
def test_normal_work_can_start_pending_anchor_and_publish_offchain(page, seeded_pilot):
    seeded_pilot.pause_chain()
    seeded_pilot.prepare_local_normal_work(page)
    work = seeded_pilot.start_assigned_work()

    assert work.verification_label == "Pending anchoring"
    seeded_pilot.complete_assigned_work()
    seeded_pilot.record_settlement_transfer()
    seeded_pilot.record_settlement_ack()
    before_ids = seeded_pilot.latest_outbox_event_ids()
    blocked = seeded_pilot.attempt_publication()

    assert not blocked.blocked
    assert seeded_pilot.ledger_count() == 1

    seeded_pilot.resume_chain()
    seeded_pilot.confirm_all_chain_events()
    assert seeded_pilot.latest_outbox_event_ids() == before_ids
    seeded_pilot.confirm_all_chain_events()
    assert seeded_pilot.ledger_count() == 1
