"""Management workspace: triage, cases, proposals."""

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import Truncator
from django.views.decorators.http import require_GET, require_http_methods
from django.utils.translation import gettext as _

from lamto.audit.services import record_audit
from lamto.documents.models import Document
from lamto.finance.proposals import spending_proposal_cases
from lamto.maintenance.ai import URGENCIES
from lamto.maintenance.models import IssueReport, MaintenanceCase, TriageSuggestion
from lamto.maintenance.cases import (
    TERMINAL_STATUSES, complete_case_work, decline_report, publish_progress,
    request_information, start_case_work,
)
from lamto.web.forms.staff import (
    ConfirmTriageForm,
    DeclineReportForm,
    InfoRequestForm,
    ProgressUpdateForm,
)
from lamto.web.staff import require_management_context, staff_context
from lamto.web.staff_documents import _delete_storage_blob, upload_document
from lamto.web.views.staff_common import (
    accountability_chain_for,
    deadline_tone,
    prepare_record_list,
)


def _triage_initial_from_suggestion(suggestion):
    """Prefill the four text/choice fields from the AI suggestion.

    ``location`` is a BuildingLocation FK and the suggestion only carries
    interpreted text, so it is left for the manager to pick.
    """
    if suggestion is None:
        return None
    return {
        "category": suggestion.category,
        "urgency": suggestion.urgency,
        "department": suggestion.department,
        "deadline_minutes": suggestion.deadline_minutes,
    }


@login_required
@require_GET
def case_list(request):
    membership, memberships = require_management_context(request)
    building_id = membership.building_id
    status = request.GET.get("status") or ""
    urgency_groups = {"routine": ("LOW", "MEDIUM"), "urgent": ("HIGH",)}
    valid_status = status in URGENCIES
    active_group = status if status in urgency_groups else next(
        (group for group, values in urgency_groups.items() if status in values), ""
    )

    report_qs = IssueReport.objects.filter(
        unit__building_id=building_id,
        status__in=[
            IssueReport.Status.SUBMITTED,
            IssueReport.Status.IN_REVIEW,
            IssueReport.Status.NEEDS_INFO,
        ],
    )
    if status in urgency_groups:
        report_qs = report_qs.filter(triage_job__suggestion__urgency__in=urgency_groups[status])
    elif valid_status:
        report_qs = report_qs.filter(triage_job__suggestion__urgency=status)
    report_list = prepare_record_list(
        request,
        report_qs,
        search_fields=("text", "location_path_snapshot"),
        sorts=(("", _("Newest first"), ("-created_at",)),),
        page_param="rpage",
    )
    cases_qs = (
        MaintenanceCase.objects.filter(building_id=building_id, active=True)
        .select_related("location")
        .annotate(work_count=Count("updates"))
    )
    if status in urgency_groups:
        cases_qs = cases_qs.filter(urgency__in=urgency_groups[status])
    elif valid_status:
        cases_qs = cases_qs.filter(urgency=status)
    case_list = prepare_record_list(
        request,
        cases_qs,
        search_fields=("category", "department", "location__name"),
        sorts=(
            ("", _("Newest first"), ("-created_at",)),
            ("deadline", _("Deadline soonest"), ("deadline_at",)),
        ),
    )
    urgency_labels = {
        "LOW": _("Low"),
        "MEDIUM": _("Medium"),
        "HIGH": _("High"),
    }

    report_items = [
        {
            "url": f"/s/reports/{r.pk}/",
            "title": Truncator(r.text).chars(120),
            "status": r.get_status_display(),
            "deadline": None,
            "deadline_tone": "neutral",
            "next_action": _("Confirm triage"),
        }
        for r in report_list["page"].object_list
    ]
    case_items = [
        {
            "url": f"/s/cases/{c.pk}/",
            "title": _("Case #%(id)s · %(category)s · %(location)s")
            % {"id": c.pk, "category": c.get_category_display(), "location": c.location.name},
            "status": urgency_labels.get(c.urgency, c.urgency),
            "deadline": c.deadline_at,
            "deadline_tone": deadline_tone(c.deadline_at),
            "next_action": (
                _("Start work") if c.work_count == 0 else _("Follow work in progress")
            ),
        }
        for c in case_list["page"].object_list
    ]
    filters = [
        {"label": label, "value": value, "active": value == active_group}
        for value, label in (("routine", _("Routine")), ("urgent", _("Urgent")))
    ]
    return render(
        request,
        "web/staff/case_detail.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="cases",
            list_mode=True,
            report_items=report_items,
            report_list=report_list,
            case_items=case_items,
            case_list=case_list,
            search_label=_("Search reports and cases"),
            filters=filters,
            filters_active=valid_status or status in urgency_groups,
            filter_param="status",
        ),
    )


