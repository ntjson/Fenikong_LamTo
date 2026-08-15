"""Unified database-backed worker cycle.

Each processor is independently callable/testable. One failed adapter must not
stop the other queues. Connections are released between cycles so replicas can
scale with locks, leases, and idempotency keys.
"""

from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass, field

from django.db import close_old_connections
from django.utils import timezone

logger = logging.getLogger(__name__)


@dataclass
class ProcessorResult:
    name: str
    ok: bool
    detail: str = ""
    count: int = 0


@dataclass
class CycleResult:
    processors: list[ProcessorResult] = field(default_factory=list)

    @property
    def all_ok(self) -> bool:
        return all(p.ok for p in self.processors)


def process_triage_batch(*, limit: int = 20) -> ProcessorResult:
    name = "triage"
    try:
        from lamto.maintenance.ai import _claim_triage_job, _process_claimed_job

        count = 0
        for _ in range(limit):
            job = _claim_triage_job()
            if job is None:
                break
            _process_claimed_job(job)
            count += 1
        return ProcessorResult(name=name, ok=True, count=count, detail=f"processed={count}")
    except Exception as exc:
        logger.exception("worker processor %s failed", name)
        return ProcessorResult(name=name, ok=False, detail=str(exc))


def process_blockchain_outbox_batch(*, limit: int = 50) -> ProcessorResult:
    name = "blockchain_outbox"
    try:
        from lamto.evidence.worker import process_due_outbox_events

        results = process_due_outbox_events(limit=limit)
        return ProcessorResult(
            name=name, ok=True, count=len(results), detail=f"processed={len(results)}"
        )
    except Exception as exc:
        logger.exception("worker processor %s failed", name)
        return ProcessorResult(name=name, ok=False, detail=str(exc))


def process_integrity_batch(*, limit: int = 20) -> ProcessorResult:
    name = "integrity"
    try:
        from lamto.finance.integrity import verify_published_entry
        from lamto.finance.models import PublishedLedgerEntry, VerificationObservation

        # Prefer entries with no observation yet, then older ones.
        observed = VerificationObservation.objects.values_list(
            "published_entry_id", flat=True
        )
        pending = (
            PublishedLedgerEntry.objects.exclude(pk__in=observed)
            .order_by("published_at", "pk")[:limit]
        )
        count = 0
        for entry in pending:
            try:
                verify_published_entry(entry.pk)
                count += 1
            except Exception:
                logger.exception("verify_published_entry failed for %s", entry.pk)
        return ProcessorResult(name=name, ok=True, count=count, detail=f"checked={count}")
    except Exception as exc:
        logger.exception("worker processor %s failed", name)
        return ProcessorResult(name=name, ok=False, detail=str(exc))


def process_deadline_risk_batch(*, limit: int = 50) -> ProcessorResult:
    """Queue deadline-risk notifications for near-due work orders.

    Scans active cases within a 24h horizon and calls ``notify_deadline_risk``.
    """
    name = "deadline_risk"
    try:
        from datetime import timedelta

        from django.utils import timezone

        from lamto.maintenance.models import MaintenanceCase
        from lamto.notifications.hooks import notify_deadline_risk

        now = timezone.now()
        horizon = now + timedelta(hours=24)
        # Include slightly overdue items still open (missed deadline awareness).
        floor = now - timedelta(hours=24)
        qs = (
            MaintenanceCase.objects.filter(
                deadline_at__lte=horizon,
                deadline_at__gte=floor,
                active=True,
                completed_at__isnull=True,
            )
            .order_by("deadline_at", "pk")[:limit]
        )
        count = 0
        for case in qs:
            try:
                notify_deadline_risk(case)
                count += 1
            except Exception:
                logger.exception(
                    "notify_deadline_risk failed for case %s", case.pk
                )
        return ProcessorResult(
            name=name, ok=True, count=count, detail=f"queued={count}"
        )
    except Exception as exc:
        logger.exception("worker processor %s failed", name)
        return ProcessorResult(name=name, ok=False, detail=str(exc))


def process_notifications_batch(*, limit: int = 50) -> ProcessorResult:
    name = "notifications"
    try:
        from lamto.notifications.services import process_due_notifications

        results = process_due_notifications(limit=limit)
        return ProcessorResult(
            name=name, ok=True, count=len(results), detail=f"processed={len(results)}"
        )
    except Exception as exc:
        logger.exception("worker processor %s failed", name)
        return ProcessorResult(name=name, ok=False, detail=str(exc))


def process_stale_devices_batch(*, days: int = 180) -> ProcessorResult:
    name = "stale_devices"
    try:
        from lamto.notifications.devices import deactivate_stale_devices

        n = deactivate_stale_devices(days=days)
        return ProcessorResult(name=name, ok=True, count=n, detail=f"deactivated={n}")
    except Exception as exc:
        logger.exception("worker processor %s failed", name)
        return ProcessorResult(name=name, ok=False, detail=str(exc))


def process_registration_expiry_batch(*, limit: int = 100) -> ProcessorResult:
    name = "registration_expiry"
    try:
        from lamto.accounts.registration import expire_registration_requests

        count = expire_registration_requests(limit=limit)
        return ProcessorResult(name=name, ok=True, count=count, detail=f"expired={count}")
    except Exception as exc:
        logger.exception("worker processor %s failed", name)
        return ProcessorResult(name=name, ok=False, detail=str(exc))


PROCESSORS = (
    process_triage_batch,
    process_blockchain_outbox_batch,
    process_integrity_batch,
    process_deadline_risk_batch,
    process_notifications_batch,
    process_stale_devices_batch,
    process_registration_expiry_batch,
)


def run_worker_cycle(**kwargs) -> CycleResult:
    """Run one bounded cycle of all processors; isolate failures per adapter."""
    result = CycleResult()
    for processor in PROCESSORS:
        try:
            result.processors.append(processor(**_kwargs_for(processor, kwargs)))
        except Exception as exc:
            logger.exception("worker processor wrapper failed for %s", processor)
            result.processors.append(
                ProcessorResult(
                    name=getattr(processor, "__name__", "?"),
                    ok=False,
                    detail=str(exc),
                )
            )
    return result


def _kwargs_for(processor, kwargs: dict) -> dict:
    # Processors accept optional limit via kwargs when provided.
    name = processor.__name__
    out = {}
    if "limit" in kwargs:
        out["limit"] = kwargs["limit"]
    # Allow per-processor limits
    specific = kwargs.get(f"{name}_limit")
    if specific is not None:
        out["limit"] = specific
    # process_stale_devices_batch takes days, not limit
    if name == "process_stale_devices_batch":
        if "days" in kwargs:
            return {"days": kwargs["days"]}
        return {}
    return out


def run_worker_loop(
    *,
    sleep_seconds: float = 2.0,
    jitter_seconds: float = 1.0,
    max_cycles: int | None = None,
    stop_event=None,
):
    """Long-running loop used by manage.py run_worker."""
    cycles = 0
    while True:
        if stop_event is not None and stop_event.is_set():
            break
        try:
            run_worker_cycle()
        finally:
            close_old_connections()
        cycles += 1
        if max_cycles is not None and cycles >= max_cycles:
            break
        delay = sleep_seconds + random.uniform(0, max(jitter_seconds, 0))
        time.sleep(delay)
