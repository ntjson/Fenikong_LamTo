"""Public Evidence explorer routes (ADR 0004).

The explorer namespace lives outside the Management workspace and resident API
auth boundaries: it is unauthenticated, and its identity is the opaque
``Proposal.public_token`` minted at first publication.
"""

import datetime
import logging

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET

from lamto.api.downloads import content_disposition_inline
from lamto.documents.access import DocumentIntegrityError, read_version_bytes
from lamto.evidence.models import BlockchainOutboxEvent, EvidenceLevel, evidence_level
from lamto.finance.models import Proposal, VerificationObservation
from lamto.finance.selectors import ledger_story_fields

logger = logging.getLogger(__name__)

EVIDENCE_LEVEL_LABELS = {
    EvidenceLevel.CHAIN_CONFIRMED: "Đã neo trên blockchain",
    EvidenceLevel.LOCAL_SIGNED: "Đã ký — chưa bật neo blockchain",
    EvidenceLevel.PENDING: "Đang chờ neo blockchain",
    EvidenceLevel.MISMATCH: "Phát hiện sai lệch dữ liệu",
}

EVIDENCE_LEVEL_TONES = {
    EvidenceLevel.CHAIN_CONFIRMED: "verified",
    EvidenceLevel.LOCAL_SIGNED: "info",
    EvidenceLevel.PENDING: "warning",
    EvidenceLevel.MISMATCH: "mismatch",
}

INTEGRITY_STATUS_LABELS = {
    VerificationObservation.Result.VERIFIED: "Bản ghi đã xác minh",
    VerificationObservation.Result.MISMATCH: "Phát hiện sai lệch toàn vẹn",
    VerificationObservation.Result.UNAVAILABLE: "Chưa kiểm tra được tính toàn vẹn",
    "UNCHECKED": "Đã công bố — chưa kiểm tra toàn vẹn",
}

INTEGRITY_STATUS_TONES = {
    VerificationObservation.Result.VERIFIED: "verified",
    VerificationObservation.Result.MISMATCH: "mismatch",
    VerificationObservation.Result.UNAVAILABLE: "warning",
    "UNCHECKED": "info",
}


def _chain_explorer_tx_url(tx_hash: str) -> str:
    """Build a link to a transaction in the external chain explorer, if configured."""
    base_url = (getattr(settings, "CHAIN_EXPLORER_URL", "") or "").rstrip("/")
    if not base_url or not tx_hash:
        return ""
    return f"{base_url}/tx/{tx_hash}"


def _make_chain_step(
    level=EvidenceLevel.PENDING,
    payload_hash="",
    transaction_hash="",
    transaction_url="",
    confirmation_time=None,
):
    return {
        "evidence_level": level,
        "evidence_label": EVIDENCE_LEVEL_LABELS.get(
            level, EVIDENCE_LEVEL_LABELS[EvidenceLevel.PENDING]
        ),
        "evidence_tone": EVIDENCE_LEVEL_TONES.get(
            level, EVIDENCE_LEVEL_TONES[EvidenceLevel.PENDING]
        ),
        "payload_hash": payload_hash,
        "transaction_hash": transaction_hash,
        "transaction_url": transaction_url,
        "confirmation_time": confirmation_time,
    }


