"""Management workspace: triage, cases, proposals."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext, gettext_lazy as _
from django.views.decorators.http import require_GET, require_http_methods

from lamto.audit.services import record_audit
from lamto.documents.models import Document, DocumentVersion
from lamto.finance.models import (
    Proposal,
    PublishedLedgerEntry,
)
from lamto.evidence.models import BlockchainOutboxEvent, SETTLED_STATUSES
from lamto.finance.publication import publish_settlement_entry
from lamto.finance.proposals import (
    ZERO_HASH,
    build_proposal_evidence_payload,
    create_proposal,
    create_standalone_proposal,
    decide_proposal,
    publish_proposal_version,
    spending_proposal_cases,
)
from lamto.maintenance.models import IssueReport, MaintenanceCase
from lamto.maintenance.cases import complete_proposal_work, publish_progress, start_case_work
from lamto.web.forms.staff import (
    ConfirmTriageForm,
    CreateProposalForm,
    ProposalDecisionForm,
    PublishLedgerEntryForm,
    ProgressUpdateForm,
    StandaloneProposalForm,
)
from lamto.web.staff import require_management_context, staff_context
from lamto.web.views.staff_common import (
    accountability_chain_for,
    prepare_record_list,
)
from lamto.web.staff_documents import _delete_storage_blob, new_event_id, upload_document


def _proposal_publishable(proposal) -> bool:
    """True when verified payment chain is ready and nothing is published yet."""
    if PublishedLedgerEntry.objects.filter(proposal=proposal).exists():
        return False
    settlement = getattr(proposal, "settlement", None)
    return bool(
        settlement
        and settlement.settled_at
        and settlement.outbox_event.status in SETTLED_STATUSES
        and proposal.current_version
        and proposal.current_version.outbox_event.status in SETTLED_STATUSES
    )


def _resolve_proposal_action_panel(
    proposal: Proposal,
    *,
    can_publish: bool,
    publication_problem: str | None,
) -> str | None:
    """Resolve the single action panel to render for a Management account."""
    if can_publish:
        return "publish"
    if publication_problem == BlockchainOutboxEvent.Status.FAILED:
        return "failed"
    if publication_problem == BlockchainOutboxEvent.Status.MISMATCH:
        return "mismatch"
    if proposal.status == Proposal.Status.PUBLISHED:
        return "decide"
    if proposal.status == Proposal.Status.IN_PROGRESS:
        if proposal.case_id:
            return "case"
        return "progress"
    return None


def _proposal_next_action(proposal: Proposal) -> str:
    if proposal.status == Proposal.Status.DRAFT:
        return _("Complete and submit")
    if proposal.status == Proposal.Status.PUBLISHED:
        return _("Decide whether to proceed")
    if proposal.status == Proposal.Status.IN_PROGRESS:
        if proposal.case_id:
            return _("Follow work on case")
        return _("Publish progress or complete")
    if proposal.status == Proposal.Status.COMPLETED:
        return _("Record settlement")
    return ""


@login_required
@require_GET
def proposal_list(request):
    membership, memberships = require_management_context(request)
    building_id = membership.building_id
    status = request.GET.get("status") or ""
    valid_status = status in Proposal.Status.values
    proposals_qs = Proposal.objects.filter(building_id=building_id)
    if valid_status:
        proposals_qs = proposals_qs.filter(status=status)
    list_meta = prepare_record_list(
        request,
        proposals_qs.select_related("current_version", "case"),
        search_fields=(
            "current_version__contractor_name",
            "case__category",
        ),
        sorts=(("", _("Newest first"), ("-created_at",)),),
    )
    proposal_items = [
        {
            "url": f"/s/proposals/{p.pk}/",
            "title": gettext("Proposal #%(id)s · %(subject)s")
            % {
                "id": p.pk,
                "subject": p.case.get_category_display()
                if p.case_id
                else (p.current_version.purpose if p.current_version else gettext("Standalone")),
            }
            + (
                f" · {p.current_version.contractor_name}"
                if p.current_version
                else ""
            ),
            "amount_vnd": p.current_version.amount_vnd if p.current_version else None,
            "status": p.get_status_display(),
            "deadline": None,
            "deadline_tone": "neutral",
            "next_action": _proposal_next_action(p),
        }
        for p in list_meta["page"].object_list
    ]
    filters = [
        {"label": label, "value": value, "active": value == status}
        for value, label in Proposal.Status.choices
    ]
    return render(
        request,
        "web/staff/proposal_detail.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="finance",
            finance_active="proposals",
            list_mode=True,
            proposal_items=proposal_items,
            list_meta=list_meta,
            search_label=_("Search proposals"),
            search_placeholder=_("ID, contractor, or category…"),
            filters=filters,
            filters_active=valid_status,
            filter_param="status",
            can_publish=True,
            publish_only=False,
        ),
    )

@login_required
@require_http_methods(["GET", "POST"])
def proposal_detail(request, pk):
    membership, memberships = require_management_context(request)
    proposal = get_object_or_404(
        Proposal.objects.select_related(
            "current_version", "current_version__outbox_event", "case", "creator_membership"
        ),
        pk=pk,
        building_id=membership.building_id,
    )
    can_publish = _proposal_publishable(proposal)
    version = proposal.current_version
    action = request.POST.get("action") if request.method == "POST" else None
    progress_form = ProgressUpdateForm(
        request.POST if action in {"progress", "complete"} else None,
    )
    publish_form = PublishLedgerEntryForm(request.POST if action == "publish" else None)
    decision_form = ProposalDecisionForm(
        request.POST if action == "decide" else None
    )

    if request.method == "POST":
        action = action or "publish"
        if action == "publish":
            if not can_publish:
                messages.error(request, _("This proposal is not eligible for publication."))
                return redirect("web:proposal-detail", pk=proposal.pk)
            if publish_form.is_valid():
                try:
                    publish_settlement_entry(proposal.settlement)
                except (ValidationError, PermissionDenied) as error:
                    publish_form.add_error(None, error)
                else:
                    messages.success(request, _("Settled expense published to the resident ledger."))
                    return redirect("web:proposal-detail", pk=proposal.pk)
        elif action == "decide":
            if decision_form.is_valid():
                proceed = decision_form.proceed
                try:
                    with transaction.atomic():
                        if proceed and proposal.case_id:
                            start_case_work(proposal.case, request.user)
                        decide_proposal(
                            proposal, request.user, proceed,
                            decision_form.cleaned_data.get("note", ""),
                        )
                except (ValidationError, PermissionDenied) as error:
                    messages.error(request, "; ".join(getattr(error, "messages", [str(error)])))
                else:
                    if proceed:
                        messages.success(request, _("Decision recorded. Work on this proposal can start."))
                    else:
                        messages.success(request, _("Decision recorded. This proposal is closed as not proceeding."))
                return redirect("web:proposal-detail", pk=proposal.pk)
        elif action in {"progress", "complete"}:
            try:
                if not progress_form.is_valid():
                    raise ValidationError(_("Review the progress fields."))
                with transaction.atomic():
                    if action == "progress":
                        publish_progress(
                            proposal=proposal, manager=request.user,
                            cause=progress_form.cleaned_data["cause"], result=progress_form.cleaned_data["result"],
                        )
                    else:
                        complete_proposal_work(
                            proposal, request.user, progress_form.cleaned_data["cause"],
                            progress_form.cleaned_data["result"],
                        )
            except (ValidationError, PermissionDenied) as error:
                if isinstance(error, ValidationError):
                    progress_form.add_error(None, error)
                else:
                    messages.error(request, str(error))
            else:
                messages.success(request, _("Proposal updated."))
                return redirect("web:proposal-detail", pk=proposal.pk)

    publication_snapshot = version
    publication_status = version.outbox_event.status if version else None
    publication_pending = publication_status in {
        BlockchainOutboxEvent.Status.PENDING,
        BlockchainOutboxEvent.Status.SUBMITTED,
    }
    publication_problem = publication_status if publication_status in {
        BlockchainOutboxEvent.Status.FAILED,
        BlockchainOutboxEvent.Status.MISMATCH,
    } else None

    action_panel = _resolve_proposal_action_panel(
        proposal,
        can_publish=can_publish,
        publication_problem=publication_problem,
    )

    return render(
        request,
        "web/staff/proposal_detail.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="finance",
            finance_active="proposals",
            list_mode=False,
            proposal=proposal,
            version=version,
            action_panel=action_panel,
            publish_form=publish_form if can_publish else None,
            can_publish=can_publish,
            publication_pending=publication_pending,
            publication_problem=publication_problem,
            publication_snapshot=publication_snapshot,
            progress_form=progress_form,
            decision_form=decision_form,
            accountability_stages=accountability_chain_for(
                proposal, publication_pending=publication_pending
            ),
        ),
    )


@login_required
@require_http_methods(["GET", "POST"])
def proposal_create(request, pk):
    membership, memberships = require_management_context(request)
    building_id = membership.building_id
    case = get_object_or_404(
        MaintenanceCase.objects.all(),
        pk=pk,
        building_id=building_id,
    )
    if not spending_proposal_cases().filter(pk=case.pk).exists():
        messages.error(request, _("This case is not eligible for a spending proposal."))
        return redirect("web:case-detail", pk=case.pk)
    existing = (
        Proposal.objects.filter(case=case)
        .select_related("current_version")
        .first()
    )
    if existing is not None and existing.current_version_id is not None:
        messages.info(request, _("A proposal has already been submitted for this case."))
        return redirect("web:proposal-detail", pk=existing.pk)

    create_form = CreateProposalForm(
        request.POST or None,
        request.FILES or None,
    )
    if request.method == "POST" and create_form.is_valid():
        original = None
        try:
            with transaction.atomic():
                original = upload_document(
                    case.building, Document.Kind.QUOTATION, request.user,
                    create_form.cleaned_data["quotation"],
                )
                proposal = existing or create_proposal(case, membership)
                publish_proposal_version(
                    proposal, membership, amount_vnd=create_form.cleaned_data["amount_vnd"],
                    contractor_name=create_form.cleaned_data["contractor_name"],
                    purpose=create_form.cleaned_data.get("purpose") or case.get_category_display(),
                    proposed_action=create_form.cleaned_data.get("proposed_action") or "Perform proposed maintenance",
                    expected_start=create_form.cleaned_data.get("expected_start"),
                    expected_end=create_form.cleaned_data.get("expected_end"),
                    quotation_versions=[original], event_id=new_event_id(),
                )
        except (ValidationError, PermissionDenied) as error:
            if original is not None:
                _delete_storage_blob(original.storage_key, original.provider_version_id or "")
            create_form.add_error(None, error)
        else:
            messages.success(request, _("Proposal published."))
            return redirect("web:proposal-detail", pk=proposal.pk)

    return render(
        request,
        "web/staff/proposal_create.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="finance",
            finance_active="proposals",
            case=case,
            create_form=create_form,
        ),
    )


@login_required
@require_http_methods(["GET", "POST"])
def standalone_proposal_create(request):
    membership, memberships = require_management_context(request)
    form = StandaloneProposalForm(
        request.POST or None,
        request.FILES or None,
    )
    if request.method == "POST":
        if form.is_valid():
            original = None
            try:
                with transaction.atomic():
                    original = upload_document(
                        membership.building, Document.Kind.QUOTATION, request.user,
                        form.cleaned_data["quotation"],
                    )
                    proposal = create_standalone_proposal(membership.building, membership)
                    publish_proposal_version(
                        proposal, membership, amount_vnd=form.cleaned_data["amount_vnd"],
                        contractor_name=form.cleaned_data["contractor_name"],
                        purpose=form.cleaned_data["purpose"],
                        proposed_action=form.cleaned_data["proposed_action"],
                        expected_start=form.cleaned_data["expected_start"],
                        expected_end=form.cleaned_data["expected_end"],
                        quotation_versions=[original], event_id=new_event_id(),
                    )
            except (ValidationError, PermissionDenied) as error:
                if original is not None:
                    _delete_storage_blob(original.storage_key, original.provider_version_id or "")
                form.add_error(None, error)
            else:
                messages.success(request, _("Proposal published."))
                return redirect("web:proposal-detail", pk=proposal.pk)
    return render(request, "web/staff/proposal_create.html", staff_context(
        request, membership, memberships, nav_active="finance", finance_active="proposals",
        case=None, create_form=form,
    ))
