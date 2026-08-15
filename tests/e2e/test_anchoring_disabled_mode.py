"""Disabled anchoring: publication and fund flows settle LOCAL (spec 5.2/5.4).

The driver's chain is paused so it never fake-confirms; the REAL worker
(`process_due_outbox_events`) performs every settlement, constructing no chain
client. Nothing may present LOCAL_SIGNED as chain confirmation.
"""

from __future__ import annotations

import pytest
from lamto.documents.models import Document
from lamto.evidence.models import BlockchainOutboxEvent, EvidenceLevel
from lamto.evidence.worker import process_due_outbox_events
from lamto.finance.fund import (
    fund_balance,
    get_or_create_fund,
    record_fund_source,
    verify_fund_source,
)
from lamto.finance.integrity import verify_published_entry
from lamto.finance.models import (
    MaintenanceFundEntry,
    PublishedLedgerEntry,
    VerificationObservation,
)
from lamto.finance.selectors import published_ledger_entries
from lamto.testing.factories import PilotDomainDriver, seed_pilot_world

pytestmark = pytest.mark.django_db

Status = BlockchainOutboxEvent.Status


def _settle_locally():
    """Run the real worker; in disabled mode every due event settles LOCAL."""
    for event in process_due_outbox_events():
        assert event.status == Status.LOCAL, event.status


def test_disabled_mode_publication_and_fund_flows(page, temp_storage, settings):
    settings.EVIDENCE_ANCHORING_BACKEND = "disabled"
    seed = seed_pilot_world(
        building_name="Offchain Building", create_sample_report=False
    )
    driver = PilotDomainDriver(seed)
    # seed_opening_fund fake-confirms its two events (a legitimate mixed
    # history); everything queued after this line must settle LOCAL.
    preconfirmed = set(
        BlockchainOutboxEvent.objects.filter(status=Status.CONFIRMED).values_list(
            "pk", flat=True
        )
    )
    driver.pause_chain()

    # --- Publication flow -------------------------------------------------
    driver.prepare_local_normal_work(page)
    driver.complete_assigned_work()
    driver.record_settlement_transfer()
    driver.record_settlement_ack()
    _settle_locally()

    entry = PublishedLedgerEntry.objects.get(case__building=seed.building)
    entry.settlement.outbox_event.refresh_from_db()
    assert entry.settlement.outbox_event.status == Status.LOCAL
    assert entry.settlement.outbox_event.evidence_level == EvidenceLevel.LOCAL_SIGNED

    # Nothing queued in disabled mode ever became CONFIRMED, nothing is pending.
    flow_events = BlockchainOutboxEvent.objects.filter(building=seed.building)
    assert not flow_events.filter(status=Status.PENDING).exists()
    assert not (
        flow_events.filter(status=Status.CONFIRMED)
        .exclude(pk__in=preconfirmed)
        .exists()
    )

    # Published data remains available through the resident API.
    assert entry.pk in [row.pk for row in published_ledger_entries(seed.building.pk)]

    # Integrity observation: documents checked, chain skipped, never faked.
    observation = verify_published_entry(entry.pk)
    assert observation.result == VerificationObservation.Result.VERIFIED
    assert observation.details.get("anchoring_backend") == "disabled"
    assert {c["result"] for c in observation.details["chain_checks"]} == {
        "SKIPPED_ANCHORING_DISABLED"
    }

    balance_after_publication = fund_balance(seed.building.pk, verified_only=True)

    # --- Fund flow (record then self-confirm) -----------------------------
    fund = get_or_create_fund(seed.building)
    (recorder,) = seed.management_memberships
    evidence = seed.document(
        Document.Kind.CONTRACT, recorder.user, "offchain-inflow"
    )
    inflow = record_fund_source(
        fund,
        MaintenanceFundEntry.EntryType.INFLOW,
        5_000_000,
        evidence,
        recorder,
    )
    verify_fund_source(inflow, recorder)
    assert (
        fund_balance(seed.building.pk, verified_only=True)
        == balance_after_publication + 5_000_000
    )
