import hashlib

from django.core.exceptions import PermissionDenied
from django.core.files.storage import storages

from lamto.accounts.models import ManagementMembership, ResidentOccupancy
from lamto.accounts.services import require_management
from lamto.audit.services import record_audit

from .models import DocumentVersion


class DocumentIntegrityError(PermissionDenied):
    pass


def _audit(user, membership, version, result, metadata=None):
    record_audit(
        actor=user,
        membership=membership,
        action="document.download",
        target_type="DocumentVersion",
        target_id=str(version.pk),
        result=result,
        metadata=metadata,
    )


def _resident_occupancy(user, version):
    return ResidentOccupancy.objects.filter(
        user=user, active=True, unit__building_id=version.document.building_id
    ).first()


def _allowed(user, membership, version, occupancy):
    return membership is not None or occupancy is not None


def _read_stored_version(version):
    storage = storages["private"]
    if hasattr(storage, "bucket_name") and hasattr(storage, "connection"):
        if (
            not isinstance(version.provider_version_id, str)
            or not version.provider_version_id
            or version.provider_version_id.lower() == "null"
        ):
            raise ValueError("S3 document version ID is missing.")
        response = storage.connection.meta.client.get_object(
            Bucket=storage.bucket_name,
            Key=version.storage_key,
            VersionId=version.provider_version_id,
        )
        stream = response["Body"]
        return iter(lambda: stream.read(8192), b"")
    return storage.open(version.storage_key, "rb").chunks()


def read_version_bytes(version) -> bytes:
    """Read a stored version and verify its sha256. Raises DocumentIntegrityError.

    Used by the resident API download path after its own authorization; the staff
    ``authorize_download`` keeps its distinct 'unavailable' vs 'integrity_mismatch'
    audit branches and is not routed through this reader.
    """
    try:
        data = b"".join(_read_stored_version(version))
    except Exception as error:
        raise DocumentIntegrityError("Document storage is unavailable.") from error
    if hashlib.sha256(data).hexdigest() != version.sha256:
        raise DocumentIntegrityError("Document integrity check failed.")
    return data


def authorize_download(user, membership_id, version) -> bytes:
    try:
        membership = require_management(user, version.document.building_id)
    except PermissionDenied:
        membership = None
    audit_membership = membership or ManagementMembership.objects.filter(
        user=user, active=True
    ).first()
    occupancy = _resident_occupancy(user, version) if membership is None else None
    if audit_membership is None and occupancy is None:
        occupancy = ResidentOccupancy.objects.filter(user=user, active=True).first()
    audit_metadata = {"occupancy_id": occupancy.id} if occupancy else None
    if not _allowed(user, membership, version, occupancy):
        _audit(user, audit_membership, version, "denied", audit_metadata)
        raise PermissionDenied("Document access denied.")
    try:
        data = b"".join(_read_stored_version(version))
    except Exception as error:
        _audit(
            user,
            audit_membership,
            version,
            "unavailable",
            {"action_item": "document_integrity_check", **(audit_metadata or {})},
        )
        raise DocumentIntegrityError("Document storage is unavailable.") from error
    if hashlib.sha256(data).hexdigest() != version.sha256:
        _audit(
            user,
            audit_membership,
            version,
            "integrity_mismatch",
            {"action_item": "document_integrity_check", **(audit_metadata or {})},
        )
        raise DocumentIntegrityError("Document integrity check failed.")
    _audit(user, audit_membership, version, "allowed", audit_metadata)
    return data
