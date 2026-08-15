import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import timedelta

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone

from lamto.audit.services import record_audit

from .backends import normalize_phone
from .models import RegistrationRequest, ResidentOccupancy, Unit, User
from .services import require_management


class RegistrationConflict(Exception):
    pass


@dataclass(frozen=True)
class RegistrationSubmission:
    request: RegistrationRequest
    status_token: str = field(repr=False)


_DUPLICATE_CONSTRAINTS = {
    "unique_pending_registration_phone",
    "unique_pending_registration_email",
}
_USER_DUPLICATE_CONSTRAINTS = {"accounts_user_email_key", "accounts_user_phone_key"}


def status_token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _expire_requests(requests, now):
    for request in requests:
        request.status = RegistrationRequest.Status.EXPIRED
        request.password_hash = ""
        request.decided_at = now
        request.updated_at = now
    RegistrationRequest.objects.bulk_update(
        requests, ["status", "password_hash", "decided_at", "updated_at"]
    )


def expire_registration_requests(*, limit=100, now=None) -> int:
    now = now or timezone.now()
    with transaction.atomic():
        requests = list(
            RegistrationRequest.objects.select_for_update(skip_locked=True)
            .filter(
                status=RegistrationRequest.Status.PENDING,
                expires_at__lte=now,
            )
            .order_by("expires_at")[:limit]
        )
        _expire_requests(requests, now)
    return len(requests)


@transaction.atomic
def submit_registration(*, full_name, phone, email, password, building_id, unit_id):
    user_phone = normalize_phone(phone)
    email = (
        BaseUserManager.normalize_email(email.strip()).casefold()
        if email and email.strip()
        else None
    )
    if user_phone is None or not Unit.objects.filter(
        pk=unit_id, building_id=building_id
    ).exists():
        raise RegistrationConflict("Registration cannot be submitted")
    phone = "+84" + user_phone[1:]

    matching = Q(phone=phone)
    if email is not None:
        matching |= Q(email=email)
    now = timezone.now()
    stale = list(
        RegistrationRequest.objects.select_for_update().filter(
            matching,
            status=RegistrationRequest.Status.PENDING,
            expires_at__lte=now,
        ).order_by("pk")
    )
    _expire_requests(stale, now)
    expire_registration_requests()
    duplicate = User.objects.filter(phone=user_phone)
    pending = RegistrationRequest.objects.filter(
        status=RegistrationRequest.Status.PENDING, phone=phone
    )
    if email is not None:
        duplicate = duplicate | User.objects.filter(email__iexact=email)
        pending = pending | RegistrationRequest.objects.filter(
            status=RegistrationRequest.Status.PENDING, email=email
        )
    if duplicate.exists() or pending.exists():
        raise RegistrationConflict("Registration cannot be submitted")

    token = secrets.token_urlsafe(32)
    try:
        request = RegistrationRequest.objects.create(
            full_name=full_name.strip(),
            phone=phone,
            email=email,
            building_id=building_id,
            unit_id=unit_id,
            password_hash=make_password(password),
            status_token_digest=status_token_digest(token),
            expires_at=timezone.now() + timedelta(days=30),
        )
    except IntegrityError as error:
        constraint = getattr(getattr(error.__cause__, "diag", None), "constraint_name", None)
        if constraint in _DUPLICATE_CONSTRAINTS:
            raise RegistrationConflict("Registration cannot be submitted") from error
        raise
    return RegistrationSubmission(request=request, status_token=token)


def get_registration_status(status_token):
    now = timezone.now()
    with transaction.atomic():
        request = RegistrationRequest.objects.select_for_update().get(
            status_token_digest=status_token_digest(status_token)
        )
        if (
            request.status == RegistrationRequest.Status.PENDING
            and request.expires_at <= now
        ):
            _expire_requests([request], now)
        return request


def approve_registration(*, request_id, actor):
    expired = False
    try:
        with transaction.atomic():
            request = (
                RegistrationRequest.objects.select_for_update()
                .select_related("building", "unit")
                .get(pk=request_id)
            )
            membership = require_management(actor, request.building_id)
            if request.status != RegistrationRequest.Status.PENDING:
                raise RegistrationConflict()
            now = timezone.now()
            if request.expires_at <= now:
                _expire_requests([request], now)
                expired = True
            else:
                user = User(
                    display_name=request.full_name,
                    phone=request.phone,
                    email=request.email,
                    is_active=True,
                )
                user.password = request.password_hash
                user.save()
                ResidentOccupancy.objects.create(user=user, unit=request.unit, active=True)
                request.status = RegistrationRequest.Status.APPROVED
                request.password_hash = ""
                request.decided_by = actor
                request.decided_at = now
                request.save(
                    update_fields=[
                        "status",
                        "password_hash",
                        "decided_by",
                        "decided_at",
                        "updated_at",
                    ]
                )
                record_audit(
                    actor,
                    membership,
                    "registration.approved",
                    "RegistrationRequest",
                    str(request.pk),
                    "accepted",
                    {"building_id": request.building_id, "unit_id": request.unit_id},
                )
                return user
    except IntegrityError as error:
        constraint = getattr(getattr(error.__cause__, "diag", None), "constraint_name", None)
        if constraint in _USER_DUPLICATE_CONSTRAINTS:
            raise RegistrationConflict() from error
        raise
    if expired:
        raise RegistrationConflict()


def reject_registration(*, request_id, actor, reason):
    reason = reason.strip()
    if not reason:
        raise ValueError("Rejection reason is required")
    with transaction.atomic():
        request = (
            RegistrationRequest.objects.select_for_update()
            .select_related("building", "unit")
            .get(pk=request_id)
        )
        membership = require_management(actor, request.building_id)
        if request.status != RegistrationRequest.Status.PENDING:
            raise RegistrationConflict()
        now = timezone.now()
        if request.expires_at <= now:
            _expire_requests([request], now)
            expired = True
        else:
            expired = False
            request.status = RegistrationRequest.Status.REJECTED
            request.password_hash = ""
            request.rejection_reason = reason
            request.decided_by = actor
            request.decided_at = now
            request.save(
                update_fields=[
                    "status",
                    "password_hash",
                    "rejection_reason",
                    "decided_by",
                    "decided_at",
                    "updated_at",
                ]
            )
            record_audit(
                actor,
                membership,
                "registration.rejected",
                "RegistrationRequest",
                str(request.pk),
                "accepted",
                {
                    "building_id": request.building_id,
                    "unit_id": request.unit_id,
                    "reason": reason,
                },
            )
    if expired:
        raise RegistrationConflict()
