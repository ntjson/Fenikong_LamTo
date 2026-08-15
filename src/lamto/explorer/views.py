"""Public Evidence explorer routes (ADR 0004).

The explorer namespace lives outside the Management workspace and resident API
auth boundaries: it is unauthenticated, and its identity is the opaque
``Proposal.public_token`` minted at first publication.
"""

import logging

from django.http import Http404, HttpResponse
from django.views.decorators.http import require_GET

from lamto.api.downloads import content_disposition_inline
from lamto.documents.access import DocumentIntegrityError, read_version_bytes
from lamto.finance.models import Proposal

logger = logging.getLogger(__name__)


@require_GET
def document_download(request, public_token, sha256):
    """Serve one transfer-proof document, content-addressed by its SHA-256.

    The URL is part of the proof: the served bytes must re-verify against the
    anchored hash, or nothing is served. Unknown tokens and unknown hashes are
    indistinguishable — both are plain not-found. Tamper detection is a
    first-class error, never a silent serving (409, matching the staff
    document route).
    """
    proposal = (
        Proposal.objects.select_related("settlement__transfer")
        .filter(public_token=public_token)
        .first()
    )
    if proposal is None:
        raise Http404("Document not found.")
    settlement = getattr(proposal, "settlement", None)
    if settlement is None:
        raise Http404("Document not found.")
    transfer = settlement.transfer
    if sha256 != transfer.sha256:
        raise Http404("Document not found.")
    try:
        data = read_version_bytes(transfer)
    except DocumentIntegrityError as error:
        logger.warning("Explorer document refused: %s", error)
        return HttpResponse(
            str(error), content_type="text/plain; charset=utf-8", status=409
        )
    response = HttpResponse(
        data,
        content_type=transfer.content_type or "application/octet-stream",
    )
    response["Cache-Control"] = "no-store"
    response["Content-Disposition"] = content_disposition_inline(transfer.filename)
    return response
