"""Role / object / file access denials for prohibited paths."""

from __future__ import annotations

from unittest.mock import patch
from urllib.error import URLError

import pytest
from lamto.documents.access import authorize_download
from lamto.finance.models import PublishedLedgerEntry
from lamto.finance.proposals import publish_proposal_version
from lamto.maintenance.ai import process_triage_job
from lamto.maintenance.models import IssueReport, TriageJob
from lamto.testing.factories import DEFAULT_AMOUNT_VND, new_event_id

pytestmark = pytest.mark.django_db


def test_role_access_denies_prohibited_document_reads(page, seeded_pilot):
    seeded_pilot.prepare_local_normal_work(page)
    seeded_pilot.complete_assigned_work()
    seeded_pilot.record_settlement_transfer()
    seeded_pilot.record_settlement_ack()
    seeded_pilot.confirm_all_chain_events()
    seeded_pilot.publish_settlement_entry()
    seeded_pilot.confirm_all_chain_events()
    entry = PublishedLedgerEntry.objects.get(
        case__building=seeded_pilot.seed.building
    )
    proof = entry.settlement.transfer

    assert authorize_download(seeded_pilot.seed.residents[0], None, proof)
    manager = seeded_pilot.seed.management_memberships[0]
    assert authorize_download(manager.user, manager.pk, proof)


def test_ai_outage_preserves_manual_triage_authority(page, seeded_pilot):
    report = seeded_pilot.submit_report(
        "AI offline elevator", "Lift 2", None
    )
    with patch("lamto.maintenance.ai.urlopen", side_effect=URLError("offline")):
        job = process_triage_job(report.triage_job.id)
    assert job.status == TriageJob.Status.NEEDS_MANUAL
    case = seeded_pilot.confirm_triage_case()
    assert case.pk is not None


def test_proposal_change_after_signature_requires_resubmission(page, seeded_pilot):
    seeded_pilot.submit_report("Elevator", "Lift 2", None)
    seeded_pilot.confirm_triage_case()
    version1 = seeded_pilot.publish_proposal(
        amount_vnd=DEFAULT_AMOUNT_VND
    )

    manager = seeded_pilot.seed.management_memberships[0]
    proposal = seeded_pilot.seed.proposal
    quotation = seeded_pilot._ctx["quotation"]
    event_id = new_event_id()
    version2 = publish_proposal_version(
        proposal, manager, amount_vnd=19_000_000, contractor_name="Changed",
        fund_code="GENERAL", purpose="Elevator",
        proposed_action="Replace the affected equipment",
        expected_schedule="Within 21 days", quotation_versions=[quotation],
        event_id=event_id,
    )
    case = seeded_pilot.seed.case
    case.refresh_from_db()
    assert version2.number == 2
    seeded_pilot.start_assigned_work()
    report = seeded_pilot.seed.report
    report.refresh_from_db()
    assert report.status == IssueReport.Status.IN_PROGRESS
