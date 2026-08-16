"""Shared helpers for staff document uploads and prepared-operation cleanup."""

import logging
import secrets

from django.core.exceptions import ValidationError
from django.core.files.storage import storages
from django.db import connection, transaction

from lamto.documents.models import Document, DocumentVersion
from lamto.documents.scanner import scan_with_clamav
from lamto.documents.services import create_document_version

logger = logging.getLogger(__name__)


def new_event_id() -> str:
    """Server-generated random bytes32 event id (spec 2.2 opacity)."""
    return "0x" + secrets.token_hex(32)


def _delete_storage_blob(storage_key, provider_version_id=""):
    """Best-effort remove a private-storage object written during upload/cleanup."""
    if not storage_key:
        return False
    storage = storages["private"]
    try:
        if hasattr(storage, "bucket_name") and hasattr(storage, "connection"):
            version_id = provider_version_id
            kwargs = {"Bucket": storage.bucket_name, "Key": storage_key}
            if isinstance(version_id, str) and version_id and version_id.lower() != "null":
                kwargs["VersionId"] = version_id
            storage.connection.meta.client.delete_object(**kwargs)
        else:
            storage.delete(storage_key)
        return True
    except Exception:
        logger.exception("Failed to purge storage blob key=%s", storage_key)
        return False


def upload_document(building, kind, uploader, file):
    """Upload one PDF through the ClamAV pipeline.

    Returns a clean DocumentVersion, the exact shape the evidence validators
    require. Storage is not transactional, so blobs already written are
    purged when the transaction rolls back.
    """
    written_blobs = []  # (storage_key, provider_version_id)
    try:
        with transaction.atomic():
            document = Document.objects.create(building=building, kind=kind)
            version = create_document_version(
                document,
                file,
                uploader,
                scan_with_clamav,
            )
            written_blobs.append((version.storage_key, version.provider_version_id or ""))
    except ValueError as error:  # DocumentUploadRejected/Quarantined + identical-bytes all subclass ValueError
        for key, pvid in written_blobs:
            _delete_storage_blob(key, pvid)
        from django.utils.translation import gettext

        from lamto.web.templatetags.staff_extras import upload_reason_label

        raise ValidationError(
            gettext("Evidence upload failed: %(reason)s")
            % {"reason": upload_reason_label(str(error))}
        ) from error
    return version




def _disable_document_append_only_triggers():
    """Allow owner-level maintenance deletes/updates of append-only document rows.

    Document / DocumentVersion have BEFORE UPDATE OR DELETE triggers that reject
    mutation for normal app paths. Cleanup of stale prepared-op orphans is an
    ops maintenance action and must run as the table owner (e.g. lamto_owner).
    Callers must re-enable via `_enable_document_append_only_triggers`.
    """
    with connection.cursor() as cursor:
        # Flush deferred FK checks so ALTER TABLE is allowed mid-transaction.
        cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
        cursor.execute("ALTER TABLE documents_documentversion DISABLE TRIGGER USER")
        cursor.execute("ALTER TABLE documents_document DISABLE TRIGGER USER")


def _enable_document_append_only_triggers():
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE documents_documentversion ENABLE TRIGGER USER")
        cursor.execute("ALTER TABLE documents_document ENABLE TRIGGER USER")


def _hard_delete_document(document_id: int) -> int:
    """Delete a Document and its versions, then purge storage blobs.

    Uses QuerySet.delete() (instance .delete() raises append-only).
    Returns the number of storage blobs successfully purged.
    """
    versions = list(
        DocumentVersion.objects.filter(document_id=document_id).values_list(
            "storage_key", "provider_version_id"
        )
    )
    DocumentVersion.objects.filter(document_id=document_id).delete()
    Document.objects.filter(pk=document_id).delete()
    purged = 0
    for key, pvid in versions:
        if _delete_storage_blob(key, pvid or ""):
            purged += 1
    return purged


