from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST
from django.utils.translation import gettext as _

from lamto.accounts.models import RegistrationRequest
from lamto.accounts.registration import (
    RegistrationConflict,
    approve_registration,
    reject_registration,
)
from django.utils.translation import gettext_lazy as _lazy

from lamto.web.staff import require_management_context, staff_context
from lamto.web.views.staff_common import prepare_record_list


def _detail_response(request, membership, memberships, registration):
    return render(
        request,
        "web/staff/registrations/detail.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="registrations",
            building_active="registrations",
            registration=registration,
        ),
    )


@login_required
@require_GET
def registration_list(request):
    membership, memberships = require_management_context(request)
    qs = RegistrationRequest.objects.filter(
        building_id=membership.building_id,
        status=RegistrationRequest.Status.PENDING,
    ).select_related("unit", "building")
    list_meta = prepare_record_list(
        request,
        qs,
        search_fields=("full_name", "phone", "email", "unit__label"),
        sorts=(
            ("", _lazy("Oldest first"), ("created_at", "pk")),
            ("newest", _lazy("Newest first"), ("-created_at", "-pk")),
        ),
    )
    return render(
        request,
        "web/staff/registrations/list.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="registrations",
            building_active="registrations",
            registrations=list_meta["page"].object_list,
            list_meta=list_meta,
        ),
    )


@login_required
@require_GET
def registration_detail(request, request_id):
    membership, memberships = require_management_context(request)
    registration = get_object_or_404(
        RegistrationRequest.objects.filter(
            building_id=membership.building_id
        ).select_related("building", "unit"),
        pk=request_id,
    )
    return _detail_response(request, membership, memberships, registration)


@login_required
@require_POST
def registration_approve(request, request_id):
    membership, _memberships = require_management_context(request)
    get_object_or_404(
        RegistrationRequest,
        pk=request_id,
        building_id=membership.building_id,
    )
    try:
        approve_registration(request_id=request_id, actor=request.user)
    except RegistrationConflict:
        messages.error(request, _("This registration has already been decided."))
        return redirect("web:staff-registration-detail", request_id)
    messages.success(request, _("Registration approved."))
    return redirect("web:staff-registration-list")


@login_required
@require_POST
def registration_reject(request, request_id):
    membership, memberships = require_management_context(request)
    registration = get_object_or_404(
        RegistrationRequest.objects.select_related("building", "unit"),
        pk=request_id,
        building_id=membership.building_id,
    )
    reason = request.POST.get("reason", "").strip()
    if not reason:
        messages.error(request, _("Rejection reason is required."))
        return _detail_response(request, membership, memberships, registration)
    try:
        reject_registration(request_id=request_id, actor=request.user, reason=reason)
    except RegistrationConflict:
        messages.error(request, _("This registration has already been decided."))
        return redirect("web:staff-registration-detail", request_id)
    messages.success(request, _("Registration rejected."))
    return redirect("web:staff-registration-list")
