"""Privileged ops health and pilot metrics panels."""

from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Q
from django.db.models.functions import Now
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET

from lamto.accounts.models import BackupMarker
from lamto.audit.services import record_audit
from lamto.documents.models import QuarantinedUpload
from lamto.evidence.models import BlockchainOutboxEvent
from lamto.finance.models import VerificationObservation
from lamto.gate.models import GatePurgeHeartbeat
from lamto.gate.retention import PURGE_STALE_AFTER_HOURS, purge_is_stale
from lamto.maintenance.models import TriageDecision, TriageJob, TriageSuggestion
from django.utils.translation import gettext_lazy as _

from lamto.notifications.models import Device, NotificationDelivery
from lamto.notifications.services import PUSH_SUPPRESSED_PREFIX
from lamto.web.staff import require_management_context, staff_context

# Raw snake_case metric keys stay in the JSON payload; screens read these labels.
PILOT_METRIC_LABELS = {
    "ai_suggestion_accepted": _("AI suggestions accepted as-is"),
    "ai_suggestion_edited": _("AI suggestions edited before confirming"),
    "ai_suggestions_total": _("AI suggestions produced"),
    "duplicate_confirmation_results": _("Suggestions flagging possible duplicates"),
    "triage_latency_ms_avg": _("Average triage latency (ms)"),
    "work_response_time_seconds_avg": _("Average work response time (seconds)"),
    "publication_time_seconds_avg": _("Average publication time (seconds)"),
    "anchoring_delay_seconds_avg": _("Average anchoring delay (seconds)"),
    "anchoring_backend": _("Anchoring backend"),
    "authoritative": _("Authoritative for decisions"),
    "generated_at": _("Generated at"),
}


def collect_health_snapshot(building_id: int) -> dict:
    now = timezone.now()
    outbox = BlockchainOutboxEvent.objects.filter(building_id=building_id)
    pending_outbox = outbox.filter(
        status__in=[
            BlockchainOutboxEvent.Status.PENDING,
            BlockchainOutboxEvent.Status.SUBMITTED,
        ]
    )
    oldest = pending_outbox.order_by("created_at").values_list("created_at", flat=True).first()
    queue_age_seconds = None
    if oldest is not None:
        queue_age_seconds = max(0, int((now - oldest).total_seconds()))

    status_counts = {
        row["status"]: row["c"]
        for row in outbox.values("status").annotate(c=Count("id"))
    }
    last_confirmed = (
        outbox.filter(status=BlockchainOutboxEvent.Status.CONFIRMED)
        .order_by("-confirmed_at")
        .values("chain_confirmed_block", "confirmed_at", "transaction_hash")
        .first()
    )
    latest_backup = BackupMarker.objects.order_by("-signed_at").first()
    mismatches = VerificationObservation.objects.filter(
        published_entry__proposal__building_id=building_id,
        result=VerificationObservation.Result.MISMATCH
    ).count()

    deliveries = NotificationDelivery.objects.filter(building_id=building_id)
    notification_failures = deliveries.filter(
        status__in=[
            NotificationDelivery.Status.FAILED,
            NotificationDelivery.Status.DEAD,
        ]
    ).count()
    push_qs = deliveries.filter(
        channel=NotificationDelivery.Channel.PUSH
    )
    push_failures = push_qs.filter(
        status__in=[
            NotificationDelivery.Status.FAILED,
            NotificationDelivery.Status.DEAD,
        ],
    ).count()
    push_sent_success = push_qs.filter(
        status=NotificationDelivery.Status.SENT, last_error=""
    ).count()
    push_suppressed = push_qs.filter(
        status=NotificationDelivery.Status.SENT,
        last_error__startswith=PUSH_SUPPRESSED_PREFIX,
    ).count()
    devices = Device.objects.filter(
        Q(user__residentoccupancy__unit__building_id=building_id)
        | Q(user__managementmembership__building_id=building_id)
    ).distinct()
    dead_devices = devices.filter(active=False).count()
    # Max whole days since last_seen_at among inactive devices (age signal, not only count).
    oldest_inactive = (
        devices.filter(active=False)
        .order_by("last_seen_at")
        .values_list("last_seen_at", flat=True)
        .first()
    )
    if oldest_inactive is None:
        stale_device_max_inactive_days = 0
    else:
        stale_device_max_inactive_days = max(0, (now - oldest_inactive).days)
    quarantined = QuarantinedUpload.objects.filter(building_id=building_id).count()
    gate_heartbeat = GatePurgeHeartbeat.objects.order_by("-last_success_at").first()

    # A non-empty outbox is normal. Warn only when delivery is aging or failing.
    queue_failed = status_counts.get(
        BlockchainOutboxEvent.Status.FAILED, 0
    ) + status_counts.get(BlockchainOutboxEvent.Status.MISMATCH, 0)
    queue_age_warn_seconds = int(
        getattr(settings, "OPS_QUEUE_AGE_WARN_SECONDS", 300)
    )
    queue_needs_attention = bool(
        queue_failed
        or (
            queue_age_seconds is not None
            and queue_age_seconds >= queue_age_warn_seconds
        )
    )

    return {
        "queue_age_seconds": queue_age_seconds,
        "queue_count": pending_outbox.count(),
        "queue_failed": queue_failed,
        "queue_needs_attention": queue_needs_attention,
        "outbox_status_counts": status_counts,
        "anchoring_backend": settings.EVIDENCE_ANCHORING_BACKEND,
        "quarantined_files": quarantined,
        "notification_failures": notification_failures,
        "push_failures": push_failures,
        "push_sent_success": push_sent_success,
        "push_suppressed": push_suppressed,
        "dead_devices": dead_devices,
        "stale_device_max_inactive_days": stale_device_max_inactive_days,
        "last_confirmed_block": (last_confirmed or {}).get("chain_confirmed_block"),
        "last_confirmed_at": (
            last_confirmed["confirmed_at"].isoformat()
            if last_confirmed and last_confirmed.get("confirmed_at")
            else None
        ),
        # Never include transaction payloads that might hold signatures beyond hash ids.
        "last_confirmed_tx": (last_confirmed or {}).get("transaction_hash") or "",
        "latest_backup_marker": (
            {
                "marker_id": latest_backup.marker_id,
                "signed_at": latest_backup.signed_at.isoformat(),
                "storage_key": latest_backup.storage_key,
            }
            if latest_backup
            else None
        ),
        "integrity_mismatches": mismatches,
        "generated_at": now.isoformat(),
        "gate_purge_last_success_at": (
            gate_heartbeat.last_success_at if gate_heartbeat else None
        ),
        "gate_purge_stale": purge_is_stale(now),
        "gate_purge_stale_after_hours": PURGE_STALE_AFTER_HOURS,
    }


