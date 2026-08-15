"""Domain-side notification fan-out helpers (safe after commit)."""

from __future__ import annotations

from lamto.notifications.services import (
    EVENT_CASE_STATUS,
    EVENT_DEADLINE_RISK,
    EVENT_INTEGRITY_MISMATCH,
    EVENT_SETTLEMENT_RECORDED,
    EVENT_PUBLICATION,
    EVENT_QUARANTINED_UPLOAD,
    EVENT_REPORT_RECEIPT,
    EVENT_TRIAGE_STATUS,
    EVENT_WORK_COMPLETED,
    notify_users,
)


def _management_users(building_id: int):
    from lamto.accounts.models import ManagementMembership

    return [
        membership.user
        for membership in ManagementMembership.objects.select_related("user").filter(
            building_id=building_id, active=True
        )
    ]


def notify_report_receipt(report):
    building_id = report.unit.building_id
    recipients = [report.reporter] + _management_users(building_id)
    notify_users(
        recipients,
        event_key=f"{EVENT_REPORT_RECEIPT}:report:{report.pk}",
        subject="Report received",
        body=f"Report #{report.pk} was submitted: {report.text[:200]}",
        event_code=EVENT_REPORT_RECEIPT,
        building=building_id,
    )


def notify_info_requested(info_request):
    report = info_request.report
    notify_users(
        [report.reporter], event_key=f"info_requested:report:{report.pk}:info:{info_request.pk}",
        subject="More information requested", body=info_request.message,
        event_code="info_requested", building=report.unit.building_id,
    )


def notify_report_declined(report):
    notify_users(
        [report.reporter], event_key=f"report_declined:report:{report.pk}",
        subject="Request declined", body=report.declined_reason,
        event_code="report_declined", building=report.unit.building_id,
    )


def notify_triage_confirmed(case, report):
    recipients = [report.reporter] + _management_users(case.building_id)
    notify_users(
        recipients,
        event_key=f"{EVENT_TRIAGE_STATUS}:case:{case.pk}",
        subject="Triage confirmed",
        body=f"Case #{case.pk} opened for report #{report.pk} ({case.category}).",
        event_code=EVENT_TRIAGE_STATUS,
        building=case.building_id,
    )


def notify_deadline_risk(case):
    recipients = _management_users(case.building_id)
    day = case.deadline_at.date().isoformat() if case.deadline_at else "unknown"
    notify_users(
        recipients,
        event_key=f"{EVENT_DEADLINE_RISK}:case:{case.pk}:day:{day}",
        subject="Deadline risk",
        body=f"Case #{case.pk} approaches deadline {case.deadline_at}.",
        event_code=EVENT_DEADLINE_RISK,
        building=case.building_id,
    )


def _case_reporters(case):
    from lamto.maintenance.models import CaseReport
    return [
        link.report.reporter
        for link in CaseReport.objects.filter(case=case).select_related("report__reporter")
    ]


def notify_progress_update(update):
    case = update.case
    notify_users(_case_reporters(case), event_key=f"case_progress:update:{update.pk}",
                 subject="Case progress update", body=f"{update.cause}: {update.result}",
                 event_code=EVENT_CASE_STATUS, building=case.building_id)


def notify_case_completed(case):
    notify_users(
        _case_reporters(case),
        event_key=f"{EVENT_WORK_COMPLETED}:case:{case.pk}",
        subject="Work completed",
        body=f"Case #{case.pk} is complete — please rate it.",
        event_code=EVENT_WORK_COMPLETED,
        building=case.building_id,
    )


def notify_settled(settlement):
    proposal = settlement.proposal
    reporters = _case_reporters(proposal.case) if proposal.case_id else []
    notify_users(
        reporters + _management_users(proposal.building_id),
        event_key=f"settlement:settled:{settlement.pk}",
        subject="Settlement recorded",
        body=f"Proposal #{proposal.pk} settled for {settlement.amount_vnd} VND.",
        event_code=EVENT_SETTLEMENT_RECORDED,
        building=proposal.building_id,
    )


def notify_publication(entry):
    building_id = entry.case.building_id
    # Residents and management in the building.
    from lamto.accounts.models import ResidentOccupancy

    residents = [
        o.user
        for o in ResidentOccupancy.objects.filter(
            unit__building_id=building_id, active=True
        ).select_related("user")
    ]
    recipients = residents + _management_users(building_id)
    notify_users(
        recipients,
        event_key=f"{EVENT_PUBLICATION}:entry:{entry.pk}",
        subject="Ledger publication",
        body=f"Spending of {entry.actual_cost_vnd} VND published to the resident ledger.",
        event_code=EVENT_PUBLICATION,
        building=building_id,
    )


def notify_integrity_mismatch(entry, observation):
    building_id = entry.case.building_id
    recipients = _management_users(building_id)
    notify_users(
        recipients,
        event_key=f"{EVENT_INTEGRITY_MISMATCH}:entry:{entry.pk}:obs:{observation.pk}",
        subject="Integrity mismatch detected",
        body=f"Published ledger entry #{entry.pk} failed integrity verification.",
        event_code=EVENT_INTEGRITY_MISMATCH,
        building=building_id,
    )


def notify_quarantined_upload(upload, building_id=None):
    building_id = building_id or upload.building_id
    recipients = [upload.uploader] + _management_users(building_id)
    notify_users(
        recipients,
        event_key=f"{EVENT_QUARANTINED_UPLOAD}:upload:{upload.pk}",
        subject="Upload quarantined",
        body=f"File {upload.filename} was quarantined: {upload.reason}",
        event_code=EVENT_QUARANTINED_UPLOAD,
        building=building_id,
    )