def _read_chain_step(event):
    """Read one outbox event against the chain live at page load.

    Returns (step_dict, chain_unreachable_bool).
    """
    if event is None:
        return _make_chain_step(), False

    tx_hash = event.transaction_hash or ""
    tx_url = _chain_explorer_tx_url(tx_hash)
    conf_time = event.chain_block_timestamp or event.confirmed_at

    # Anchoring disabled or local settlement: pure local truth
    if (
        settings.EVIDENCE_ANCHORING_BACKEND == "disabled"
        or event.status == BlockchainOutboxEvent.Status.LOCAL
    ):
        return _make_chain_step(
            level=EvidenceLevel.LOCAL_SIGNED,
            payload_hash=event.payload_hash,
            transaction_hash=tx_hash,
            transaction_url=tx_url,
            confirmation_time=conf_time,
        ), False

    if event.status == BlockchainOutboxEvent.Status.MISMATCH:
        return _make_chain_step(
            level=EvidenceLevel.MISMATCH,
            payload_hash=event.payload_hash,
            transaction_hash=tx_hash,
            transaction_url=tx_url,
            confirmation_time=conf_time,
        ), False

    try:
        from lamto.evidence.chain import EvidenceRegistryClient

        client = EvidenceRegistryClient()
        record = client.find(event)
    except Exception as exc:
        logger.warning("Explorer live chain read failed for %s: %s", event.event_id, exc)
        stored_level = evidence_level(event.status)
        return _make_chain_step(
            level=stored_level,
            payload_hash=event.payload_hash,
            transaction_hash=tx_hash,
            transaction_url=tx_url,
            confirmation_time=conf_time,
        ), True

    if record is None:
        stored_level = evidence_level(event.status)
        return _make_chain_step(
            level=stored_level,
            payload_hash=event.payload_hash,
            transaction_hash=tx_hash,
            transaction_url=tx_url,
            confirmation_time=conf_time,
        ), False

    on_chain_hash = record.payload_hash.removeprefix("0x").lower()
    local_hash = event.payload_hash.removeprefix("0x").lower()
    if on_chain_hash != local_hash:
        level = EvidenceLevel.MISMATCH
    else:
        level = EvidenceLevel.CHAIN_CONFIRMED

    if record.recorded_at > 0:
        conf_time = datetime.datetime.fromtimestamp(
            record.recorded_at, tz=datetime.timezone.utc
        )

    return _make_chain_step(
        level=level,
        payload_hash=event.payload_hash,
        transaction_hash=tx_hash,
        transaction_url=tx_url,
        confirmation_time=conf_time,
    ), False


