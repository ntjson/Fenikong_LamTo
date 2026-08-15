"""Cross-role normal flow (domain driver; browser optional)."""

from __future__ import annotations

import pytest

from lamto.evidence.models import BlockchainOutboxEvent, is_settled
from lamto.testing.factories import DEFAULT_AMOUNT_VND

pytestmark = pytest.mark.django_db


def test_direct_outcome_c_happy_path(seeded_pilot):
    seeded_pilot.submit_report("Lift doors stick", "Building B / Lift 2")
    seeded_pilot.confirm_triage_case()
    seeded_pilot.start_assigned_work()
    seeded_pilot.publish_work_progress()
    seeded_pilot.complete_assigned_work()

    rating = seeded_pilot.rate_completed_case(satisfied=True)

    assert rating.satisfied is True
    assert not BlockchainOutboxEvent.objects.filter(
        building=seeded_pilot.seed.building
    ).exists()


def test_realistic_normal_flow(page, seeded_pilot):
    seeded_pilot.submit_report(
        "Elevator shakes heavily",
        "Building B / Lift 2",
        "tests/fixtures/elevator.jpg",
    )

    seeded_pilot.confirm_triage_case()
    proposal_version = seeded_pilot.publish_proposal(amount_vnd=DEFAULT_AMOUNT_VND)
    seeded_pilot.decide_proposal(proceed=True)

    seeded_pilot.start_assigned_work()
    seeded_pilot.publish_work_progress()
    seeded_pilot.complete_assigned_work()
    seeded_pilot.record_settlement_transfer()
    seeded_pilot.record_settlement_ack()
    seeded_pilot.confirm_all_chain_events()
    rating = seeded_pilot.rate_completed_case(satisfied=True)
    seeded_pilot.confirm_all_chain_events()

    ledger = seeded_pilot.open_latest_ledger_entry()
    settlement = seeded_pilot._ctx["settlement"]
    proposal_version.outbox_event.refresh_from_db()
    settlement.outbox_event.refresh_from_db()
    assert is_settled(proposal_version.outbox_event.status)
    assert is_settled(settlement.outbox_event.status)
    assert ledger.entry.settlement_id == settlement.pk
    assert rating.satisfied is True
    assert ledger.actual_cost_vnd == DEFAULT_AMOUNT_VND
    assert ledger.status == "Record verified"
    assert ledger.has_documents()

    verification = seeded_pilot.verify_latest_ledger_entry()
    assert verification.document_hashes_match
    assert verification.chain_events_match
    assert verification.recomputed_fund_balance_vnd == ledger.current_fund_balance_vnd


def test_standalone_proposal_happy_path(seeded_pilot):
    proposal_version = seeded_pilot.publish_standalone_proposal(
        amount_vnd=DEFAULT_AMOUNT_VND
    )
    seeded_pilot.decide_proposal(proceed=True)
    seeded_pilot.publish_proposal_progress()
    seeded_pilot.complete_proposal_work()
    seeded_pilot.record_settlement_transfer()
    settlement = seeded_pilot.record_settlement_ack()
    seeded_pilot.confirm_all_chain_events()
    rating = seeded_pilot.rate_completed_proposal(satisfied=True)

    ledger = seeded_pilot.open_latest_ledger_entry()
    proposal_version.outbox_event.refresh_from_db()
    settlement.outbox_event.refresh_from_db()
    assert is_settled(proposal_version.outbox_event.status)
    assert is_settled(settlement.outbox_event.status)
    assert ledger.entry.settlement_id == settlement.pk
    assert rating.proposal_id == seeded_pilot.seed.proposal.pk
    assert rating.satisfied is True
    assert ledger.actual_cost_vnd == DEFAULT_AMOUNT_VND
    assert ledger.status == "Record verified"
    assert ledger.has_documents()

    verification = seeded_pilot.verify_latest_ledger_entry()
    assert verification.document_hashes_match
    assert verification.chain_events_match
    assert verification.recomputed_fund_balance_vnd == ledger.current_fund_balance_vnd
