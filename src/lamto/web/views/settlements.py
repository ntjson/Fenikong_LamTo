from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext as _

from lamto.accounts.security import pop_stashed_post, require_recent_auth
from lamto.documents.models import Document
from lamto.finance.models import Proposal, Settlement
from lamto.finance.settlements import record_acknowledgement, record_transfer
from lamto.web.forms.staff import RecordSettlementAcknowledgementForm, RecordSettlementTransferForm
from lamto.web.staff import require_management_context, staff_context
from lamto.web.views.staff_common import accountability_chain_for, prepare_record_list
from lamto.web.staff_documents import _delete_storage_blob, document_options, new_event_id, selected_document, upload_document


def _context(request, membership, memberships, **extra):
    return staff_context(request, membership, memberships, nav_active="finance", finance_active="settlements", **extra)


@login_required
def settlement_list(request):
    membership, memberships = require_management_context(request)
    settlements_list = prepare_record_list(
        request,
        Settlement.objects.filter(proposal__building_id=membership.building_id).select_related("proposal", "outbox_event", "ack").order_by("-pk"),
        sorts=(("", _("Newest first"), ("-pk",)),),
    )
    pending_qs = Proposal.objects.filter(building_id=membership.building_id, status=Proposal.Status.COMPLETED, settlement__isnull=True).order_by("-pk")
    pending_total = pending_qs.count()
    pending = list(pending_qs[:50])
    return render(request, "web/staff/settlement_detail.html", _context(request, membership, memberships, settlements=settlements_list["page"].object_list, settlements_list=settlements_list, pending=pending, pending_total=pending_total, pending_capped=pending_total > len(pending), list_mode=True))


@login_required
@require_http_methods(["GET", "POST"])
def settlement_record_transfer(request, pk):
    membership, memberships = require_management_context(request)
    # Recent auth before the form renders: the five-minute window starts with typing.
    require_recent_auth(request)
    proposal = get_object_or_404(
        Proposal.objects.select_related("current_version"),
        pk=pk,
        building_id=membership.building_id,
    )
    options = document_options(membership.building_id, Document.Kind.PAYMENT_PROOF)
    form = RecordSettlementTransferForm(
        request.POST or None,
        request.FILES or None,
        proof_choices=[(value, label) for value, label, _ in options],
        initial=pop_stashed_post(request) if request.method == "GET" else None,
    )
    if request.method == "POST" and form.is_valid():
        uploaded = False
        try:
            with transaction.atomic():
                uploaded = bool(form.cleaned_data.get("proof_upload"))
                proof = upload_document(membership.building, Document.Kind.PAYMENT_PROOF, request.user, form.cleaned_data["proof_upload"]) if uploaded else selected_document(options, form.cleaned_data["proof"])
                if proof is not None:
                    settlement = record_transfer(proposal, membership, transfer=proof, **{key: form.cleaned_data[key] for key in ("amount_vnd", "payee_name", "bank_reference")})
        except (ValidationError, PermissionDenied) as error:
            if uploaded and "proof" in locals() and proof is not None:
                _delete_storage_blob(proof.storage_key, proof.provider_version_id or "")
            form.add_error(None, error)
            proof = None
        if proof is None:
            if not form.errors:
                form.add_error("proof", _("Selected evidence is no longer available."))
        else:
            messages.success(request, _("Transfer evidence recorded."))
            return redirect("web:settlement-detail", pk=settlement.pk)
    return render(request, "web/staff/settlement_detail.html", _context(request, membership, memberships, proposal=proposal, transfer_form=form, transfer_mode=True))


@login_required
@require_http_methods(["GET", "POST"])
def settlement_record_ack(request, pk):
    membership, memberships = require_management_context(request)
    require_recent_auth(request)
    settlement = get_object_or_404(Settlement, pk=pk, proposal__building_id=membership.building_id)
    options = document_options(membership.building_id, Document.Kind.PAYMENT_PROOF)
    initial = {"event_id": new_event_id()}
    if request.method == "GET":
        initial = {**initial, **(pop_stashed_post(request) or {})}
        initial["event_id"] = initial["event_id"] or new_event_id()
    form = RecordSettlementAcknowledgementForm(request.POST or None, request.FILES or None, initial=initial, proof_choices=[(value, label) for value, label, _ in options])
    if request.method == "POST" and form.is_valid():
        uploaded = False
        try:
            with transaction.atomic():
                uploaded = bool(form.cleaned_data.get("proof_upload"))
                proof = upload_document(membership.building, Document.Kind.PAYMENT_PROOF, request.user, form.cleaned_data["proof_upload"]) if uploaded else selected_document(options, form.cleaned_data["proof"])
                if proof is not None:
                    record_acknowledgement(settlement, membership, ack=proof, event_id=form.cleaned_data["event_id"])
        except (ValidationError, PermissionDenied) as error:
            if uploaded and "proof" in locals() and proof is not None:
                _delete_storage_blob(proof.storage_key, proof.provider_version_id or "")
            form.add_error(None, error)
            proof = None
        if proof is None:
            if not form.errors:
                form.add_error("proof", _("Selected evidence is no longer available."))
        else:
            messages.success(request, _("Acknowledgement recorded; settlement anchored."))
            return redirect("web:settlement-detail", pk=settlement.pk)
    return render(request, "web/staff/settlement_detail.html", _context(request, membership, memberships, settlement=settlement, ack_form=form, ack_mode=True))


@login_required
def settlement_detail(request, pk):
    membership, memberships = require_management_context(request)
    settlement = get_object_or_404(Settlement.objects.select_related("proposal", "outbox_event", "transfer", "ack"), pk=pk, proposal__building_id=membership.building_id)
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
