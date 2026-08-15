from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.utils.translation import gettext as _

from lamto.accounts.models import ResidentOccupancy
from lamto.billing.models import Bill
from lamto.billing.qr import bill_qr_svg
from lamto.billing.services import BillError, issue_bill, void_bill
from lamto.documents.models import Document
from django.utils.translation import gettext_lazy as _lazy

from lamto.web.forms.bills import BillForm, VoidBillForm
from lamto.web.staff import require_management_context, staff_context
from lamto.web.staff_documents import _delete_storage_blob, upload_document
from lamto.web.views.staff_common import prepare_record_list


def _resident_choices(building_id):
    occupancies = (
        ResidentOccupancy.objects.filter(
            active=True, unit__building_id=building_id
        )
        .select_related("user", "unit")
        .order_by("unit__label", "user__display_name")
    )
    seen = set()
    choices = []
    for occupancy in occupancies:
        if occupancy.user_id in seen:
            continue
        seen.add(occupancy.user_id)
        name = occupancy.user.display_name or occupancy.user.email
        choices.append((str(occupancy.user_id), f"{name} · {occupancy.unit.label}"))
    return choices


def _bills_for(building_id):
    return (
        Bill.objects.filter(building_id=building_id)
        .select_related("resident")
        .order_by("-issued_at", "-pk")
    )


def _bill_for(membership, pk):
    return get_object_or_404(
        Bill.objects.select_related("resident", "paid_confirmed_by"),
        pk=pk,
        building_id=membership.building_id,
    )


def _bill_list_context(request, membership, memberships):
    list_meta = prepare_record_list(
        request,
        _bills_for(membership.building_id),
        search_fields=("title", "resident__display_name", "resident__email", "status"),
        sorts=(
            ("", _lazy("Newest first"), ("-issued_at", "-pk")),
            ("oldest", _lazy("Oldest first"), ("issued_at", "pk")),
            ("amount", _lazy("Amount"), ("-amount_vnd", "-pk")),
        ),
    )
    return staff_context(
        request,
        membership,
        memberships,
        nav_active="bills",
        building_active="bills",
        bills=list_meta["page"].object_list,
        list_meta=list_meta,
    )


@login_required
@require_GET
def bill_list(request):
    membership, memberships = require_management_context(request)
    return render(
        request,
        "web/staff/bills/list.html",
        _bill_list_context(request, membership, memberships),
    )


@login_required
@require_http_methods(["GET", "POST"])
def bill_create(request):
    membership, memberships = require_management_context(request)
    choices = _resident_choices(membership.building_id)
    if request.method == "GET":
        return render(
            request,
            "web/staff/bills/create.html",
            staff_context(
                request,
                membership,
                memberships,
                nav_active="bills",
                building_active="bills",
                form=BillForm(resident_choices=choices),
            ),
        )
    form = BillForm(request.POST, request.FILES, resident_choices=choices)
    if form.is_valid():
        document = None
        try:
            with transaction.atomic():
                document = upload_document(
                    membership.building,
                    Document.Kind.RESIDENT_BILL,
                    request.user,
                    form.cleaned_data["document"],
                )
                issue_bill(
                    request.user,
                    membership.building_id,
                    int(form.cleaned_data["resident"]),
                    title=form.cleaned_data["title"],
                    amount_vnd=form.cleaned_data["amount_vnd"],
                    document=document,
                    note=form.cleaned_data["note"],
                    period=form.cleaned_data["period"],
                    due_date=form.cleaned_data["due_date"],
                )
        except (ValidationError, BillError) as error:
            if document is not None:
                _delete_storage_blob(
                    document.storage_key, document.provider_version_id or ""
                )
            form.add_error(None, str(error))
        else:
            messages.success(request, _("Bill issued."))
            return redirect("web:staff-bill-list")
    return render(
        request,
        "web/staff/bills/create.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="bills",
            building_active="bills",
            form=form,
        ),
    )


@login_required
@require_GET
def bill_detail(request, pk):
    membership, memberships = require_management_context(request)
    bill = _bill_for(membership, pk)
    return render(
        request,
        "web/staff/bills/detail.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="bills",
            bill=bill,
            qr_svg=mark_safe(bill_qr_svg(bill.reference)),
            void_form=VoidBillForm(),
        ),
    )


@login_required
@require_POST
def bill_void(request, pk):
    membership, memberships = require_management_context(request)
    bill = _bill_for(membership, pk)
    form = VoidBillForm(request.POST)
    if not form.is_valid():
        return render(request, "web/staff/bills/detail.html", staff_context(
            request, membership, memberships, nav_active="bills", bill=bill,
            qr_svg=mark_safe(bill_qr_svg(bill.reference)), void_form=form,
        ))
    try:
        void_bill(request.user, bill.pk, reason=form.cleaned_data["reason"])
    except BillError as error:
        messages.error(request, str(error))
    else:
        messages.success(request, _("Bill voided."))
    return redirect("web:staff-bill-detail", bill.pk)
