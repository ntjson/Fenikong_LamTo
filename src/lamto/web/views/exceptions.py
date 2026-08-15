"""Staff Exceptions review: inspect trust-critical failures, record a named response.

An exception clears only when its source clears (a verification stops
mismatching, an anchor stops failing, a quarantined file expires). What this
surface adds is accountability: each item gets a page where a named person
inspects the real record and files an append-only response in the audit log.
"""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from lamto.audit.models import AuditEvent
from lamto.audit.services import record_audit
from lamto.documents.models import QuarantinedUpload
from lamto.evidence.models import BlockchainOutboxEvent
from lamto.finance.models import PublishedLedgerEntry, VerificationObservation
from lamto.web.action_inbox import mismatched_ledger_entry_ids
from lamto.web.staff import require_management_context, staff_context

RESPONSE_ACTION = "exception.review"

EXCEPTION_TARGET_TYPES = {
    "integrity_mismatch": "PublishedLedgerEntry",
    "failed_outbox": "BlockchainOutboxEvent",
    "quarantined_upload": "QuarantinedUpload",
}

LIST_CAP = 50


def _responses_for(target_type: str, target_ids) -> dict[str, list[AuditEvent]]:
    """Recorded responses per target id, newest first."""
    rows = (
        AuditEvent.objects.filter(
            action=RESPONSE_ACTION,
            target_type=target_type,
            target_id__in=[str(pk) for pk in target_ids],
        )
        .select_related("actor")
        .order_by("-created_at")
    )
    grouped: dict[str, list[AuditEvent]] = {}
    for row in rows:
        grouped.setdefault(row.target_id, []).append(row)
    return grouped


def _get_target(kind: str, pk: int, building_id: int):
    if kind == "integrity_mismatch":
        return get_object_or_404(
            PublishedLedgerEntry.objects.select_related("proposal", "settlement"),
            pk=pk,
            proposal__building_id=building_id,
        )
    if kind == "failed_outbox":
        return get_object_or_404(BlockchainOutboxEvent, pk=pk, building_id=building_id)
    if kind == "quarantined_upload":
        return get_object_or_404(
            QuarantinedUpload.objects.select_related("uploader"),
            pk=pk,
            building_id=building_id,
        )
    raise Http404("Unknown exception kind.")


@login_required
@require_http_methods(["GET"])
def exception_list(request):
    membership, memberships = require_management_context(request)
    building_id = membership.building_id

    mismatch_ids = mismatched_ledger_entry_ids(building_id)
    mismatch_entries = list(
        PublishedLedgerEntry.objects.filter(pk__in=mismatch_ids).select_related(
            "proposal"
        )
    )
    mismatch_entries.sort(key=lambda entry: mismatch_ids.index(entry.pk))

    outbox_qs = BlockchainOutboxEvent.objects.filter(
        status=BlockchainOutboxEvent.Status.FAILED, building_id=building_id
    ).order_by("-updated_at")
    outbox_total = outbox_qs.count()
    outbox_events = list(outbox_qs[:LIST_CAP])

    quarantine_qs = QuarantinedUpload.objects.filter(building_id=building_id).order_by(
        "-created_at"
    )
    quarantine_total = quarantine_qs.count()
    quarantined = list(quarantine_qs[:LIST_CAP])

    mismatch_responses = _responses_for(
        "PublishedLedgerEntry", [entry.pk for entry in mismatch_entries]
    )
    outbox_responses = _responses_for(
        "BlockchainOutboxEvent", [event.pk for event in outbox_events]
    )
    quarantine_responses = _responses_for(
        "QuarantinedUpload", [upload.pk for upload in quarantined]
    )

    return render(
        request,
        "web/staff/exceptions.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="ops",
            ops_active="exceptions",
            mismatch_items=[
                {"entry": entry, "reviewed": str(entry.pk) in mismatch_responses}
                for entry in mismatch_entries
            ],
            outbox_items=[
                {"event": event, "reviewed": str(event.pk) in outbox_responses}
                for event in outbox_events
            ],
            outbox_total=outbox_total,
            outbox_capped=outbox_total > len(outbox_events),
            quarantine_items=[
                {
                    "upload": upload,
                    "reviewed": str(upload.pk) in quarantine_responses,
                    "expired": upload.retention_expires_at <= timezone.now(),
                }
                for upload in quarantined
            ],
            quarantine_total=quarantine_total,
            quarantine_capped=quarantine_total > len(quarantined),
            list_cap=LIST_CAP,
        ),
    )


@login_required
@require_http_methods(["GET", "POST"])
def exception_review(request, kind, pk):
    if kind not in EXCEPTION_TARGET_TYPES:
        raise Http404("Unknown exception kind.")
    membership, memberships = require_management_context(request)
    target = _get_target(kind, pk, membership.building_id)
    target_type = EXCEPTION_TARGET_TYPES[kind]

    note = ""
    if request.method == "POST":
        note = (request.POST.get("note") or "").strip()
        if not note:
            messages.error(
                request,
                _("Write what you checked or did before recording; the response cannot be empty."),
            )
        else:
            record_audit(
                request.user,
                membership,
                RESPONSE_ACTION,
                target_type,
                str(pk),
                "accepted",
                {"kind": kind, "note": note},
            )
            messages.success(
                request,
                _("Response recorded in the audit log under your name."),
            )
            return redirect("web:exception-review", kind=kind, pk=pk)

    extra: dict = {}
    if kind == "integrity_mismatch":
        latest = (
            VerificationObservation.objects.filter(published_entry_id=target.pk)
            .order_by("-observed_at", "-pk")
            .first()
        )
        extra = {
            "entry": target,
            "latest_observation": latest,
            "cleared": bool(
                latest and latest.result != VerificationObservation.Result.MISMATCH
            ),
        }
    elif kind == "failed_outbox":
        extra = {
            "event": target,
            "cleared": target.status != BlockchainOutboxEvent.Status.FAILED,
        }
    else:
        extra = {
            "upload": target,
            "expired": target.retention_expires_at <= timezone.now(),
        }

    return render(
        request,
        "web/staff/exception_review.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="ops",
            ops_active="exceptions",
            kind=kind,
            target_pk=pk,
            note=note,
            responses=_responses_for(target_type, [pk]).get(str(pk), []),
            **extra,
        ),
    )
