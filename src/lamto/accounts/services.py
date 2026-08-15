from django.core.exceptions import PermissionDenied

def require_management(user, building_id: int) -> "ManagementMembership":
    from .models import ManagementMembership

    membership = ManagementMembership.objects.filter(
        user=user, building_id=building_id, active=True
    ).first()
    if membership is None:
        raise PermissionDenied("management")
    return membership
