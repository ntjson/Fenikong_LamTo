"""Idempotent blockchain outbox worker."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Protocol

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from eth_utils import to_checksum_address

from .chain import ChainRecord, default_client
from .models import BlockchainOutboxEvent

LEASE_SECONDS = 180

def _json_safe(value):
    if isinstance(value, (bytes, bytearray)):
        return "0x" + bytes(value).hex()
    # AttributeDict and other Mapping-like receipt fields (not always real dict).
    if isinstance(value, dict) or (
        hasattr(value, "items") and not isinstance(value, (str, bytes, bytearray))
    ):
        try:
            items = value.items()
        except Exception:
            return value
        return {str(k): _json_safe(v) for k, v in items}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if hasattr(value, "hex") and not isinstance(value, (str, int, bool, float)):
        try:
            hexed = value.hex()
            if isinstance(hexed, str):
                return hexed if hexed.startswith("0x") else "0x" + hexed
        except Exception:
            pass
    return value


RETRY_BASE_SECONDS = 30
RETRY_MAX_SECONDS = 3600


class ChainClient(Protocol):
    last_receipt: dict | None

    def find(self, event) -> ChainRecord | None: ...

    def submit(self, event) -> str: ...

    def set_signer(self, address, authorized: bool) -> str: ...


def _retry_delay(attempts: int) -> timedelta:
    exponent = max(attempts - 1, 0)
    seconds = min(RETRY_BASE_SECONDS * (2**exponent), RETRY_MAX_SECONDS)
    return timedelta(seconds=seconds)


def anchoring_disabled() -> bool:
    return settings.EVIDENCE_ANCHORING_BACKEND == "disabled"


def _normalize_payload_hash(value: str) -> str:
    text = value.lower()
    return text[2:] if text.startswith("0x") else text


def _record_matches_event(record: ChainRecord, event: BlockchainOutboxEvent) -> bool:
    return (
        _normalize_payload_hash(record.payload_hash)
        == _normalize_payload_hash(event.payload_hash)
        and record.previous_hash.lower() == event.previous_hash.lower()
        and int(record.event_type) == int(event.event_type)
        and to_checksum_address(record.signer)
        == to_checksum_address(event.signer_address)
    )


def _claim_outbox_event(event_pk: int) -> BlockchainOutboxEvent | None:
    """Atomically claim a due outbox row with a short SUBMITTED lease."""
    now = timezone.now()
    with transaction.atomic():
        event = (
            BlockchainOutboxEvent.objects.select_for_update(skip_locked=True, of=("self",))
            .filter(pk=event_pk)
            .filter(
                Q(status=BlockchainOutboxEvent.Status.PENDING)
                & (Q(next_attempt_at__isnull=True) | Q(next_attempt_at__lte=now))
                | Q(
                    status=BlockchainOutboxEvent.Status.SUBMITTED,
                    lease_expires_at__lte=now,
                )
            )
            .first()
        )
        if event is None:
            return None
        event.status = BlockchainOutboxEvent.Status.SUBMITTED
        event.lease_expires_at = now + timedelta(seconds=LEASE_SECONDS)
        event.submitted_at = event.submitted_at or now
        event.last_attempt_at = now
        event.last_error = ""
        event.save(
            update_fields=[
                "status",
                "lease_expires_at",
                "submitted_at",
                "last_attempt_at",
                "last_error",
                "updated_at",
            ]
        )
        return event


def _mark_confirmed(
    event: BlockchainOutboxEvent,
    *,
    transaction_hash: str = "",
    receipt: dict | None = None,
    recorded_at: int | None = None,
) -> BlockchainOutboxEvent:
    now = timezone.now()
    receipt = _json_safe(receipt or {})
    event.status = BlockchainOutboxEvent.Status.CONFIRMED
    event.lease_expires_at = None
    event.confirmed_at = now
    event.last_error = ""
    if transaction_hash:
        event.transaction_hash = transaction_hash
    if receipt:
        event.receipt = receipt
        if "status" in receipt:
            event.receipt_status = int(receipt["status"])
        block_number = receipt.get("blockNumber")
        if block_number is not None:
            event.chain_confirmed_block = int(block_number)
    if recorded_at:
        event.chain_block_timestamp = datetime.fromtimestamp(recorded_at, tz=UTC)
    event.save(
        update_fields=[
            "status",
            "lease_expires_at",
            "confirmed_at",
            "last_error",
            "transaction_hash",
            "receipt",
            "receipt_status",
            "chain_confirmed_block",
            "chain_block_timestamp",
            "updated_at",
        ]
    )
    return event


def _mark_mismatch(event: BlockchainOutboxEvent, record: ChainRecord) -> BlockchainOutboxEvent:
    event.status = BlockchainOutboxEvent.Status.MISMATCH
    event.lease_expires_at = None
    event.last_error = (
        "On-chain record does not match outbox signed identity "
        f"(payload={record.payload_hash}, previous={record.previous_hash}, "
        f"type={record.event_type}, signer={record.signer})."
    )
    event.save(
        update_fields=["status", "lease_expires_at", "last_error", "updated_at"]
    )
    return event


def _mark_retry(event: BlockchainOutboxEvent, error: BaseException) -> BlockchainOutboxEvent:
    now = timezone.now()
    event.attempts = int(event.attempts) + 1
    event.status = BlockchainOutboxEvent.Status.PENDING
    event.lease_expires_at = None
    event.next_attempt_at = now + _retry_delay(event.attempts)
    event.last_attempt_at = now
    event.last_error = str(error)[:2000]
    event.save(
        update_fields=[
            "attempts",
            "status",
            "lease_expires_at",
            "next_attempt_at",
            "last_attempt_at",
            "last_error",
            "updated_at",
        ]
    )
    return event


def _mark_local(event: BlockchainOutboxEvent) -> BlockchainOutboxEvent:
    """Settle without a chain round-trip.

    Honest LOCAL metadata: clear claim/receipt fields so the row cannot look
    chain-submitted or confirmed (no lease, submitted_at, tx hash, or confirmed_at).
    """
    event.status = BlockchainOutboxEvent.Status.LOCAL
    event.lease_expires_at = None
    event.submitted_at = None
    event.transaction_hash = ""
    event.confirmed_at = None
    event.last_error = ""
    event.save(
        update_fields=[
            "status",
            "lease_expires_at",
            "submitted_at",
            "transaction_hash",
            "confirmed_at",
            "last_error",
            "updated_at",
        ]
    )
    return event


def process_outbox_event(event_id, client: ChainClient | None = None) -> BlockchainOutboxEvent:
    """
    Process one outbox row idempotently by stable event primary key.

    Never re-signs or changes payload identity fields. Only delivery status,
    attempts, lease, and receipt metadata are mutated. With anchoring disabled,
    due rows settle immediately as LOCAL and no chain client is constructed.
    """
    existing = (
        BlockchainOutboxEvent.objects
        .filter(pk=event_id)
        .first()
    )
    if existing is None:
        raise BlockchainOutboxEvent.DoesNotExist(
            f"BlockchainOutboxEvent id={event_id} does not exist"
        )
    if existing.status in {
        BlockchainOutboxEvent.Status.CONFIRMED,
        BlockchainOutboxEvent.Status.MISMATCH,
        BlockchainOutboxEvent.Status.LOCAL,
    }:
        # Terminal states: re-check chain for CONFIRMED but never resubmit.
        # LOCAL settled off-chain and is never retro-anchored (spec 5.2).
        if (
            existing.status == BlockchainOutboxEvent.Status.CONFIRMED
            and not anchoring_disabled()
        ):
            client = client or default_client()
            try:
                record = client.find(existing)
            except Exception:
                return existing
            if record is not None and not _record_matches_event(record, existing):
                with transaction.atomic():
                    return _mark_mismatch(existing, record)
        return existing

    claimed = _claim_outbox_event(event_id)
    if claimed is None:
        # Another worker holds the lease, or the row is not due.
        return BlockchainOutboxEvent.objects.get(pk=event_id)

    return _process_claimed_event(claimed, client=client)


def claim_next_due_outbox_event() -> BlockchainOutboxEvent | None:
    """Claim the next due outbox event for batch processing."""
    now = timezone.now()
    with transaction.atomic():
        event = (
            BlockchainOutboxEvent.objects.select_for_update(skip_locked=True, of=("self",))
            .filter(
                Q(status=BlockchainOutboxEvent.Status.PENDING)
                & (Q(next_attempt_at__isnull=True) | Q(next_attempt_at__lte=now))
                | Q(
                    status=BlockchainOutboxEvent.Status.SUBMITTED,
                    lease_expires_at__lte=now,
                )
            )
            .order_by("created_at", "pk")
            .first()
        )
        if event is None:
            return None
        event.status = BlockchainOutboxEvent.Status.SUBMITTED
        event.lease_expires_at = now + timedelta(seconds=LEASE_SECONDS)
        event.submitted_at = event.submitted_at or now
        event.last_attempt_at = now
        event.last_error = ""
        event.save(
            update_fields=[
                "status",
                "lease_expires_at",
                "submitted_at",
                "last_attempt_at",
                "last_error",
                "updated_at",
            ]
        )
        return event


def process_due_outbox_events(
    *, limit: int = 100, client: ChainClient | None = None
) -> list[BlockchainOutboxEvent]:
    if client is None and not anchoring_disabled():
        client = default_client()
    processed: list[BlockchainOutboxEvent] = []
    for _ in range(limit):
        claimed = claim_next_due_outbox_event()
        if claimed is None:
            break
        processed.append(_process_claimed_event(claimed, client=client))
    return processed


def _process_claimed_event(
    claimed: BlockchainOutboxEvent, *, client: ChainClient | None = None
) -> BlockchainOutboxEvent:
    if anchoring_disabled():
        with transaction.atomic():
            event = BlockchainOutboxEvent.objects.select_for_update().get(pk=claimed.pk)
            return _mark_local(event)

    client = client or default_client()
    try:
        record = client.find(claimed)
    except Exception as exc:
        with transaction.atomic():
            event = BlockchainOutboxEvent.objects.select_for_update().get(pk=claimed.pk)
            return _mark_retry(event, exc)

    if record is not None:
        with transaction.atomic():
            event = (
                BlockchainOutboxEvent.objects.select_for_update(of=("self",))
                .get(pk=claimed.pk)
            )
            if _record_matches_event(record, event):
                return _mark_confirmed(
                    event,
                    transaction_hash=event.transaction_hash,
                    recorded_at=record.recorded_at,
                )
            return _mark_mismatch(event, record)

    try:
        tx_hash = client.submit(claimed)
        receipt = getattr(client, "last_receipt", None) or {}
    except Exception as exc:
        with transaction.atomic():
            event = BlockchainOutboxEvent.objects.select_for_update().get(pk=claimed.pk)
            return _mark_retry(event, exc)

    with transaction.atomic():
        event = BlockchainOutboxEvent.objects.select_for_update().get(pk=claimed.pk)
        return _mark_confirmed(event, transaction_hash=tx_hash, receipt=receipt)