@login_required
@require_http_methods(["GET", "POST"])
def report_detail(request, pk):
    """Staff triage surface for IssueReport pk only (not MaintenanceCase)."""
    membership, memberships = require_management_context(request)
    building_id = membership.building_id
    report = get_object_or_404(IssueReport, pk=pk, unit__building_id=building_id)

    link = report.case_reports.filter(case__active=True).select_related("case").first()
    if link is not None:
        return redirect("web:case-detail", pk=link.case_id)

    suggestion = TriageSuggestion.objects.filter(job__report=report).first()
    action = request.POST.get("action") if request.method == "POST" else None
    form = ConfirmTriageForm(
        request.POST if action == "confirm_triage" else None,
        building_id=building_id,
        initial=_triage_initial_from_suggestion(suggestion),
        extra_deadline_minutes=suggestion.deadline_minutes if suggestion else None,
    )
    info_form = InfoRequestForm(request.POST if action == "request_info" else None)
    decline_form = DeclineReportForm(request.POST if action == "decline" else None)
    if request.method == "POST":
        if action == "confirm_triage":
            require_management_context(request)
            if form.is_valid():
                try:
                    case = form.save(report, request.user)
                except (ValidationError, PermissionDenied) as error:
                    if isinstance(error, ValidationError):
                        form.add_error(None, error)
                    else:
                        raise
                else:
                    record_audit(
                        request.user,
                        membership,
                        "workspace.triage.confirm",
                        "MaintenanceCase",
                        str(case.pk),
                        "accepted",
                    )
                    messages.success(
                        request,
                        _("Triage confirmed. Start work to assign the repair."),
                    )
                    return redirect("web:case-detail", pk=case.pk)
        elif action == "request_info" and info_form.is_valid():
            try:
                request_information(report, request.user, info_form.cleaned_data["message"])
            except ValidationError as error:
                messages.error(request, _("Information request was not sent. %(detail)s The report was not changed — review the message and try again.") % {"detail": "; ".join(error.messages)})
            else:
                messages.success(request, _("Information requested."))
            return redirect("web:staff-report-detail", pk=report.pk)
        elif action == "decline" and decline_form.is_valid():
            try:
                decline_report(report, request.user, decline_form.cleaned_data["reason"])
            except ValidationError as error:
                messages.error(request, _("Request was not declined. %(detail)s The report was not changed — review the reason and try again.") % {"detail": "; ".join(error.messages)})
            else:
                messages.success(request, _("Request declined."))
            return redirect("web:staff-report-detail", pk=report.pk)

    return render(
        request,
        "web/staff/case_detail.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="cases",
            report=report,
            case=None,
            form=form,
            work_form=None,
            legacy_items=[],
            list_mode=False,
            mode="report",
            info_form=info_form,
            decline_form=decline_form,
            terminal=report.status in TERMINAL_STATUSES,
            open_info_request=report.info_requests.filter(resolved_at__isnull=True).first(),
            report_photos=report.photos.select_related("version").all(),
            suggestion=suggestion,
            suggestion_raw_json=(
                json.dumps(suggestion.raw_response, indent=2, ensure_ascii=False)
                if suggestion else None
            ),
            accountability_stages=accountability_chain_for(report),
        ),
    )


@login_required
@require_http_methods(["GET", "POST"])
def case_detail(request, pk):
    """MaintenanceCase pk only (not IssueReport)."""
    membership, memberships = require_management_context(request)
    building_id = membership.building_id
    case = get_object_or_404(MaintenanceCase, pk=pk, building_id=building_id)
    report = case.reports.order_by("pk").first()

    work_form = None
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "start_work":
            try:
                start_case_work(case, request.user)
            except (ValidationError, PermissionDenied) as error:
                messages.error(request, _("Work was not started. %(detail)s The case was not changed — try again.") % {"detail": "; ".join(getattr(error, "messages", [str(error)]))})
            else:
                messages.success(request, _("Case work started."))
            return redirect("web:case-detail", pk=case.pk)
        if action in {"publish_progress", "complete_work"}:
            work_form = ProgressUpdateForm(request.POST, request.FILES, building_id=building_id, uploader_id=request.user.pk)
            if work_form.is_valid():
                uploaded = []
                try:
                    with transaction.atomic():
                        before = list(work_form.cleaned_data["before_versions"])
                        after = list(work_form.cleaned_data["after_versions"])
                        if work_form.cleaned_data.get("before_upload"):
                            uploaded.append(upload_document(case.building, Document.Kind.BEFORE_PHOTO, request.user, work_form.cleaned_data["before_upload"]))
                            before.extend(uploaded[-1:])
                        if work_form.cleaned_data.get("after_upload"):
                            uploaded.append(upload_document(case.building, Document.Kind.AFTER_PHOTO, request.user, work_form.cleaned_data["after_upload"]))
                            after.extend(uploaded[-1:])
                        service = complete_case_work if action == "complete_work" else publish_progress
                        service(case, request.user, work_form.cleaned_data["cause"],
                                work_form.cleaned_data["result"], before, after)
                except (ValidationError, PermissionDenied) as error:
                    for version in uploaded:
                        _delete_storage_blob(version.storage_key, version.provider_version_id or "")
                    if isinstance(error, ValidationError):
                        work_form.add_error(None, error)
                    else:
                        raise
                else:
                    messages.success(
                        request,
                        _("Case work completed.") if action == "complete_work" else _("Progress published."),
                    )
                    return redirect("web:case-detail", pk=case.pk)

    if work_form is None:
        work_form = ProgressUpdateForm(building_id=building_id, uploader_id=request.user.pk)

    return render(
        request,
        "web/staff/case_detail.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="cases",
            report=report,
            case=case,
            form=None,
            work_form=work_form,
            legacy_items=[],
            updates=case.updates.prefetch_related("evidence_links__version").order_by("-created_at"),
            ratings=case.completion_ratings.select_related("resident").order_by("created_at"),
            report_photos=(
                report.photos.select_related("version").all() if report is not None else []
            ),
            can_create_proposal=(
                not hasattr(case, "proposal")
                and spending_proposal_cases().filter(pk=case.pk).exists()
            ),
            list_mode=False,
            mode="case",
            accountability_stages=accountability_chain_for(case),
        ),
    )
