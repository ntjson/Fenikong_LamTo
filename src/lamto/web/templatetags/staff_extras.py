"""Staff template filters and tags."""

from __future__ import annotations

from django import template
from django.utils import formats, timezone
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy

register = template.Library()

URGENCY_LABELS = {"LOW": _lazy("Low"), "MEDIUM": _lazy("Medium"), "HIGH": _lazy("High")}

# Stored QuarantinedUpload.reason codes stay stable English; screens translate.
UPLOAD_REASON_LABELS = {
    "unsupported content type": _lazy("the file type is not supported"),
    "upload exceeds size limit": _lazy("the file exceeds the size limit"),
    "file signature does not match content type": _lazy("the file content does not match its declared type"),
    "image verification failed": _lazy("the image could not be verified"),
    "scanner unavailable": _lazy("the virus scanner was unavailable"),
    "malware detected": _lazy("the scan detected malware"),
}


def upload_reason_label(value):
    """Translated label for a stored upload-rejection reason; unknown text passes through."""
    return UPLOAD_REASON_LABELS.get(str(value or "").strip(), value)


@register.filter
def staff_upload_reason(value):
    return upload_reason_label(value)


@register.filter
def staff_urgency(value):
    """Translated label for a stored urgency code; unknown codes pass through."""
    return URGENCY_LABELS.get(str(value or "").upper(), value)


@register.filter
def staff_category(value):
    """Translated label for a stored case category code; unknown codes pass through."""
    from lamto.maintenance.models import CaseCategory

    try:
        return CaseCategory(str(value)).label
    except ValueError:
        return value


@register.filter
def describe_errors(bound_field):
    """Widget with aria-describedby/aria-invalid wired to its error block."""
    if not getattr(bound_field, "errors", None):
        return bound_field
    return bound_field.as_widget(attrs={
        "aria-describedby": f"{bound_field.auto_id}-error",
        "aria-invalid": "true",
    })


@register.filter(expects_localtime=True)
def staff_datetime(value):
    """One shared staff datetime format (locale-aware SHORT_DATETIME_FORMAT)."""
    if value in (None, ""):
        return ""
    if isinstance(value, str):
        from django.utils.dateparse import parse_datetime

        parsed = parse_datetime(value)
        if parsed is None:
            return value
        value = parsed
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    return formats.date_format(value, "SHORT_DATETIME_FORMAT")


@register.simple_tag
def staff_entry_count(count):
    """Translatable entry/entries label (replaces entr|y,ies pluralize)."""
    try:
        n = int(count)
    except (TypeError, ValueError):
        n = 0
    return _("%(count)d entry") % {"count": n} if n == 1 else _("%(count)d entries") % {"count": n}


@register.simple_tag
def staff_result_count(count):
    try:
        n = int(count)
    except (TypeError, ValueError):
        n = 0
    return _("%(count)d result") % {"count": n} if n == 1 else _("%(count)d results") % {"count": n}


@register.simple_tag
def staff_task_count(count):
    try:
        n = int(count)
    except (TypeError, ValueError):
        n = 0
    return _("%(count)d open task") % {"count": n} if n == 1 else _("%(count)d open tasks") % {"count": n}
