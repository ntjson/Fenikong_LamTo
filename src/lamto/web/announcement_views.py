from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from django.utils.translation import gettext as _

from lamto.notifications.announcements import (
    AnnouncementConflict,
    edit_announcement,
    publish_announcement,
    withdraw_announcement,
)
from lamto.notifications.models import Announcement
from django.utils.translation import gettext_lazy as _lazy

from lamto.web.forms.announcements import AnnouncementForm
from lamto.web.staff import require_management_context, staff_context
from lamto.web.views.staff_common import prepare_record_list


def _announcement_for(membership, announcement_id):
    return get_object_or_404(
        Announcement.objects.select_related("created_by", "updated_by"),
        pk=announcement_id,
        building_id=membership.building_id,
    )


def _render_detail(request, membership, memberships, announcement, form=None):
    return render(
        request,
        "web/staff/announcements/detail.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="announcements",
            announcement=announcement,
            form=form,
        ),
    )


def _announcement_list_context(request, membership, memberships):
    qs = (
        Announcement.objects.filter(building_id=membership.building_id)
        .select_related("created_by", "updated_by")
    )
    list_meta = prepare_record_list(
        request,
        qs,
        search_fields=("title", "body", "state"),
        sorts=(
            ("", _lazy("Newest first"), ("-created_at", "-pk")),
            ("oldest", _lazy("Oldest first"), ("created_at", "pk")),
        ),
    )
    return staff_context(
        request,
        membership,
        memberships,
        nav_active="announcements",
        building_active="announcements",
        announcements=list_meta["page"].object_list,
        list_meta=list_meta,
    )


@login_required
@require_GET
def announcement_list(request):
    membership, memberships = require_management_context(request)
    return render(
        request,
        "web/staff/announcements/list.html",
        _announcement_list_context(request, membership, memberships),
    )


@login_required
@require_http_methods(["GET", "POST"])
def announcement_create(request):
    membership, memberships = require_management_context(request)
    if request.method == "GET":
        form = AnnouncementForm()
    else:
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = publish_announcement(
                request.user,
                membership.building_id,
                form.cleaned_data["title"],
                form.cleaned_data["body"],
            )
            messages.success(request, _("Announcement published."))
            return redirect("web:staff-announcement-detail", announcement.pk)
    return render(
        request,
        "web/staff/announcements/create.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="announcements",
            building_active="announcements",
            form=form,
        ),
    )


@login_required
@require_GET
def announcement_detail(request, announcement_id):
    membership, memberships = require_management_context(request)
    announcement = _announcement_for(membership, announcement_id)
    return _render_detail(request, membership, memberships, announcement)


@login_required
@require_http_methods(["GET", "POST"])
def announcement_edit(request, announcement_id):
    membership, memberships = require_management_context(request)
    announcement = _announcement_for(membership, announcement_id)
    if request.method == "GET":
        form = AnnouncementForm(
            initial={
                "title": announcement.title,
                "body": announcement.body,
                "expected_revision": announcement.revision,
            }
        )
        return _render_detail(request, membership, memberships, announcement, form)

    form = AnnouncementForm(request.POST)
    if not form.is_valid() or form.cleaned_data.get("expected_revision") is None:
        if form.cleaned_data.get("expected_revision") is None:
            form.add_error("expected_revision", _("Revision is required."))
        return _render_detail(request, membership, memberships, announcement, form)
    try:
        edit_announcement(
            request.user,
            announcement.pk,
            expected_revision=form.cleaned_data["expected_revision"],
            title=form.cleaned_data["title"],
            body=form.cleaned_data["body"],
        )
    except AnnouncementConflict:
        messages.error(request, _("This announcement changed since you opened it."))
    else:
        messages.success(request, _("Announcement updated."))
    return redirect("web:staff-announcement-detail", announcement.pk)


@login_required
@require_POST
def announcement_withdraw(request, announcement_id):
    membership, _memberships = require_management_context(request)
    announcement = _announcement_for(membership, announcement_id)
    try:
        expected_revision = int(request.POST.get("expected_revision", ""))
    except ValueError:
        messages.error(request, _("Revision is required."))
        return redirect("web:staff-announcement-detail", announcement.pk)
    try:
        withdraw_announcement(
            request.user,
            announcement.pk,
            expected_revision=expected_revision,
        )
    except AnnouncementConflict:
        messages.error(request, _("This announcement changed since you opened it."))
    else:
        messages.success(request, _("Announcement withdrawn."))
    return redirect("web:staff-announcement-detail", announcement.pk)