def _referenced_document_ids():
    """Document pks whose versions are linked from domain evidence FKs."""
    from lamto.finance.models import (
        MaintenanceFundEntry,
        ProposalDocument,
        Settlement,
    )
    from lamto.maintenance.models import ReportPhoto

    def _docs_from_version_ids(qs_values):
        version_ids = [vid for vid in qs_values if vid is not None]
        if not version_ids:
            return set()
        return set(
            DocumentVersion.objects.filter(pk__in=version_ids).values_list(
                "document_id", flat=True
            )
        )

    protected = set(
        ProposalDocument.objects.values_list("document_version__document_id", flat=True)
    )
    protected |= _docs_from_version_ids(
        MaintenanceFundEntry.objects.exclude(evidence_id=None).values_list(
            "evidence_id", flat=True
        )
    )
    protected |= _docs_from_version_ids(
        Settlement.objects.values_list("transfer_id", flat=True)
    )
    protected |= _docs_from_version_ids(
        ReportPhoto.objects.values_list("version_id", flat=True)
    )
    return protected


def stale_prepared_ops_candidates(*, older_than_hours=24):
    """Return (orphan_document_ids, draft_proposal_count) older than threshold."""
    from datetime import timedelta

    from django.utils import timezone

    from lamto.finance.models import Proposal

    cutoff = timezone.now() - timedelta(hours=older_than_hours)
    protected = _referenced_document_ids()
    stale_docs = (
        Document.objects.exclude(pk__in=protected)
        .filter(versions__created_at__lt=cutoff)
        .distinct()
    )
    orphan_ids = [
        doc.pk
        for doc in stale_docs
        if not doc.versions.filter(created_at__gte=cutoff).exists()
    ]
    draft_count = Proposal.objects.filter(
        current_version__isnull=True,
        created_at__lt=cutoff,
    ).count()
    return orphan_ids, draft_count


def cleanup_stale_prepared_ops(*, older_than_hours=24, dry_run=False):
    """Expire prepared-but-never-signed staff drafts and orphan documents.

    Removes:
    - Document rows whose versions are all older than the threshold and that
      are not referenced by any domain evidence FK (proposal docs, fund,
      settlements, report photos, work-update evidence).
    - Proposal rows still without a current_version older than threshold.

    Also purges private-storage blobs for deleted document versions.

    Does not delete signed/submitted proposal versions, verified fund entries,
    or any outbox-linked evidence. Returns a dict of deletion counts.

    Document tables are DB append-only; this function briefly disables their
    user triggers as table owner inside a single transaction so a crash
    re-enables them on rollback. Run from an owner-role ops job, not the
    restricted web writer role.
    """
    from datetime import timedelta

    from django.utils import timezone

    from lamto.finance.models import Proposal

    orphan_ids, draft_count = stale_prepared_ops_candidates(
        older_than_hours=older_than_hours
    )

    if dry_run:
        return {
            "documents_deleted": 0,
            "proposals_deleted": 0,
            "storage_purged": 0,
            "documents_candidate": len(orphan_ids),
            "proposals_candidate": draft_count,
            "dry_run": True,
        }

    documents_deleted = 0
    storage_purged = 0
    if orphan_ids:
        # ALTER TABLE is transactional in Postgres: wrap disable+delete+enable
        # so a mid-flight crash rolls triggers back to ENABLED.
        with transaction.atomic():
            _disable_document_append_only_triggers()
            try:
                for document_id in orphan_ids:
                    storage_purged += _hard_delete_document(document_id)
                    documents_deleted += 1
            finally:
                _enable_document_append_only_triggers()

    cutoff = timezone.now() - timedelta(hours=older_than_hours)
    proposals_deleted, _ = Proposal.objects.filter(
        current_version__isnull=True,
        created_at__lt=cutoff,
    ).delete()

    return {
        "documents_deleted": documents_deleted,
        "proposals_deleted": proposals_deleted,
        "storage_purged": storage_purged,
        "dry_run": False,
    }
