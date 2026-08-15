import hashlib
import os
import tempfile
import uuid
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.files import File
from django.core.files.storage import storages
from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from PIL import Image, UnidentifiedImageError

from lamto.accounts.models import ManagementMembership, ResidentOccupancy
from lamto.accounts.services import require_management
from lamto.audit.services import record_audit
from django.utils.translation import gettext_lazy as _

from .models import Document, DocumentVersion, QuarantinedUpload
from .scanner import DocumentScanUnavailable


class DocumentUploadRejected(ValueError):
    pass


class DocumentUploadQuarantined(ValueError):
    pass


class DocumentStorageError(ValueError):
    pass


MIME_SIGNATURES = {
    "application/pdf": b"%PDF-",
    "image/jpeg": b"\xff\xd8\xff",
    "image/png": b"\x89PNG\r\n\x1a\n",
}
PHOTO_KINDS = {
    Document.Kind.REPORT_PHOTO,
    Document.Kind.BEFORE_PHOTO,
    Document.Kind.AFTER_PHOTO,
}
BILL_KINDS = {Document.Kind.RESIDENT_BILL}


def _membership_for(uploader, building):
    return require_management(uploader, getattr(building, "pk", building))


def _audit(uploader, membership, action, target_id, result, metadata=None):
    record_audit(
        actor=uploader,
        membership=membership,
        action=action,
        target_type="DocumentUpload",
        target_id=str(target_id),
        result=result,
        metadata=metadata,
    )


def _occupancy_for(uploader, building):
    return (
        ResidentOccupancy.objects.select_related("unit")
        .filter(user=uploader, active=True, unit__building_id=getattr(building, "pk", building))
        .first()
    )


def create_resident_report_photo(resident, building, uploaded_file, scanner) -> DocumentVersion:
    """Create a clean original REPORT_PHOTO version for an active resident."""
    document = Document.objects.create(building=building, kind=Document.Kind.REPORT_PHOTO)
    return create_document_version(
        document,
        uploaded_file,
        resident,
        scanner,
        allow_resident_occupancy=True,
    )


def _allowed_content_types(document):
    if document.kind in PHOTO_KINDS:
        return {"image/jpeg", "image/png"}
    if document.kind in BILL_KINDS:
        return {"application/pdf", "image/jpeg", "image/png"}
    return {"application/pdf"}


def _metadata(uploaded_file):
    return {
        "filename": os.path.basename(getattr(uploaded_file, "name", "upload"))[:255],
        "content_type": getattr(uploaded_file, "content_type", "") or "",
        "byte_size": getattr(uploaded_file, "size", 0) or 0,
    }


def _retention_expires_at():
    return timezone.now() + timedelta(days=settings.DOCUMENT_QUARANTINE_RETENTION_DAYS)


def _create_rejection(uploader, membership, metadata, reason, occupancy=None):
    building = None
    if membership is not None:
        building = membership.building
    elif occupancy is not None:
        building = occupancy.unit.building
    rejected = QuarantinedUpload.objects.create(
        uploader=uploader,
        building=building,
        reason=reason,
        storage_key=None,
        provider_version_id="",
        sha256="",
        retention_expires_at=_retention_expires_at(),
        **metadata,
    )
    audit_meta = {"reason": reason}
    if membership is None and occupancy is not None:
        audit_meta["occupancy_id"] = occupancy.pk
        # Occupancy-based rejections use document.upload audit allowance.
        record_audit(
            actor=uploader,
            membership=None,
            action="document.upload",
            target_type="DocumentVersion",
            target_id=str(rejected.pk),
            result="rejected",
            metadata=audit_meta,
        )
    else:
        _audit(uploader, membership, "document.upload_rejected", rejected.pk, "rejected", {"reason": reason})
    raise DocumentUploadRejected(reason)


