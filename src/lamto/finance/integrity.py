import hashlib

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from lamto.audit.services import record_audit
from lamto.documents.access import _read_stored_version
from lamto.evidence.models import BlockchainOutboxEvent, is_settled
from lamto.finance.models import (
    PublishedLedgerEntry,
    VerificationObservation,
)
from lamto.finance.publication import _collect_document_checks, _load_execution_chain


def _stream_sha256(version):
    digest = hashlib.sha256()
    for chunk in _read_stored_version(version):
        digest.update(chunk)
    return digest.hexdigest()


def _related_outbox_events(entry):
    proposal = entry.proposal
    settlement = _load_execution_chain(proposal)
    versions = proposal.versions.select_related("outbox_event").order_by("number")
    return [version.outbox_event for version in versions if version.outbox_event_id] + [
        settlement.outbox_event
    ]


def _check_chain_records(events):
    """Return (chain_ok, chain_unavailable, details).

    Chain-dependent checks are skipped, never faked (spec 5.2): disabled mode
    skips every event; besu mode skips LOCAL-settled events individually.
    """
    if settings.EVIDENCE_ANCHORING_BACKEND == "disabled":
        return None, True, {
            "anchoring_backend": "disabled",
            "chain_checks": [
                {
                    "event_id": event.event_id,
                    "local_status": event.status,
                    "result": "SKIPPED_ANCHORING_DISABLED",
                }
                for event in events
            ],
        }

    details = {"chain_checks": []}
    chain_events = []
    for event in events:
        if event.status == BlockchainOutboxEvent.Status.LOCAL:
            details["chain_checks"].append(
                {
                    "event_id": event.event_id,
                    "local_status": event.status,
                    "result": "SKIPPED_LOCAL",
                }
            )
        else:
            chain_events.append(event)
    if not chain_events:
        return None, True, details

    try:
        from lamto.evidence.chain import EvidenceRegistryClient

        client = EvidenceRegistryClient()
    except Exception as exc:  # pragma: no cover - import/config failure path
        details["chain_error"] = str(exc)
        return None, True, details

    any_unavailable = False
    any_mismatch = False
    for event in chain_events:
        check = {
            "event_id": event.event_id,
            "local_payload_hash": event.payload_hash,
            "local_status": event.status,
        }
        try:
            record = client.find(event)
        except Exception as exc:
            any_unavailable = True
            check["result"] = "UNAVAILABLE"
            check["error"] = str(exc)
            details["chain_checks"].append(check)
            continue
        if record is None:
            if event.status == BlockchainOutboxEvent.Status.CONFIRMED:
                # Local confirmation without on-chain record in test/dev: soft unavailable.
                any_unavailable = True
                check["result"] = "UNAVAILABLE"
                check["error"] = "chain record missing"
            else:
                any_unavailable = True
                check["result"] = "UNAVAILABLE"
            details["chain_checks"].append(check)
            continue
        on_chain = record.payload_hash.removeprefix("0x")
        local = event.payload_hash.removeprefix("0x")
        check["chain_payload_hash"] = on_chain
        if on_chain != local:
            any_mismatch = True
            check["result"] = "MISMATCH"
        else:
            check["result"] = "VERIFIED"
        details["chain_checks"].append(check)

    if any_mismatch:
        return False, False, details
    if any_unavailable:
        return None, True, details
    return True, False, details


def verify_published_entry(entry_id, using="default") -> VerificationObservation:
    """Append a verification observation for a published entry.

    ``using`` selects the Django DB alias for reads and the insert-only
    observation write (restored-DB integrity drills). The filesystem report
    path remains outside this function.
    """
    with transaction.atomic(using=using):
        entry = (
            PublishedLedgerEntry.objects.using(using)
            .select_related(
                "proposal__current_version",
                "proposal__case",
                "settlement__ack_recorded_by__user",
            )
            .filter(pk=entry_id)
            .first()
        )
        if entry is None:
            from django.core.exceptions import ValidationError

            raise ValidationError(_("Published ledger entry does not exist."))

        proposal = entry.proposal
        version = proposal.current_version
        settlement = _load_execution_chain(proposal)
        document_checks = _collect_document_checks(
            proposal, version, settlement, using=using
        )

        checked_hashes = []
        doc_details = []
        doc_result = VerificationObservation.Result.VERIFIED
        for doc_version, expected_hash, gate in document_checks:
            item = {
                "document_version_id": doc_version.pk,
                "gate": gate,
                "expected_hash": expected_hash or doc_version.sha256,
                "stored_sha256": doc_version.sha256,
            }
            try:
                actual = _stream_sha256(doc_version)
            except Exception as exc:
                doc_result = VerificationObservation.Result.UNAVAILABLE
                item["result"] = "UNAVAILABLE"
                item["error"] = str(exc)
                doc_details.append(item)
                continue
            item["actual_hash"] = actual
            checked_hashes.append(actual)
            if actual != doc_version.sha256 or actual != (expected_hash or doc_version.sha256):
                doc_result = VerificationObservation.Result.MISMATCH
                item["result"] = "MISMATCH"
            else:
                item["result"] = "VERIFIED"
            doc_details.append(item)

        events = _related_outbox_events(entry)
        chain_event_ids = [event.event_id for event in events]
        chain_ok, chain_unavailable, chain_details = _check_chain_records(events)

        if doc_result == VerificationObservation.Result.MISMATCH:
            result = VerificationObservation.Result.MISMATCH
        elif doc_result == VerificationObservation.Result.UNAVAILABLE:
            result = VerificationObservation.Result.UNAVAILABLE
        elif chain_ok is False:
            result = VerificationObservation.Result.MISMATCH
        elif chain_unavailable:
            # Documents verified; chain not independently reachable or anchoring
            # skipped. Prefer VERIFIED when every local outbox event is settled.
            if all(is_settled(event.status) for event in events):
                result = VerificationObservation.Result.VERIFIED
            else:
                result = VerificationObservation.Result.UNAVAILABLE
        else:
            result = VerificationObservation.Result.VERIFIED

        details = {
            "documents": doc_details,
            **chain_details,
            "document_result": doc_result,
        }
        observation = VerificationObservation.objects.using(using).create(
            published_entry=entry,
            result=result,
            checked_document_hashes=checked_hashes,
            checked_chain_event_ids=chain_event_ids,
            details=details,
            observed_at=timezone.now(),
        )

        if result == VerificationObservation.Result.MISMATCH:
            publisher = entry.settlement.ack_recorded_by
            record_audit(
                publisher.user,
                publisher,
                "integrity.mismatch",
                "PublishedLedgerEntry",
                str(entry.pk),
                "mismatch",
                {
                    "observation_id": observation.pk,
                    "action_item": "integrity_mismatch",
                    "details": details,
                },
            )
            try:
                from lamto.notifications.hooks import notify_integrity_mismatch

                notify_integrity_mismatch(entry, observation)
            except Exception:
                pass
        return observation
