import hashlib

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction

from lamto.accounts.models import ResidentOccupancy, Unit
from lamto.audit.services import record_audit
from lamto.documents.models import Document, DocumentVersion
from lamto.documents.scanner import scan_with_clamav
from lamto.documents.services import create_resident_report_photo

from .models import BuildingLocation, IssueReport, ReportPhoto, TriageJob


class ReportClientRefConflict(Exception):
    """Same (reporter, client_ref) submitted with materially different content (spec 3.5)."""


@transaction.atomic
def submit_report(resident, unit, text, location, photo_versions, client_ref=None, is_private=False) -> IssueReport:
    unit = Unit.objects.select_for_update().select_related("building").filter(
        pk=getattr(unit, "pk", None)
    ).first()
    if unit is None:
        raise ValidationError("Report unit is required.")
    occupancy = ResidentOccupancy.objects.filter(user=resident, unit=unit, active=True).first()
    if occupancy is None:
        raise PermissionDenied("Active occupancy is required to submit a report.")
    if not isinstance(text, str) or not (text := text.strip()):
        raise ValidationError("Report text is required.")
    location = BuildingLocation.objects.select_for_update().select_related("building").filter(
        pk=getattr(location, "pk", None)
    ).first()
    if location is None:
        raise ValidationError("Report location is required.")
    path_location = location
    path_names = []
    seen_locations = set()
    while path_location is not None:
        if (
            path_location.pk in seen_locations
            or not path_location.active
            or path_location.building_id != unit.building_id
        ):
            raise ValidationError("Report location hierarchy must be active and belong to the unit building.")
        seen_locations.add(path_location.pk)
        path_names.append(path_location.name)
        if path_location.parent_id is None:
            break
        path_location = BuildingLocation.objects.select_for_update().filter(
            pk=path_location.parent_id
        ).first()
        if path_location is None:
            raise ValidationError("Report location hierarchy is invalid.")
    location_path_snapshot = " / ".join([location.building.name, *reversed(path_names)])

    photo_versions = list(photo_versions)
    photo_ids = [version.pk for version in photo_versions]
    if len(photo_ids) != len(set(photo_ids)):
        raise ValidationError("A photo version can only be attached once.")
    photo_versions = list(
        DocumentVersion.objects.select_for_update()
        .select_related("document")
        .filter(
            pk__in=photo_ids,
            uploader_id=resident.pk,
            document__building_id=unit.building_id,
            document__kind=Document.Kind.REPORT_PHOTO,
            scan_status=DocumentVersion.ScanStatus.CLEAN,
        )
    )
    if len(photo_versions) != len(photo_ids):
        raise ValidationError("Report photos must be owned, clean original photos in the unit building.")

    report = IssueReport.objects.create(
        reporter=resident,
        unit=unit,
        building=unit.building,
        text=text,
        selected_location=location,
        location_path_snapshot=location_path_snapshot,
        client_ref=client_ref,
        is_private=is_private,
    )
    ReportPhoto.objects.bulk_create(
        [
            ReportPhoto(
                report=report,
                version=version,
                content_sha=version.sha256,
            )
            for version in photo_versions
        ]
    )
    TriageJob.objects.create(report=report)
    record_audit(
        actor=resident,
        membership=None,
        action="report.submit",
        target_type="IssueReport",
        target_id=str(report.pk),
        result="accepted",
        metadata={"occupancy_id": occupancy.pk},
    )
    try:
        from lamto.notifications.hooks import notify_report_receipt

        notify_report_receipt(report)
    except Exception:
        pass
    return report


def _content_matches(existing, text, unit, location, is_private=False) -> bool:
    return (
        existing.text == (text or "").strip()
        and existing.unit_id == getattr(unit, "pk", unit)
        and existing.selected_location_id == getattr(location, "pk", location)
        and existing.is_private == is_private
    )


def submit_report_idempotent(resident, unit, text, location, photo_versions, client_ref, is_private=False):
    """Idempotent POST /reports entry point (spec 3.5). Returns (report, created)."""
    existing = IssueReport.objects.filter(reporter=resident, client_ref=client_ref).first()
    if existing is not None:
        if _content_matches(existing, text, unit, location, is_private):
            return existing, False
        raise ReportClientRefConflict("client_ref reused with different content.")
    try:
        report = submit_report(
            resident, unit, text, location, photo_versions,
            client_ref=client_ref, is_private=is_private,
        )
    except IntegrityError:
        # Concurrent duplicate on the partial unique (reporter, client_ref): re-fetch.
        # Unrelated integrity failures (no matching row) must not masquerade as 409.
        existing = IssueReport.objects.filter(reporter=resident, client_ref=client_ref).first()
        if existing is None:
            raise
        if _content_matches(existing, text, unit, location, is_private):
            return existing, False
        raise ReportClientRefConflict("client_ref reused with different content.")
    return report, True


def _upload_sha256(uploaded_file) -> str:
    """Content digest for photo-upload idempotency (amendment 10). Resets the stream."""
    digest = hashlib.sha256()
    for chunk in uploaded_file.chunks():
        digest.update(chunk)
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)
    return digest.hexdigest()


def attach_report_photo(resident, report, uploaded_file, scanner=None):
    """Upload one report photo through the ClamAV pipeline and link it to the report.

    The caller must own the report (checked by the view). Requires an active
    occupancy in the report's building. Preserves the P1 upload-after-commit rule.

    Returns ``(version, created)``. Same report + identical content SHA-256 is
    idempotent: returns the existing version without a second ReportPhoto row
    (amendment 10 / lost-response retry).
    """
    # Resolve the scanner at call time (not as a default arg) so tests can patch
    # lamto.maintenance.reporting.scan_with_clamav.
    if scanner is None:
        scanner = scan_with_clamav
    occupancy = ResidentOccupancy.objects.filter(
        user=resident, active=True, unit__building_id=report.building_id
    ).first()
    if occupancy is None:
        raise PermissionDenied("Active occupancy in the report building is required.")

    content_sha = _upload_sha256(uploaded_file)
    # Fast path without lock (common sequential retry).
    existing = (
        ReportPhoto.objects.select_related("version")
        .filter(report=report, content_sha=content_sha)
        .first()
    )
    if existing is not None:
        return existing.version, False

    # Lock first, recheck, then create the DocumentVersion so a concurrent
    # loser never creates an orphan version (append-only docs cannot be deleted).
    with transaction.atomic():
        IssueReport.objects.select_for_update().filter(pk=report.pk).get()
        existing = (
            ReportPhoto.objects.select_related("version")
            .filter(report=report, content_sha=content_sha)
            .first()
        )
        if existing is not None:
            return existing.version, False
        # Nested savepoint so IntegrityError recovery does not poison the
        # outer select_for_update transaction (same pattern as device races).
        try:
            with transaction.atomic():
                version = create_resident_report_photo(
                    resident, report.building, uploaded_file, scanner
                )
                ReportPhoto.objects.create(
                    report=report, version=version, content_sha=content_sha
                )
        except IntegrityError:
            existing = (
                ReportPhoto.objects.select_related("version")
                .filter(report=report, content_sha=content_sha)
                .first()
            )
            if existing is not None:
                return existing.version, False
            raise
        return version, True
