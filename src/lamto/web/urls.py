from django.urls import path
from django.views.generic import RedirectView

from lamto.web.announcement_views import (
    announcement_create,
    announcement_detail,
    announcement_edit,
    announcement_list,
    announcement_withdraw,
)
from lamto.web.bill_views import bill_create, bill_detail, bill_list, bill_void
from lamto.web.registration_views import (
    registration_approve,
    registration_detail,
    registration_list,
    registration_reject,
)
from lamto.web.views import (
    documents,
    exceptions,
    exports,
    fund,
    gate,
    health,
    proposals,
    requests,
    settlements,
    staff_common,
)

app_name = "web"

urlpatterns = [
    path(
        "",
        RedirectView.as_view(pattern_name="web:staff-home", permanent=False),
        name="root",
    ),
    # Shell
    path("s/", staff_common.staff_home, name="staff-home"),
    path("s/inbox/", staff_common.action_inbox, name="action-inbox"),
    path("s/building/", staff_common.switch_building, name="switch-building"),
    path("s/announcements/", announcement_list, name="staff-announcement-list"),
    path(
        "s/announcements/create/", announcement_create, name="staff-announcement-create"
    ),
    path("s/bills/", bill_list, name="staff-bill-list"),
    path("s/bills/create/", bill_create, name="staff-bill-create"),
    path("s/bills/<int:pk>/", bill_detail, name="staff-bill-detail"),
    path("s/bills/<int:pk>/void/", bill_void, name="staff-bill-void"),
    path(
        "s/announcements/<int:announcement_id>/",
        announcement_detail,
        name="staff-announcement-detail",
    ),
    path(
        "s/announcements/<int:announcement_id>/edit/",
        announcement_edit,
        name="staff-announcement-edit",
    ),
    path(
        "s/announcements/<int:announcement_id>/withdraw/",
        announcement_withdraw,
        name="staff-announcement-withdraw",
    ),
    path("s/registrations/", registration_list, name="staff-registration-list"),
    path(
        "s/registrations/<int:request_id>/",
        registration_detail,
        name="staff-registration-detail",
    ),
    path(
        "s/registrations/<int:request_id>/approve/",
        registration_approve,
        name="staff-registration-approve",
    ),
    path(
        "s/registrations/<int:request_id>/reject/",
        registration_reject,
        name="staff-registration-reject",
    ),
    # Requests (cases + reports)
    path("s/cases/", requests.case_list, name="case-list"),
    path("s/reports/<int:pk>/", requests.report_detail, name="staff-report-detail"),
    path("s/cases/<int:pk>/", requests.case_detail, name="case-detail"),
    # Proposals
    path("s/proposals/", proposals.proposal_list, name="proposal-list"),
    path(
        "s/proposals/new/",
        proposals.standalone_proposal_create,
        name="standalone-proposal-create",
    ),
    path("s/proposals/<int:pk>/", proposals.proposal_detail, name="proposal-detail"),
    path(
        "s/cases/<int:pk>/propose/", proposals.proposal_create, name="proposal-create"
    ),
    path("s/settlements/", settlements.settlement_list, name="settlement-list"),
    path(
        "s/settlements/record/<int:pk>/",
        settlements.settlement_record_transfer,
        name="settlement-record-transfer",
    ),
    path(
        "s/settlements/<int:pk>/ack/",
        settlements.settlement_record_ack,
        name="settlement-record-ack",
    ),
    path(
        "s/settlements/<int:pk>/",
        settlements.settlement_detail,
        name="settlement-detail",
    ),
    # Exports
    path("s/exports/", exports.export_home, name="export-home"),
    path("s/audit/export/", exports.audit_export, name="audit-export"),
    # Documents (staff evidence download)
    path(
        "s/documents/<int:version_id>/",
        documents.staff_document_redirect,
        name="staff-document",
    ),
    path(
        "s/documents/d/<str:token>/",
        documents.staff_document_download,
        name="staff-document-download",
    ),
    # Fund
    path("s/fund/", fund.fund_home, name="fund-home"),
    path("s/fund/record/", fund.fund_record, name="fund-record"),
    path("s/fund/verify/<int:pk>/", fund.fund_verify, name="fund-verify"),
    # Ops
    path("s/ops/health/", health.ops_health, name="ops-health"),
    path("s/ops/metrics/", health.pilot_metrics, name="pilot-metrics"),
    path("s/exceptions/", exceptions.exception_list, name="exception-list"),
    path(
        "s/exceptions/<str:kind>/<int:pk>/",
        exceptions.exception_review,
        name="exception-review",
    ),
    path("s/gate/", gate.gate_queue, name="gate-queue"),
    path("s/gate/face/<int:pk>/photo/", gate.gate_face_photo, name="gate-face-photo"),
    path(
        "s/gate/face/<int:pk>/decide/", gate.gate_face_decide, name="gate-face-decide"
    ),
    path(
        "s/gate/plates/<int:pk>/decide/",
        gate.gate_plate_decide,
        name="gate-plate-decide",
    ),
    path("s/gate/registrations/", gate.gate_registrations, name="gate-registrations"),
    path("s/gate/devices/", gate.gate_devices, name="gate-devices"),
    path("s/gate/log/", gate.gate_log, name="gate-log"),
]