def _store(storage, storage_key, file_obj, content_type):
    file_obj.seek(0)
    if hasattr(storage, "bucket_name") and hasattr(storage, "connection"):
        client = storage.connection.meta.client
        try:
            versioning = client.get_bucket_versioning(Bucket=storage.bucket_name)
        except Exception as error:
            raise DocumentStorageError(_("Could not verify S3 bucket versioning.")) from error
        if versioning.get("Status") != "Enabled":
            raise DocumentStorageError(_("S3 bucket versioning is not enabled."))
        response = client.put_object(
            Bucket=storage.bucket_name,
            Key=storage_key,
            Body=file_obj,
            ContentType=content_type,
        )
        if not isinstance(version_id := response.get("VersionId"), str) or not version_id or version_id.lower() == "null":
            raise DocumentStorageError(_("S3 did not return an immutable VersionId."))
        return version_id
    saved_key = storage.save(storage_key, File(file_obj, name=storage_key))
    return saved_key


def quarantine_upload(uploaded_file, uploader, reason) -> QuarantinedUpload:
    memberships = list(
        ManagementMembership.objects.select_related("building")
        .filter(user=uploader, active=True)
        .order_by("pk")
    )
    if not memberships:
        raise PermissionDenied("Quarantine upload cannot be audited.")
    building_ids = {m.building_id for m in memberships}
    if len(building_ids) > 1:
        raise PermissionDenied(
            "Ambiguous building for quarantine; active membership must be unique to one building."
        )
    membership = memberships[0]
    metadata = _metadata(uploaded_file)
    digest = hashlib.sha256()
    with tempfile.SpooledTemporaryFile(max_size=settings.DOCUMENT_SPOOL_MAX_BYTES) as temporary:
        for chunk in uploaded_file.chunks():
            digest.update(chunk)
            temporary.write(chunk)
        metadata["byte_size"] = temporary.tell()
        storage_key = f"quarantine/{uuid.uuid4().hex}"
        provider_version_id = _store(storages["private"], storage_key, temporary, metadata["content_type"])
    quarantined = QuarantinedUpload.objects.create(
        uploader=uploader,
        building=membership.building,
        reason=reason,
        storage_key=storage_key,
        provider_version_id=provider_version_id,
        sha256=digest.hexdigest(),
        retention_expires_at=_retention_expires_at(),
        **metadata,
    )
    _audit(
        uploader,
        membership,
        "document.upload_quarantined",
        quarantined.pk,
        "quarantined",
        {"reason": reason},
    )
    try:
        from lamto.notifications.hooks import notify_quarantined_upload

        notify_quarantined_upload(quarantined)
    except Exception:
        pass
    return quarantined


