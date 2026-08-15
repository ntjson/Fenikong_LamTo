"""Staff document download — signed short-TTL URL, fail-closed."""

from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.core import signing
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET

from lamto.api.downloads import (
    DOWNLOAD_MAX_AGE,
    content_disposition_inline,
)
from lamto.documents.access import DocumentIntegrityError, authorize_download
from lamto.documents.models import DocumentVersion
from lamto.web.staff import require_management_context, staff_context

STAFF_DOWNLOAD_SALT = "lamto.web.staff_download"


def issue_staff_download_token(user_id: int, version_id: int) -> str:
    return signing.dumps({"v": version_id, "u": user_id}, salt=STAFF_DOWNLOAD_SALT)


def staff_document_url(request, version_id: int) -> str:
    """Issue a short-TTL staff download URL for templates."""
    token = issue_staff_download_token(request.user.pk, version_id)
    return reverse("web:staff-document-download", kwargs={"token": token})


def _integrity_failure(request, membership, memberships, version, error):
    """Tamper detection is a first-class page, never a 404."""
    return render(
        request,
        "web/staff/document_integrity.html",
        staff_context(
            request,
            membership,
            memberships,
            version=version,
            storage_unavailable="unavailable" in str(error),
        ),
        status=409,
    )


@login_required
@require_GET
def staff_document_redirect(request, version_id: int):
    """Authorize then redirect to a signed short-TTL download URL."""
    membership, memberships = require_management_context(request)
    version = get_object_or_404(
        DocumentVersion.objects.select_related("document"), pk=version_id
    )
    try:
        authorize_download(request.user, membership.pk, version)
    except DocumentIntegrityError as error:
        return _integrity_failure(request, membership, memberships, version, error)
    except PermissionDenied as error:
        raise Http404(str(error)) from error
    return redirect(staff_document_url(request, version.pk))


@login_required
@require_GET
def staff_document_download(request, token: str):
    """Redeem a signed staff download token; re-check access on every hit."""
    membership, memberships = require_management_context(request)
    try:
        payload = signing.loads(token, salt=STAFF_DOWNLOAD_SALT, max_age=DOWNLOAD_MAX_AGE)
    except signing.BadSignature as error:
        raise Http404("Document not found.") from error
    if payload.get("u") != request.user.pk:
        raise Http404("Document not found.")
    version = (
        DocumentVersion.objects.select_related("document")
        .filter(pk=payload.get("v"))
        .first()
    )
    if version is None:
        raise Http404("Document not found.")
    try:
        data = authorize_download(request.user, membership.pk, version)
    except DocumentIntegrityError as error:
        return _integrity_failure(request, membership, memberships, version, error)
    except PermissionDenied as error:
        raise Http404(str(error)) from error
    response = HttpResponse(data, content_type=version.content_type or "application/octet-stream")
    response["Cache-Control"] = "private, no-store"
    response["Content-Disposition"] = content_disposition_inline(version.filename)
    return response