def collect_pilot_metrics(building_id: int) -> dict:
    """Non-authoritative pilot metrics — never used as workflow authority."""
    suggestions_qs = TriageSuggestion.objects.filter(
        job__report__building_id=building_id
    )
    suggestions = suggestions_qs.count()
    decisions = TriageDecision.objects.filter(
        report__building_id=building_id
    ).select_related("suggestion")
    accepted = 0
    edited = 0
    for decision in decisions.iterator(chunk_size=200):
        if decision.suggestion_id is None:
            continue
        # differences empty ⇒ accepted suggestion as-is.
        diffs = decision.differences or {}
        if diffs:
            edited += 1
        else:
            accepted += 1

    duplicate_confirmations = suggestions_qs.exclude(
        duplicate_report_ids=[]
    ).count()

    triage_latency_ms = suggestions_qs.aggregate(avg=Avg("elapsed_ms")).get("avg")

    # Work response time: assignment → first in-progress (proxy: created vs updated status).
    work_response = None
    # Publication time / anchoring delay remain coarse aggregates when timestamps exist.
    anchoring_delay_seconds = None
    confirmed = BlockchainOutboxEvent.objects.filter(
        building_id=building_id,
        status=BlockchainOutboxEvent.Status.CONFIRMED,
        confirmed_at__isnull=False,
    )
    if confirmed.exists():
        # Average created_at → confirmed_at.
        total = 0
        n = 0
        for row in confirmed.values_list("created_at", "confirmed_at").iterator(chunk_size=200):
            if row[0] and row[1]:
                total += (row[1] - row[0]).total_seconds()
                n += 1
        if n:
            anchoring_delay_seconds = total / n

    return {
        "ai_suggestion_accepted": accepted,
        "ai_suggestion_edited": edited,
        "ai_suggestions_total": suggestions,
        "duplicate_confirmation_results": duplicate_confirmations,
        "triage_latency_ms_avg": triage_latency_ms,
        "work_response_time_seconds_avg": work_response,
        "publication_time_seconds_avg": None,
        "anchoring_delay_seconds_avg": anchoring_delay_seconds,
        "anchoring_backend": settings.EVIDENCE_ANCHORING_BACKEND,
        "authoritative": False,
        "generated_at": timezone.now().isoformat(),
    }


@login_required
@require_GET
def ops_health(request):
    membership, memberships = require_management_context(request)
    snapshot = collect_health_snapshot(membership.building_id)
    record_audit(
        request.user,
        membership,
        "ops.health",
        "Health",
        "snapshot",
        "accepted",
        {},
    )
    if request.GET.get("format") == "json":
        return JsonResponse(snapshot)
    return render(
        request,
        "web/staff/ops_health.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="ops",
            ops_active="health",
            health=snapshot,
            panel="health",
        ),
    )


@login_required
@require_GET
def pilot_metrics(request):
    membership, memberships = require_management_context(request)
    metrics = collect_pilot_metrics(membership.building_id)
    record_audit(
        request.user,
        membership,
        "ops.pilot_metrics",
        "Metrics",
        "pilot",
        "accepted",
        {},
    )
    if request.GET.get("format") == "json":
        return JsonResponse(metrics)
    # A latency is not a currency: one decimal on screen, raw values in JSON.
    from django.utils.translation import gettext

    metric_rows = []
    for key, value in metrics.items():
        if isinstance(value, float):
            value = round(value, 1)
        elif isinstance(value, bool):
            value = gettext("Yes") if value else gettext("No")
        elif key == "anchoring_backend" and value == "disabled":
            value = gettext("disabled — records are signed locally")
        metric_rows.append(
            {
                "label": PILOT_METRIC_LABELS.get(key, key),
                "value": value,
                "is_datetime": key == "generated_at",
            }
        )
    return render(
        request,
        "web/staff/ops_metrics.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="ops",
            ops_active="metrics",
            metric_rows=metric_rows,
            panel="metrics",
        ),
    )
