"""Fund ops workspace: entries list, balance, source recording + verification."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET, require_http_methods

from lamto.accounts.security import pop_stashed_post, require_recent_auth
from lamto.documents.models import Document
from lamto.finance.fund import (
    fund_balance,
    get_or_create_fund,
    record_fund_source,
    verify_fund_source,
)
from lamto.finance.models import MaintenanceFund, MaintenanceFundEntry
from lamto.finance.selectors import (
    FUND_SERIES_RANGE_KEYS,
    fund_period_flows,
    fund_series,
    pending_fund_verification_entries,
    pending_reconciliation_proposals,
    verified_fund_entries,
)
from lamto.web.forms.staff import RecordFundSourceForm
from lamto.web.staff import require_management_context, staff_context
from lamto.web.staff_documents import upload_document


FUND_CHART_RANGES = (
    ("30d", _("30 days")),
    ("6m", _("6 months")),
    ("12m", _("12 months")),
)


@login_required
@require_GET
def fund_home(request):
    from lamto.web.views.staff_common import prepare_record_list

    membership, memberships = require_management_context(request)
    building_id = membership.building_id
    entries_list = prepare_record_list(
        request,
        verified_fund_entries(building_id).select_related("recorder", "verification"),
        sorts=(("", _("Newest first"), ("-recorded_at", "-pk")),),
    )
    entries = entries_list["page"].object_list
    # Both pending selectors stay human-scale; materialize once for total + slice.
    pending_verification_all = list(pending_fund_verification_entries(building_id))
    pending_verification_total = len(pending_verification_all)
    pending_verification = pending_verification_all[:50]
    inflows, outflows = fund_period_flows(building_id, days=30)
    pending_all = list(pending_reconciliation_proposals(building_id))
    pending_total = len(pending_all)
    pending = pending_all[:50]
    range_key = request.GET.get("range", "6m")
    if range_key not in FUND_SERIES_RANGE_KEYS:
        range_key = "6m"
    series = fund_series(building_id, range_key=range_key)
    window_inflows = sum(row["inflows_vnd"] for row in series)
    window_outflows = sum(row["outflows_vnd"] for row in series)
    window_closing = series[-1]["balance_vnd"] if series else 0
    chart_points = [
        {**row, "period_start": row["period_start"].isoformat()} for row in series
    ]
    return render(
        request,
        "web/staff/fund_detail.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="finance",
            finance_active="fund",
            list_mode=True,
            entries=entries,
            entries_list=entries_list,
            pending_verification=pending_verification,
            pending_verification_total=pending_verification_total,
            pending_verification_capped=pending_verification_total > len(pending_verification),
            balance_vnd=fund_balance(building_id, verified_only=True),
            period_inflows=inflows,
            period_outflows=outflows,
            pending=pending,
            pending_total=pending_total,
            pending_capped=pending_total > len(pending),
            chart_points=chart_points,
            chart_range=range_key,
            chart_ranges=FUND_CHART_RANGES,
            window_opening_vnd=window_closing - window_inflows - window_outflows,
            window_closing_vnd=window_closing,
            window_inflows_vnd=window_inflows,
            window_outflows_vnd=window_outflows,
            fund_exists=MaintenanceFund.objects.filter(building_id=building_id).exists(),
            can_record=True,
            can_verify=True,
        ),
    )


@login_required
@require_http_methods(["GET", "POST"])
def fund_record(request):
    """Two-phase record of an opening-balance/inflow fund source (spec 4.3.2)."""
    membership, memberships = require_management_context(request)
    building = membership.building
    # Recent auth before the form renders: the five-minute window starts with typing.
    require_recent_auth(request)
    fund = get_or_create_fund(building)

    record_form = RecordFundSourceForm(
        request.POST or None,
        request.FILES or None,
        initial=pop_stashed_post(request) if request.method == "GET" else None,
    )
    if request.method == "POST" and record_form.is_valid():
        try:
            evidence = upload_document(
                building,
                Document.Kind.CONTRACT,
                request.user,
                record_form.cleaned_data["evidence"],
            )
            entry_type = record_form.cleaned_data["entry_type"]
            amount = record_form.cleaned_data["amount_vnd"]
            record_fund_source(fund, entry_type, amount, evidence, membership)
        except (ValidationError, PermissionDenied) as error:
            if isinstance(error, ValidationError):
                record_form.add_error(None, error)
            else:
                raise
        else:
            messages.success(request, _("Fund source recorded; awaiting verification."))
            return redirect("web:fund-home")

    return render(
        request,
        "web/staff/fund_detail.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="finance",
            finance_active="fund",
            list_mode=False,
            mode="record",
            record_form=record_form,
        ),
    )


@login_required
@require_http_methods(["GET", "POST"])
def fund_verify(request, pk):
    """Confirm an unverified fund source. Managers sign off offline before data
    entry, so the recorder may confirm their own source; the balance only counts
    confirmed sources, which keeps this a real gate against typos."""
    membership, memberships = require_management_context(request)
    building_id = membership.building_id
    entry = get_object_or_404(
        MaintenanceFundEntry.objects.select_related("recorder"),
        pk=pk,
        fund__building_id=building_id,
    )
    already_verified = hasattr(entry, "verification")
    if not already_verified:
        # The verify screen re-presents the frozen record; demanding recent auth
        # on render keeps review and sign-off inside one five-minute window.
        require_recent_auth(request)
    if request.method == "POST" and not already_verified:
        try:
            verify_fund_source(entry, membership)
        except (ValidationError, PermissionDenied) as error:
            if isinstance(error, ValidationError):
                messages.error(request, "; ".join(error.messages))
            else:
                raise
        else:
            messages.success(request, _("Fund source verified."))
            return redirect("web:fund-home")

    return render(
        request,
        "web/staff/fund_detail.html",
        staff_context(
            request,
            membership,
            memberships,
            nav_active="finance",
            finance_active="fund",
            list_mode=False,
            mode="verify",
            entry=entry,
            already_verified=already_verified,
        ),
    )
