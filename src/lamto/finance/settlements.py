import re

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from lamto.accounts.services import require_management
from lamto.audit.services import record_audit
from lamto.documents.models import Document, DocumentVersion
from lamto.evidence.models import EvidenceType
from lamto.evidence.services import queue_platform_event, utc_rfc3339
from django.utils.translation import gettext_lazy as _

from .models import Proposal, Settlement


def normalize_bank_reference(value):
    value = re.sub(r"\s+", " ", str(value or "").strip()).upper()
    if not value:
        raise ValidationError(_("Bank reference is required."))
    return value


def _require_proof(proof, building_id, *, lock=False):
    qs = DocumentVersion.objects.select_related("document").filter(pk=getattr(proof, "pk", None))
    if lock:
        qs = qs.select_for_update()
    version = qs.first()
    if not version or version.document.kind != Document.Kind.PAYMENT_PROOF or version.document.building_id != building_id or version.scan_status != DocumentVersion.ScanStatus.CLEAN:
        raise ValidationError(_("Settlement evidence requires a clean payment proof in the proposal building."))
    return version


def build_settlement_evidence_payload(settlement):
    proposal = settlement.proposal
    return {"schema": "settlement.v1", "settlement_id": settlement.pk, "proposal_id": proposal.pk, "proposal_version": proposal.current_version.number, "amount_vnd": settlement.amount_vnd, "payee_name": settlement.payee_name, "bank_reference": normalize_bank_reference(settlement.bank_reference), "transfer_sha256": settlement.transfer.sha256, "ack_sha256": settlement.ack.sha256, "transfer_recorded_at": utc_rfc3339(settlement.transfer_recorded_at), "ack_recorded_at": utc_rfc3339(settlement.ack_recorded_at)}


@transaction.atomic
def record_transfer(proposal, membership, *, amount_vnd, payee_name, bank_reference, transfer):
    proposal = Proposal.objects.select_for_update().get(pk=proposal.pk)
    actor = require_management(membership.user, proposal.building_id)
    if proposal.status != Proposal.Status.COMPLETED:
        raise ValidationError(_("Only completed proposals can be settled."))
    if Settlement.objects.filter(proposal=proposal).exists():
        raise ValidationError(_("Settlement already exists for this proposal."))
    if type(amount_vnd) is not int or amount_vnd <= 0:
        raise ValidationError(_("Settlement amount must be a positive integer VND amount."))
    if proposal.current_version is None or amount_vnd != proposal.current_version.amount_vnd:
        raise ValidationError(_("Settlement amount must match the published proposal amount."))
    payee_name = str(payee_name or "").strip()
    if not payee_name:
        raise ValidationError(_("Payee name is required."))
    original = _require_proof(transfer, proposal.building_id, lock=True)
    settlement = Settlement.objects.create(proposal=proposal, amount_vnd=amount_vnd, payee_name=payee_name, bank_reference=normalize_bank_reference(bank_reference), transfer=original, transfer_recorded_by=actor, transfer_recorded_at=timezone.now())
    record_audit(actor.user, actor, "settlement.transfer_recorded", "Settlement", str(settlement.pk), "accepted")
    return settlement


@transaction.atomic
def record_acknowledgement(settlement, membership, *, ack, event_id):
    settlement = Settlement.objects.select_for_update().get(pk=settlement.pk)
    actor = require_management(membership.user, settlement.proposal.building_id)
    if settlement.settled_at is not None:
        raise ValidationError(_("Settlement is already settled."))
    original = _require_proof(ack, settlement.proposal.building_id, lock=True)
    now = timezone.now()
    settlement.ack, settlement.ack_recorded_by, settlement.ack_recorded_at = original, actor, now
    event = queue_platform_event(event_id, EvidenceType.SETTLEMENT, build_settlement_evidence_payload(settlement), "0x" + settlement.proposal.current_version.outbox_event.payload_hash, settlement.proposal.building)
    settlement.outbox_event, settlement.settled_at = event, now
    settlement.save(update_fields=["ack", "ack_recorded_by", "ack_recorded_at", "outbox_event", "settled_at"])
    from .fund import create_settlement_outflow
    create_settlement_outflow(settlement)
    from .publication import publish_settlement_entry
    publish_settlement_entry(settlement)
    record_audit(actor.user, actor, "settlement.settled", "Settlement", str(settlement.pk), "accepted", {"event_id": event.event_id})
    from lamto.notifications.hooks import notify_settled
    transaction.on_commit(lambda: notify_settled(settlement))
    return settlement