def create_document_version(document, uploaded_file, uploader, scanner, *, allow_resident_occupancy=False) -> DocumentVersion:
    try:
        membership = require_management(uploader, document.building_id)
    except PermissionDenied:
        membership = None
    occupancy = None
    if membership is None:
        if not (
            allow_resident_occupancy
            and document.kind == Document.Kind.REPORT_PHOTO
        ):
            raise PermissionDenied("Document uploader does not belong to this building.")
        occupancy = _occupancy_for(uploader, document.building)
        if occupancy is None:
            raise PermissionDenied("Active occupancy is required to upload report photos.")
    metadata = _metadata(uploaded_file)
    max_bytes = settings.DOCUMENT_MAX_UPLOAD_BYTES
    if metadata["content_type"] not in _allowed_content_types(document):
        _create_rejection(uploader, membership, metadata, "unsupported content type", occupancy=occupancy)
    if metadata["byte_size"] > max_bytes:
        _create_rejection(uploader, membership, metadata, "upload exceeds size limit", occupancy=occupancy)

    digest = hashlib.sha256()
    with tempfile.SpooledTemporaryFile(max_size=settings.DOCUMENT_SPOOL_MAX_BYTES) as temporary:
        for chunk in uploaded_file.chunks():
            digest.update(chunk)
            temporary.write(chunk)
            if temporary.tell() > max_bytes:
                metadata["byte_size"] = temporary.tell()
                _create_rejection(uploader, membership, metadata, "upload exceeds size limit", occupancy=occupancy)
        metadata["byte_size"] = temporary.tell()
        temporary.seek(0)
        signature = temporary.read(8)
        expected_signature = MIME_SIGNATURES[metadata["content_type"]]
        if not signature.startswith(expected_signature):
            _create_rejection(uploader, membership, metadata, "file signature does not match content type", occupancy=occupancy)
        if metadata["content_type"].startswith("image/"):
            try:
                temporary.seek(0)
                with Image.open(temporary) as image:
                    image.verify()
            except (UnidentifiedImageError, OSError, ValueError):
                _create_rejection(uploader, membership, metadata, "image verification failed", occupancy=occupancy)
        temporary.seek(0)
        try:
            clean = scanner(temporary)
        except Exception as error:
            clean = False
            reason = "scanner unavailable"
        else:
            reason = "malware detected"
        if not clean:
            storage_key = f"quarantine/{uuid.uuid4().hex}"
            provider_version_id = _store(
                storages["private"], storage_key, temporary, metadata["content_type"]
            )
            building = None
            if membership is not None:
                building = membership.building
            elif occupancy is not None:
                building = occupancy.unit.building
            quarantined = QuarantinedUpload.objects.create(
                uploader=uploader,
                building=building,
                reason=reason,
                storage_key=storage_key,
                provider_version_id=provider_version_id,
                sha256=digest.hexdigest(),
                retention_expires_at=_retention_expires_at(),
                **metadata,
            )
            if membership is None and occupancy is not None:
                record_audit(
                    actor=uploader,
                    membership=None,
                    action="document.upload",
                    target_type="DocumentVersion",
                    target_id=str(quarantined.pk),
                    result="quarantined",
                    metadata={"occupancy_id": occupancy.pk, "reason": reason},
                )
            else:
                _audit(
                    uploader,
                    membership,
                    "document.upload_quarantined",
                    quarantined.pk,
                    "quarantined",
                    {"reason": reason},
                )
            raise DocumentUploadQuarantined(reason)

        with transaction.atomic():
            locked_document = Document.objects.select_for_update().get(pk=document.pk)
            next_version = (
                DocumentVersion.objects.filter(document=locked_document).aggregate(Max("version"))["version__max"]
                or 0
            ) + 1
            storage_key = f"documents/{locked_document.pk}/{uuid.uuid4().hex}"
            provider_version_id = _store(
                storages["private"], storage_key, temporary, metadata["content_type"]
            )
            version = DocumentVersion.objects.create(
                document=locked_document,
                version=next_version,
                storage_key=storage_key,
                provider_version_id=provider_version_id,
                filename=metadata["filename"],
                content_type=metadata["content_type"],
                byte_size=metadata["byte_size"],
                sha256=digest.hexdigest(),
                uploader=uploader,
            )
    if membership is None and occupancy is not None:
        record_audit(
            actor=uploader,
            membership=None,
            action="document.upload",
            target_type="DocumentVersion",
            target_id=str(version.pk),
            result="allowed",
            metadata={"occupancy_id": occupancy.pk},
        )
    else:
        _audit(uploader, membership, "document.upload", version.pk, "allowed")
    return version


def purge_expired_quarantine(now=None):
    storage = storages["private"]
    expired = QuarantinedUpload.objects.filter(
        storage_key__isnull=False, retention_expires_at__lte=now or timezone.now()
    ).exclude(storage_key="")
    for upload in expired:
        if hasattr(storage, "bucket_name") and hasattr(storage, "connection"):
            version_id = upload.provider_version_id
            if not isinstance(version_id, str) or not version_id or version_id.lower() == "null":
                raise DocumentStorageError(_("S3 quarantine object has no immutable VersionId."))
            storage.connection.meta.client.delete_object(
                Bucket=storage.bucket_name,
                Key=upload.storage_key,
                VersionId=version_id,
            )
        else:
            storage.delete(upload.storage_key)
    return expired.count()
