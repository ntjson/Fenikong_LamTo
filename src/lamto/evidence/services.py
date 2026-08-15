import hashlib
import json
import re
from datetime import UTC, datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction

from .canonical import canonical_bytes, payload_hash
from .models import BlockchainOutboxEvent, EvidenceType
from .signatures import (
    BYTES32_RE,
    platform_sign_evidence,
    platform_signer_address,
)


HASH_RE = re.compile(r"(?:0x)?[0-9a-f]{64}\Z")
UTC_RFC3339_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z\Z")
# Closed vocabulary of payload value shapes (spec 2.2 opacity). Free-text shapes
# must not be added — chain hashes remain non-invertible only if payloads stay opaque.
OPAQUE_PAYLOAD_SHAPES = frozenset({
    "id", "positive_int", "money", "bool", "hash", "hashes", "bytes32", "timestamp", "text",
})
HASH_PAYLOAD_SHAPES = frozenset({"hash", "hashes", "bytes32"})
EVIDENCE_PAYLOAD_SCHEMAS = {
    EvidenceType.PROPOSAL_CREATED: ({
        "proposal_id": "id", "proposal_version": "positive_int", "record_id": "id",
        "amount_vnd": "money", "proposal_snapshot_hash": "hash",
        "quotation_hash": "hash",
    }, {"building_id": "id", "case_id": "id", "report_id": "id", "case_snapshot_hash": "hash",
        "report_snapshot_hash": "hash", "estimated_amount_vnd": "money",
        "photo_hash": "hash", "photo_hashes": "hashes"}),
    EvidenceType.SETTLEMENT: ({
        "schema": frozenset({"settlement.v1"}), "settlement_id": "id",
        "proposal_id": "id", "proposal_version": "positive_int", "amount_vnd": "money",
        "payee_name": "text", "bank_reference": "text",
        "transfer_sha256": "hash", "ack_sha256": "hash",
        "transfer_recorded_at": "timestamp", "ack_recorded_at": "timestamp",
    }, {}),
}


class EvidenceConflict(Exception):
    pass


def utc_rfc3339(value: datetime) -> str:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise TypeError("Timestamp must be a timezone-aware datetime.")
    return value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def lowercase_identifier(value) -> str:
    return str(value).lower()


def normalize_vnd(value) -> int:
    if type(value) is not int or value < 0:
        raise ValueError("VND amounts must be non-negative integers.")
    return value


def _platform_write_authorization(*parts) -> str:
    message = "|".join(("platform-evidence-queue", *(str(part) for part in parts)))
    secret = settings.EVIDENCE_WRITE_SECRET.encode()
    inner = hashlib.sha256(secret + message.encode()).digest()
    return hashlib.sha256(secret + inner).hexdigest()


def _validate_payload(event_type, payload):
    if not isinstance(event_type, int) or isinstance(event_type, bool):
        raise ValueError("Evidence event type must be an integer from 1 through 11.")
    if event_type not in (EvidenceType.PROPOSAL_CREATED, EvidenceType.SETTLEMENT):
        raise ValidationError("Only proposal versions and settlements may be anchored.")
    schema = EVIDENCE_PAYLOAD_SCHEMAS.get(event_type)
    if schema is None:
        raise ValueError("Evidence event type must be an integer from 1 through 11.")
    if not isinstance(payload, dict) or any(not isinstance(key, str) for key in payload):
        raise ValidationError("Evidence payload must be an object with known fields.")
    required, optional = schema
    if set(payload) - required.keys() - optional.keys():
        raise ValidationError("Evidence payload contains fields outside its event schema.")
    if missing := required.keys() - payload.keys():
        raise ValidationError(f"Evidence payload is missing required fields: {', '.join(sorted(missing))}.")
    for field, value in payload.items():
        shape = required.get(field, optional.get(field))
        if isinstance(shape, str) and shape not in OPAQUE_PAYLOAD_SHAPES:
            raise ValidationError(
                f"Evidence payload field {field!r} uses non-opaque shape {shape!r}."
            )
        valid = (
            (shape == "id" and type(value) is int and value > 0)
            or (shape == "positive_int" and type(value) is int and value > 0)
            or (shape == "money" and type(value) is int and value >= 0)
            or (shape == "bool" and type(value) is bool)
            or (shape == "text" and isinstance(value, str) and bool(value))
            or (shape == "hash" and isinstance(value, str) and bool(HASH_RE.fullmatch(value)))
            or (shape == "bytes32" and isinstance(value, str) and bool(BYTES32_RE.fullmatch(value)))
            or (
                shape == "hashes" and isinstance(value, list) and bool(value)
                and all(isinstance(item, str) and HASH_RE.fullmatch(item) for item in value)
            )
            or (
                shape == "timestamp" and isinstance(value, str)
                and bool(UTC_RFC3339_RE.fullmatch(value))
                and _is_valid_utc_timestamp(value)
            )
            or (isinstance(shape, frozenset) and type(value) is str and value in shape)
        )
        if not valid:
            raise ValidationError(f"Evidence payload field {field!r} has an invalid value.")


def _is_valid_utc_timestamp(value):
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return False
    return True


@transaction.atomic
def queue_platform_event(
    event_id, event_type, payload, previous_hash, building
) -> BlockchainOutboxEvent:
    event_id = lowercase_identifier(event_id)
    previous_hash = lowercase_identifier(previous_hash)
    _validate_payload(event_type, payload)
    if not BYTES32_RE.fullmatch(event_id) or not BYTES32_RE.fullmatch(previous_hash):
        raise ValidationError("Event ID and previous hash must be 0x-prefixed bytes32 values.")
    normalized_payload = json.loads(canonical_bytes(payload))
    digest = payload_hash(normalized_payload)
    signature = platform_sign_evidence(
        event_id, event_type, "0x" + digest, previous_hash
    )
    signer_address = platform_signer_address()
    canonical_payload = canonical_bytes(normalized_payload).decode("utf-8")
    existing = BlockchainOutboxEvent.objects.filter(event_id=event_id).first()
    identity = {
        "event_type": event_type,
        "payload": normalized_payload,
        "payload_hash": digest,
        "previous_hash": previous_hash,
        "signature": signature,
        "signer_address": signer_address,
    }
    if existing:
        if all(getattr(existing, field) == value for field, value in identity.items()):
            return existing
        raise EvidenceConflict("Event ID already exists with different signed identity.")
    try:
        authorization = _platform_write_authorization(
            event_id, int(event_type), digest, previous_hash, signature,
            signer_address, building.pk, canonical_payload,
        )
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT lamto_security.evidence_insert_platform_outbox_event(
                    %s, %s::smallint, %s::jsonb, %s, %s, %s, %s, %s, %s, %s
                )""",
                [event_id, event_type, canonical_payload, digest, previous_hash,
                 signature, signer_address, building.pk, canonical_payload, authorization],
            )
            event_pk = cursor.fetchone()[0]
        return BlockchainOutboxEvent.objects.get(pk=event_pk)
    except IntegrityError:
        existing = BlockchainOutboxEvent.objects.get(event_id=event_id)
        if all(getattr(existing, field) == value for field, value in identity.items()):
            return existing
        raise EvidenceConflict("Event ID already exists with different signed identity.")
