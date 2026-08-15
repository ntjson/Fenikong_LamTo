from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from lamto.audit.services import record_audit
from lamto.accounts.models import ResidentOccupancy

from .cases import TERMINAL_STATUSES
from .models import CaseReport, CompletionRating, IssueReport, MaintenanceCase


@transaction.atomic
def rate_completed_case(resident, case, satisfied, comment="") -> CompletionRating:
    case = MaintenanceCase.objects.select_for_update().filter(pk=getattr(case, "pk", None)).first()
    if case is None:
        raise ValidationError("Case is required.")
    if case.completed_at is None:
        raise ValidationError("Only completed cases can be rated.")
    if type(satisfied) is not bool:
        raise ValidationError("Satisfied must be a boolean.")
    if comment is None:
        comment = ""
    if not isinstance(comment, str):
        raise ValidationError("Rating comment must be text.")
    comment = comment.strip()
    if len(comment) > 500:
        raise ValidationError("Rating comment must be at most 500 characters.")

    owns_report = CaseReport.objects.filter(
        case=case,
        report__reporter_id=getattr(resident, "pk", None),
    ).exists()
    if not owns_report:
        raise PermissionDenied("Only residents who reported this case may rate the work.")

    occupancy = ResidentOccupancy.objects.filter(
        user=resident, active=True, unit__building_id=case.building_id
    ).first()
    if occupancy is None:
        raise PermissionDenied("Active occupancy in the building is required to rate work.")

    if CompletionRating.objects.filter(resident=resident, case=case).exists():
        raise ValidationError("This case has already been rated by this resident.")

    rating = CompletionRating.objects.create(
        resident=resident,
        case=case,
        satisfied=satisfied,
        comment=comment,
        created_at=timezone.now(),
    )
    record_audit(
        actor=resident,
        membership=None,
        action="work.rate",
        target_type="CompletionRating",
        target_id=str(rating.pk),
        result="accepted",
        metadata={"occupancy_id": occupancy.pk, "case_id": case.pk},
    )
    IssueReport.objects.filter(
        case_reports__case=case, reporter=resident, status=IssueReport.Status.COMPLETED
    ).update(status=IssueReport.Status.CLOSED)
    if not IssueReport.objects.filter(case_reports__case=case).exclude(status__in=TERMINAL_STATUSES).exists():
        case.active = False
        case.closed_at = timezone.now()
        case.save(update_fields=["active", "closed_at"])
    return rating


@transaction.atomic
def rate_completed_proposal(resident, proposal, satisfied, comment="") -> CompletionRating:
    from lamto.finance.models import Proposal
    proposal = Proposal.objects.select_for_update().filter(
        pk=getattr(proposal, "pk", None), case__isnull=True
    ).first()
    if proposal is None:
        raise ValidationError("Standalone proposal is required.")
    if proposal.status != Proposal.Status.COMPLETED or proposal.completed_at is None:
        raise ValidationError("Only completed proposals can be rated.")
    if type(satisfied) is not bool:
        raise ValidationError("Satisfied must be a boolean.")
    if comment is None:
        comment = ""
    if not isinstance(comment, str) or len(comment.strip()) > 500:
        raise ValidationError("Rating comment must be text of at most 500 characters.")
    occupancy = ResidentOccupancy.objects.filter(
        user=resident, active=True, unit__building_id=proposal.building_id
    ).first()
    if occupancy is None:
        raise PermissionDenied("Active occupancy in the building is required to rate work.")
    if CompletionRating.objects.filter(resident=resident, proposal=proposal).exists():
        raise ValidationError("This proposal has already been rated by this resident.")
    rating = CompletionRating.objects.create(
        resident=resident, proposal=proposal, satisfied=satisfied,
        comment=comment.strip(), created_at=timezone.now(),
    )
    record_audit(resident, None, "work.rate", "CompletionRating", str(rating.pk), "accepted",
                 {"occupancy_id": occupancy.pk, "proposal_id": proposal.pk})
    return rating
