from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext as _

from lamto.documents.models import Document
from lamto.finance.models import Proposal, Settlement
from lamto.finance.settlements import record_settlement
from lamto.web.forms.staff import RecordSettlementForm
from lamto.web.staff import require_management_context, staff_context
from lamto.web.views.staff_common import accountability_chain_for, prepare_record_list
from lamto.web.staff_documents import _delete_storage_blob, new_event_id, upload_document


def _context(request, membership, memberships, **extra):
    return staff_context(request, membership, memberships, nav_active="finance", finance_active="settlements", **extra)


@login_required
def settlement_list(request):
    membership, memberships = require_management_context(request)
    settlements_list = prepare_record_list(
        request,
        Settlement.objects.filter(proposal__building_id=membership.building_id).select_related("proposal", "outbox_event").order_by("-pk"),
        sorts=(("", _("Newest first"), ("-pk",)),),
    )
    pending_qs = Proposal.objects.filter(building_id=membership.building_id, status=Proposal.Status.COMPLETED, settlement__isnull=True).order_by("-pk")
    pending_total = pending_qs.count()
    pending = list(pending_qs[:50])
    return render(request, "web/staff/settlement_detail.html", _context(request, membership, memberships, settlements=settlements_list["page"].object_list, settlements_list=settlements_list, pending=pending, pending_total=pending_total, pending_capped=pending_total > len(pending), list_mode=True))


@login_required
@require_http_methods(["GET", "POST"])
def settlement_record(request, pk):
    membership, memberships = require_management_context(request)
    proposal = get_object_or_404(
        Proposal.objects.select_related("current_version"),
        pk=pk,
        building_id=membership.building_id,
    )
    form = RecordSettlementForm(
        request.POST or None,
        request.FILES or None,
        initial={"event_id": new_event_id()},
    )
    if request.method == "POST" and form.is_valid():
        proof = None
        try:
            with transaction.atomic():
                proof = upload_document(membership.building, Document.Kind.PAYMENT_PROOF, request.user, form.cleaned_data["proof_upload"])
                settlement = record_settlement(proposal, membership, transfer=proof, event_id=form.cleaned_data["event_id"])
        except (ValidationError, PermissionDenied) as error:
            # The rollback drops the version row but not the blob it already wrote.
            if proof is not None:
                _delete_storage_blob(proof.storage_key, proof.provider_version_id or "")
            form.add_error(None, error)
        else:
            messages.success(request, _("Settlement recorded and anchored."))
            return redirect("web:settlement-detail", pk=settlement.pk)
    return render(request, "web/staff/settlement_detail.html", _context(request, membership, memberships, proposal=proposal, settle_form=form, settle_mode=True))


@login_required
def settlement_detail(request, pk):
    membership, memberships = require_management_context(request)
    settlement = get_object_or_404(Settlement.objects.select_related("proposal", "proposal__current_version", "outbox_event", "transfer"), pk=pk, proposal__building_id=membership.building_id)
    return render(
        request,
        "web/staff/settlement_detail.html",
        _context(
            request,
            membership,
            memberships,
            settlement=settlement,
            accountability_stages=accountability_chain_for(settlement),
        ),
    )
