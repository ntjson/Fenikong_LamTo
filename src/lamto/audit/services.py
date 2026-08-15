from django.core.exceptions import PermissionDenied

from lamto.accounts.models import ManagementMembership, ResidentOccupancy

from .models import AuditEvent


def record_audit(actor, membership, action, target_type, target_id, result, metadata=None) -> AuditEvent:
    if membership is None:
        occupancy_id = (metadata or {}).get("occupancy_id")
        resident_report = (action, target_type) in {
            ("report.submit", "IssueReport"),
            ("request.info_replied", "InfoRequest"),
        }
        resident_rating = action == "work.rate" and target_type == "CompletionRating"
        resident_document = action == "document.upload" and target_type == "DocumentVersion"
        bill_payment = action == "bill.payment_recorded" and target_type == "Bill"
        valid_occupancy = occupancy_id is not None and ResidentOccupancy.objects.filter(
            pk=occupancy_id, user_id=getattr(actor, "pk", None), active=True
        ).exists()
        if bill_payment or (resident_report or resident_rating or resident_document) and valid_occupancy:
            pass
        elif (
            (action, target_type) != ("document.download", "DocumentVersion")
            or ManagementMembership.objects.filter(user_id=getattr(actor, "pk", None), active=True).exists()
            or (occupancy_id is not None and not valid_occupancy)
        ):
            raise PermissionDenied("Audit membership attribution is invalid.")
    elif not isinstance(membership, ManagementMembership) or not ManagementMembership.objects.filter(
        pk=membership.pk, user_id=getattr(actor, "pk", None), active=True
    ).exists():
        raise PermissionDenied("Audit membership attribution is invalid.")
    return AuditEvent.objects.create(
        actor=actor,
        membership=membership,
        action=action,
        target_type=target_type,
        target_id=target_id,
        result=result,
        metadata={} if metadata is None else metadata,
    )