@require_GET
def explorer_page(request, public_token):
    """Public Evidence explorer detail page for one proposal chain."""
    proposal = (
        Proposal.objects.select_related(
            "building",
            "case",
            "current_version",
            "decided_by__user",
            "settlement__transfer",
            "settlement__settled_by__user",
            "settlement__outbox_event",
            "published_ledger_entry",
        )
        .prefetch_related(
            "versions__creator_membership__user",
            "versions__outbox_event",
            "versions__quotations",
        )
        .filter(public_token=public_token)
        .first()
    )
    if proposal is None:
        raise Http404("Proposal not found.")

    chain_unreachable = False
    timeline_steps = []

    # 1. Published proposal versions in ascending number order
    for version in proposal.versions.order_by("number"):
        chain_step, step_unreachable = _read_chain_step(version.outbox_event)
        if step_unreachable:
            chain_unreachable = True
        timeline_steps.append(
            {
                "kind": "proposal_version",
                "number": version.number,
                "title": f"Phiên bản đề xuất #{version.number}",
                "amount_vnd": version.amount_vnd,
                "contractor_name": version.contractor_name,
                "purpose": version.purpose,
                "proposed_action": version.proposed_action,
                "expected_schedule": version.expected_schedule,
                "creator_name": version.creator_membership.user.display_name,
                "created_at": version.created_at,
                "quotations": [
                    {
                        "filename": q.filename,
                        "sha256": q.sha256,
                        "byte_size": q.byte_size,
                    }
                    for q in version.quotations.all()
                ],
                "chain": chain_step,
            }
        )

    # 2. Settlement step (settled or pending)
    settlement = getattr(proposal, "settlement", None)
    if settlement is not None:
        chain_step, step_unreachable = _read_chain_step(settlement.outbox_event)
        if step_unreachable:
            chain_unreachable = True
        timeline_steps.append(
            {
                "kind": "settlement",
                "is_settled": True,
                "title": "Nghiệm thu và thanh toán",
                "amount_vnd": settlement.amount_vnd,
                "contractor_name": (
                    proposal.current_version.contractor_name
                    if proposal.current_version
                    else ""
                ),
                "settled_by": settlement.settled_by.user.display_name,
                "settled_at": settlement.settled_at,
                "transfer": {
                    "filename": settlement.transfer.filename,
                    "sha256": settlement.transfer.sha256,
                    "byte_size": settlement.transfer.byte_size,
                },
                "chain": chain_step,
            }
        )
    else:
        timeline_steps.append(
            {
                "kind": "settlement",
                "is_settled": False,
                "title": "Nghiệm thu và thanh toán",
                "chain": {
                    "evidence_level": EvidenceLevel.PENDING,
                    "evidence_label": EVIDENCE_LEVEL_LABELS[EvidenceLevel.PENDING],
                    "evidence_tone": EVIDENCE_LEVEL_TONES[EvidenceLevel.PENDING],
                    "payload_hash": "",
                    "transaction_hash": "",
                    "transaction_url": "",
                    "confirmation_time": None,
                },
            }
        )

    # 3. Resident-ledger parity fields
    entry = getattr(proposal, "published_ledger_entry", None)
    if entry is not None:
        story = ledger_story_fields(entry)
        what_was_fixed = story["what_was_fixed"]
        why = story["why"]
        published_at = entry.published_at
    else:
        case = proposal.case
        work = (
            case.updates.order_by("-created_at", "-pk").first()
            if case
            else proposal.updates.order_by("-created_at", "-pk").first()
        )
        report = None
        decision = getattr(case, "decision", None) if case else None
        if decision is not None:
            report = getattr(decision, "report", None)
        result = (getattr(work, "result", None) or "").strip()
        cause = (getattr(work, "cause", None) or "").strip()
        report_text = (getattr(report, "text", None) or "").strip() if report else ""
        category = (getattr(case, "category", None) or "").strip()
        purpose = (
            (getattr(proposal.current_version, "purpose", None) or "").strip()
            if proposal.current_version
            else ""
        )
        what_was_fixed = result or report_text or category or purpose
        why = cause or category or purpose
        published_at = None

    approvers = []
    if proposal.decided_by:
        approvers.append(proposal.decided_by.user.display_name)

    # 4. Latest independent integrity observation
    integrity_observation = None
    if entry is not None:
        latest = entry.verification_observations.order_by("-observed_at", "-pk").first()
        if latest is not None:
            verifier = (
                latest.details.get("verifier")
                or (
                    entry.settlement.settled_by.user.display_name
                    if entry.settlement
                    else ""
                )
                or "Ban quản lý"
            )
            integrity_observation = {
                "result": latest.result,
                "label": INTEGRITY_STATUS_LABELS.get(
                    latest.result, latest.get_result_display()
                ),
                "tone": INTEGRITY_STATUS_TONES.get(latest.result, "warning"),
                "verifier": verifier,
                "observed_at": latest.observed_at,
            }

    context = {
        "proposal": proposal,
        "public_token": public_token,
        "building": proposal.building,
        "timeline_steps": timeline_steps,
        "what_was_fixed": what_was_fixed,
        "why": why,
        "published_at": published_at,
        "approvers": approvers,
        "integrity_observation": integrity_observation,
        "chain_unreachable": chain_unreachable,
    }
    return render(request, "explorer/detail.html", context)

logger = logging.getLogger(__name__)


@require_GET
def document_download(request, public_token, sha256):
    """Serve one transfer-proof document, content-addressed by its SHA-256.

    The URL is part of the proof: the served bytes must re-verify against the
    anchored hash, or nothing is served. Unknown tokens and unknown hashes are
    indistinguishable — both are plain not-found. Tamper detection is a
    first-class error, never a silent serving (409, matching the staff
    document route).
    """
    proposal = (
        Proposal.objects.select_related("settlement__transfer")
        .filter(public_token=public_token)
        .first()
    )
    if proposal is None:
        raise Http404("Document not found.")
    settlement = getattr(proposal, "settlement", None)
    if settlement is None:
        raise Http404("Document not found.")
    transfer = settlement.transfer
    if sha256 != transfer.sha256:
        raise Http404("Document not found.")
    try:
        data = read_version_bytes(transfer)
    except DocumentIntegrityError as error:
        logger.warning("Explorer document refused: %s", error)
        return HttpResponse(
            str(error), content_type="text/plain; charset=utf-8", status=409
        )
    response = HttpResponse(
        data,
        content_type=transfer.content_type or "application/octet-stream",
    )
    response["Cache-Control"] = "no-store"
    response["Content-Disposition"] = content_disposition_inline(transfer.filename)
    return response
