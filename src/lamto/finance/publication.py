from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from lamto.audit.services import record_audit
from django.utils.translation import gettext_lazy as _

from .models import Proposal, PublishedLedgerEntry


def _load_execution_chain(proposal):
    try:
        settlement = proposal.settlement
    except Proposal.settlement.RelatedObjectDoesNotExist as exc:
        raise ValidationError(_("Settlement is required before publication.")) from exc
    if settlement.settled_at is None or settlement.outbox_event_id is None:
        raise ValidationError(_("Settlement must be completed before publication."))
    return settlement


def _resident_payload(proposal, version, settlement, document_hashes):
    case = proposal.case
    return {
        "report_id": case.decision.report_id if case else None,
        "case_id": case.pk if case else None,
        "proposal_id": proposal.pk,
        "proposal_version": version.number,
        "proposed_amount_vnd": version.amount_vnd,
        "actual_cost_vnd": settlement.amount_vnd,
        "contractor_name": version.contractor_name,
        "document_hashes": document_hashes,
        "settlement": {
            "settlement_id": settlement.pk,
            "settlement_event_hash": settlement.outbox_event.payload_hash,
        },
    }


def _collect_document_checks(proposal, version, settlement, using="default"):
    from lamto.documents.models import DocumentVersion

    checks = []
    for item in version.snapshot.get("quotation_versions", []):
        quotation = DocumentVersion.objects.using(using).get(pk=item["version_id"])
        checks.append((quotation, item["sha256"], "QUOTATION"))
    checks.extend((
        (settlement.transfer, settlement.transfer.sha256, "SETTLEMENT_TRANSFER"),
        (settlement.ack, settlement.ack.sha256, "SETTLEMENT_ACK"),
    ))
    return checks


@transaction.atomic
def publish_settlement_entry(settlement) -> PublishedLedgerEntry:
    settlement = type(settlement).objects.select_for_update(of=("self",)).select_related(
        "proposal__current_version", "proposal__case__decision__report", "transfer",
        "ack", "outbox_event",
    ).get(pk=settlement.pk)
    existing = PublishedLedgerEntry.objects.filter(settlement=settlement).first()
    if existing:
        return existing
    if settlement.settled_at is None or settlement.outbox_event_id is None:
        raise ValidationError(_("Settlement must be completed before publication."))
    proposal, version = settlement.proposal, settlement.proposal.current_version
    if version is None:
        raise ValidationError(_("A current proposal version is required."))
    hashes = sorted({document.sha256 for document, _expected, _gate in _collect_document_checks(proposal, version, settlement)})
    entry = PublishedLedgerEntry.objects.create(
        resident_payload=_resident_payload(proposal, version, settlement, hashes),
        case=proposal.case,
        proposal=proposal,
        settlement=settlement,
        actual_cost_vnd=settlement.amount_vnd,
        contractor_name=version.contractor_name,
        published_at=timezone.now(),
    )
    record_audit(settlement.ack_recorded_by.user, settlement.ack_recorded_by, "ledger.published", "PublishedLedgerEntry", str(entry.pk), "accepted")
    return entry
