"""Management CSV exports with formula neutralization."""

from __future__ import annotations

import csv
from datetime import datetime, timezone as dt_timezone

from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET

from lamto.audit.models import AuditEvent
from lamto.audit.services import record_audit
from lamto.documents.models import DocumentVersion
from lamto.evidence.models import BlockchainOutboxEvent
from lamto.finance.models import MaintenanceFundEntry, VerificationObservation
from lamto.web.staff import require_management_context, staff_context


FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")

EXPORT_KINDS = (
    ("audit_events", _("Audit events")),
    ("fund_entries", _("Fund entries")),
    ("documents", _("Documents")),
    ("outbox", _("Evidence outbox")),
)


def neutralize_cell(value) -> str:
    """Neutralize spreadsheet-formula prefixes in text cells; never emit raw secrets."""
    if value is None:
        return ""
    text = str(value)
    if text and text[0] in FORMULA_PREFIXES:
        return "'" + text
    return text


class _Echo:
    def write(self, value):
        return value


def _csv_stream(header: list[str], rows):
    pseudo = _Echo()
    writer = csv.writer(pseudo)
    yield writer.writerow([neutralize_cell(c) for c in header])
    for row in rows:
        yield writer.writerow([neutralize_cell(c) for c in row])


def _kind_counts(building_id: int) -> dict[str, int]:
    return {
        "audit_events": AuditEvent.objects.filter(membership__building_id=building_id).count(),
        "fund_entries": MaintenanceFundEntry.objects.filter(fund__building_id=building_id).count(),
        "documents": DocumentVersion.objects.filter(document__building_id=building_id).count(),
        "outbox": BlockchainOutboxEvent.objects.filter(building_id=building_id).count(),
    }


@login_required
@require_GET
def export_home(request):
    """Chooser page for the four auditor CSV exports."""
    membership, memberships = require_management_context(request)
    counts = _kind_counts(membership.building_id)
    kinds = [
        {"key": key, "label": label, "count": counts.get(key, 0)}
        for key, label in EXPORT_KINDS
    ]
    return render(
        request,
        "web/staff/exports.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="ops",
            ops_active="exports",
            export_kinds=kinds,
        ),
    )


@login_required
@require_GET
def audit_export(request):
    """Stream fixed-column CSV covering audit/finance/evidence surfaces for auditors."""
    membership, _ = require_management_context(request)

    building_id = membership.building_id
    kind = (request.GET.get("kind") or "audit_events").strip()
    if kind not in {k for k, _ in EXPORT_KINDS} and kind != "observations":
        kind = "audit_events"

    try:
        if kind == "fund_entries":
            header, rows = _fund_entry_rows(building_id)
        elif kind == "documents":
            header, rows = _document_rows(building_id)
        elif kind == "outbox":
            header, rows = _outbox_rows(building_id)
        elif kind == "observations":
            header, rows = _observation_rows(building_id)
        else:
            kind = "audit_events"
            header, rows = _audit_event_rows(building_id)

        record_audit(
            request.user,
            membership,
            "audit.export",
            "Export",
            kind,
            "accepted",
            {"kind": kind},
        )
    except Exception as error:
        try:
            record_audit(
                request.user,
                membership,
                "audit.export",
                "Export",
                kind,
                "denied",
                {"reason": type(error).__name__},
            )
        except Exception:
            pass
        raise

    filename = f"lamto-{kind}-{datetime.now(dt_timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.csv"
    response = StreamingHttpResponse(
        _csv_stream(header, rows),
        content_type="text/csv; charset=utf-8",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response["X-Content-Type-Options"] = "nosniff"
    return response


def _audit_event_rows(building_id):
    header = [
        "id",
        "created_at",
        "actor_id",
        "membership_id",
        "action",
        "target_type",
        "target_id",
        "result",
    ]
    qs = (
        AuditEvent.objects.filter(membership__building_id=building_id)
        .order_by("id")
        .values_list(
            "id",
            "created_at",
            "actor_id",
            "membership_id",
            "action",
            "target_type",
            "target_id",
            "result",
        )
        .iterator(chunk_size=500)
    )
    return header, qs


def _fund_entry_rows(building_id):
    header = [
        "id",
        "entry_type",
        "amount_vnd",
        "evidence_hash",
        "recorder_membership_id",
        "source_key",
        "recorded_at",
    ]
    # Never include bank account numbers or private keys.
    rows = []
    for entry in (
        MaintenanceFundEntry.objects.filter(fund__building_id=building_id)
        .select_related("recorder")
        .order_by("id")
        .iterator(chunk_size=200)
    ):
        rows.append(
            [
                entry.id,
                entry.entry_type,
                entry.amount_vnd,
                entry.evidence_hash,
                entry.recorder_id,
                entry.source_key,
                entry.recorded_at.isoformat() if entry.recorded_at else "",
            ]
        )
    return header, rows



def _document_rows(building_id):
    header = [
        "id",
        "document_id",
        "version",
        "filename",
        "content_type",
        "byte_size",
        "sha256",
        "scan_status",
        "uploader_id",
        "created_at",
    ]
    # Hashes only — never raw file bytes.
    qs = (
        DocumentVersion.objects.filter(document__building_id=building_id)
        .order_by("id")
        .values_list(
            "id",
            "document_id",
            "version",
            "filename",
            "content_type",
            "byte_size",
            "sha256",
            "scan_status",
            "uploader_id",
            "created_at",
        )
        .iterator(chunk_size=500)
    )
    return header, qs


def _outbox_rows(building_id):
    header = [
        "id",
        "event_id",
        "event_type",
        "payload_hash",
        "status",
        "evidence_level",
        "transaction_hash",
        "chain_confirmed_block",
        "signer_address",
        "created_at",
        "confirmed_at",
    ]
    rows = []
    for event in (
        BlockchainOutboxEvent.objects.filter(building_id=building_id)
        .order_by("id")
        .iterator(chunk_size=200)
    ):
        rows.append(
            [
                event.id,
                event.event_id,
                event.event_type,
                event.payload_hash,
                event.status,
                event.evidence_level,
                event.transaction_hash,
                event.chain_confirmed_block,
                event.signer_address,
                event.created_at.isoformat() if event.created_at else "",
                event.confirmed_at.isoformat() if event.confirmed_at else "",
            ]
        )
    return header, rows


def _observation_rows(building_id):
    header = [
        "id",
        "published_entry_id",
        "result",
        "details",
        "observed_at",
    ]
    rows = []
    for obs in (
        VerificationObservation.objects.filter(
            published_entry__proposal__building_id=building_id
        )
        .order_by("id")
        .iterator(chunk_size=200)
    ):
        details = getattr(obs, "details", None) or getattr(obs, "notes", "") or ""
        if isinstance(details, dict):
            details = str(details)
        rows.append(
            [
                obs.id,
                obs.published_entry_id,
                obs.result,
                details,
                obs.observed_at.isoformat() if obs.observed_at else "",
            ]
        )
    return header, rows
