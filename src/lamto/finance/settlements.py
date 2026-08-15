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
    return {"schema": "settlement.v2", "settlement_id": settlement.pk, "proposal_id": proposal.pk, "proposal_version": proposal.current_version.number, "amount_vnd": settlement.amount_vnd, "transfer_sha256": settlement.transfer.sha256, "settled_at": utc_rfc3339(settlement.settled_at)}


@transaction.atomic
def record_settlement(proposal, membership, *, transfer, event_id):
    """Settle a completed proposal against its transfer proof (ADR 0002).

    The amount is not an argument: it is the published proposal amount, which is
    frozen and anchored, so there is nothing for a caller to disagree with.
    """
    proposal = Proposal.objects.select_for_update().get(pk=proposal.pk)
    actor = require_management(membership.user, proposal.building_id)
    if proposal.status != Proposal.Status.COMPLETED:
        raise ValidationError(_("Only completed proposals can be settled."))
    if Settlement.objects.filter(proposal=proposal).exists():
        raise ValidationError(_("Settlement already exists for this proposal."))
    if proposal.current_version is None:
        raise ValidationError(_("A current proposal version is required."))
    original = _require_proof(transfer, proposal.building_id, lock=True)
    settlement = Settlement.objects.create(
        proposal=proposal, amount_vnd=proposal.current_version.amount_vnd,
        transfer=original, settled_by=actor, settled_at=timezone.now(),
    )
    event = queue_platform_event(
        event_id, EvidenceType.SETTLEMENT, build_settlement_evidence_payload(settlement),
        "0x" + proposal.current_version.outbox_event.payload_hash, proposal.building,
    )
    settlement.outbox_event = event
    settlement.save(update_fields=["outbox_event"])
    from .fund import create_settlement_outflow
    create_settlement_outflow(settlement)
    from .publication import publish_settlement_entry
    publish_settlement_entry(settlement)
    record_audit(actor.user, actor, "settlement.settled", "Settlement", str(settlement.pk), "accepted", {"event_id": event.event_id})
    from lamto.notifications.hooks import notify_settled
    transaction.on_commit(lambda: notify_settled(settlement))
    return settlement
