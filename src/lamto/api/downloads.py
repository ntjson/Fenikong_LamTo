"""Signed resident document downloads (spec 3.6).

Django-hosted, short-TTL signed URLs — never presigned object-store URLs.
The token binds a version to the requesting user; redemption re-checks the
user and re-runs resident_can_download, so a token can never widen access.
"""

from __future__ import annotations

from urllib.parse import quote

from django.core import signing
from django.db.models import Q

from lamto.accounts.tenancy import active_occupancies
from lamto.config.log_filters import DownloadTokenLogFilter, scrub_download_token_in_text
from lamto.documents.models import Document
from lamto.evidence.models import SETTLED_STATUSES
from lamto.finance.models import Proposal, ProposalDocument, PublishedLedgerEntry
from lamto.maintenance.models import ReportPhoto, WorkUpdateEvidence

# Re-export for callers that import scrub helpers from the downloads module.
__all__ = (
    "DOWNLOAD_MAX_AGE",
    "DOWNLOAD_SALT",
    "DownloadTokenLogFilter",
    "content_disposition_inline",
    "issue_download_token",
    "RESIDENT_DOWNLOADABLE_KINDS",
    "resident_can_download",
    "sanitize_download_filename",
    "scrub_download_token_in_text",
)

DOWNLOAD_SALT = "lamto.api.download"
DOWNLOAD_MAX_AGE = 300  # spec 3.6: TTL <= 5 minutes

# Fail-closed outer gate. Every kind absent here is unreachable by residents no
# matter what the reference queries below do, so a bug in one of them cannot
# leak fund contracts, invoices, or completion reports.
RESIDENT_DOWNLOADABLE_KINDS = frozenset(
    {
        Document.Kind.REPORT_PHOTO,
        Document.Kind.BEFORE_PHOTO,
        Document.Kind.AFTER_PHOTO,
        Document.Kind.QUOTATION,
        Document.Kind.PAYMENT_PROOF,
        Document.Kind.RESIDENT_BILL,
    }
)


def sanitize_download_filename(filename: str | None) -> str:
    """Make a stored filename safe for disposition parameters.

    Strips path components, CR/LF, and double-quotes so a hostile or malformed
    stored name cannot break or inject into the response header. Empty results
    fall back to a neutral default.
    """
    if not filename:
        return "download"
    # Drop any directory components (POSIX or Windows separators).
    name = str(filename).replace("\\", "/").rsplit("/", 1)[-1]
    for ch in ("\r", "\n", '"'):
        name = name.replace(ch, "")
    name = name.strip()
    return name or "download"


def _ascii_fallback_filename(name: str) -> str:
    """ASCII-only basename for the legacy ``filename="…"`` parameter."""
    ascii_name = name.encode("ascii", "ignore").decode("ascii")
    # Drop characters that are awkward inside a quoted-string even after sanitize.
    for ch in ("\\", ";"):
        ascii_name = ascii_name.replace(ch, "")
    ascii_name = ascii_name.strip()
    return ascii_name or "download"


def content_disposition_inline(filename: str | None) -> str:
    """Build ``Content-Disposition: inline`` with ASCII fallback + RFC 5987 ``filename*``.

    Both parameters use the same sanitized basename. ``filename`` is ASCII-only
    for older clients; ``filename*=UTF-8''…`` percent-encodes the full Unicode name.
    """
    name = sanitize_download_filename(filename)
    fallback = _ascii_fallback_filename(name)
    # RFC 5987: attr-char unreserved; quote percent-encodes the rest (spaces, non-ASCII).
    starred = quote(name, safe="")
    return f'inline; filename="{fallback}"; filename*=UTF-8\'\'{starred}'


def issue_download_token(user_id: int, version_id: int) -> str:
    """Signed, TTL-bound token binding a document version to one user."""
    return signing.dumps({"v": version_id, "u": user_id}, salt=DOWNLOAD_SALT)


def resident_can_download(user, version) -> bool:
    """True only for the caller's own report photos and the published-ledger
    documents their building has published. Staff-only kinds
    are refused by RESIDENT_DOWNLOADABLE_KINDS before any lookup runs."""
    if version.document.kind not in RESIDENT_DOWNLOADABLE_KINDS:
        return False
    if version.document.kind == Document.Kind.RESIDENT_BILL:
        from lamto.billing.models import Bill

        return (
            Bill.objects.filter(document=version, resident=user)
            .exclude(status=Bill.Status.VOID)
            .exists()
        )
    if version.document.kind == Document.Kind.REPORT_PHOTO:
        return ReportPhoto.objects.filter(version=version, report__reporter=user).exists()
    if version.document.kind in (Document.Kind.BEFORE_PHOTO, Document.Kind.AFTER_PHOTO):
        return WorkUpdateEvidence.objects.filter(
            version=version,
            update__case__case_reports__report__reporter=user,
        ).exists()
    building_ids = list(active_occupancies(user).values_list("unit__building_id", flat=True))
    if not building_ids:
        return False
    if (
        version.document.kind == Document.Kind.QUOTATION
        and ProposalDocument.objects.filter(
            proposal_version__proposal__building_id__in=building_ids,
            proposal_version__proposal__status__in=[
                Proposal.Status.PUBLISHED,
                Proposal.Status.NOT_PROCEEDING,
                Proposal.Status.IN_PROGRESS,
                Proposal.Status.COMPLETED,
                Proposal.Status.CLOSED,
            ],
            document_version=version,
        ).exists()
    ):
        return True
    return (
        PublishedLedgerEntry.objects.filter(
            proposal__building_id__in=building_ids,
            proposal__current_version__outbox_event__status__in=SETTLED_STATUSES,
            settlement__outbox_event__status__in=SETTLED_STATUSES,
        )
        .filter(
            Q(settlement__transfer=version)
            | Q(settlement__ack=version)
        )
        .exists()
    )
