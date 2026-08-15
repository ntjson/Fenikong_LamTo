"""Resident API views (spec 3). Resident-only; staff stay on the /s/ web surface."""

from django.contrib.auth import authenticate
from django.conf import settings
from django.core import signing
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import HttpResponse
from django.db import transaction
from django.urls import reverse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from knox.models import AuthToken
from knox.views import LogoutAllView as KnoxLogoutAllView
from knox.views import LogoutView as KnoxLogoutView
from rest_framework import exceptions, generics, pagination, parsers, permissions
from rest_framework import status as drf_status
from rest_framework.response import Response
from rest_framework.views import APIView

from lamto.accounts.security import (
    assert_not_throttled,
    client_ip,
    record_auth_failure,
    reset_auth_throttle,
)
from lamto.accounts.tenancy import active_occupancies
from lamto.api import problems
from lamto.api.authentication import ResidentTokenAuthentication
from lamto.api.downloads import (
    DOWNLOAD_MAX_AGE,
    DOWNLOAD_SALT,
    content_disposition_inline,
    issue_download_token,
    resident_can_download,
)
from lamto.api.occupancy import OCCUPANCY_HEADER_PARAMETER, resolve_api_occupancy
from lamto.api.problems import problem_responses
from lamto.api.serializers import (
    DeviceRegisterSerializer,
    DeviceSerializer,
    FundSeriesSerializer,
    FundSummarySerializer,
    LedgerEntryDetailSerializer,
    LedgerEntryListSerializer,
    LedgerFilterSerializer,
    LocationSerializer,
    LoginSerializer,
    LogoutInstallIdSerializer,
    MeSerializer,
    NotificationFeedSerializer,
    NotificationFilterSerializer,
    NotificationPreferenceSerializer,
    NotificationPreferenceUpdateSerializer,
    ReportCreateSerializer,
    ReportDetailSerializer,
    InfoReplySerializer,
    InfoReplyResultSerializer,
    ReportPhotoSerializer,
    ReportPhotoUploadSerializer,
    ReportSummarySerializer,
    TokenResponseSerializer,
    CaseRatingResultSerializer,
    CaseRatingSerializer,
    ProposalRatingResultSerializer,
    ProposalSerializer,
)
from lamto.notifications.devices import deactivate_device, register_device
from lamto.notifications.models import NotificationDelivery, NotificationPreference
from lamto.notifications.services import (
    PREFERENCE_EVENT_CHOICES,
    RESIDENT_PUSH_EVENT_CODES,
    mark_notification_read,
    resident_feed,
)

# Logout may deactivate the caller's FCM Device for this install (spec 7.2).
INSTALL_ID_HEADER_PARAMETER = OpenApiParameter(
    name="X-Install-Id",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.HEADER,
    required=False,
    description=(
        "Stable per-install client id. When present on logout, deactivates that "
        "install's FCM Device so push stops for the install. Also accepted as "
        "JSON body field install_id."
    ),
)
from lamto.documents.access import DocumentIntegrityError, read_version_bytes
from lamto.documents.models import DocumentVersion
from lamto.documents.services import DocumentUploadQuarantined, DocumentUploadRejected
from lamto.api.services import (
    INVALID_CREDENTIALS_DETAIL,
    canonicalize_login_identifier,
    log_auth_outcome,
    revoke_tokens_if_no_active_occupancy,
)
from lamto.evidence.models import evidence_level
from lamto.finance.fund import fund_balance
from lamto.finance.models import Proposal
from lamto.finance.selectors import resident_proposals
from lamto.maintenance.ratings import rate_completed_proposal
from lamto.finance.selectors import (
    FUND_SERIES_RANGE_KEYS,
    fund_period_flows,
    fund_series,
    ledger_entry_proof,
    published_ledger_entries,
    published_ledger_entry_for_proof,
)
from lamto.maintenance.models import BuildingLocation, IssueReport, MaintenanceCase
from lamto.maintenance.cases import reply_information
from lamto.maintenance.ratings import rate_completed_case
from lamto.maintenance.reporting import (
    ReportClientRefConflict,
    attach_report_photo,
    submit_report_idempotent,
)
from lamto.maintenance.selectors import (
    active_location_tree,
    resident_report_timeline,
    resident_reports,
)

TOKEN_CAP_PER_USER = 5  # spec 3.2: 5 concurrent tokens; oldest evicted at login


class LoginView(APIView):
    authentication_classes: list = []
    permission_classes = [permissions.AllowAny]

    def get_authenticate_header(self, request):
        # DRF coerces AuthenticationFailed → 403 when no authenticators provide a
        # WWW-Authenticate header. Keep login failures as 401 (clarification 2).
        return 'Token'

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: TokenResponseSerializer,
            **problem_responses(400, 401, 429),
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_identifier = serializer.validated_data["identifier"]
        identifier = canonicalize_login_identifier(raw_identifier)
        ip = client_ip(request)
        try:
            assert_not_throttled(identifier, ip)
        except DjangoPermissionDenied:
            raise exceptions.Throttled(
                detail="Too many authentication attempts. Try again later."
            )
        user = authenticate(
            request,
            username=identifier,
            password=serializer.validated_data["password"],
        )
        if user is None:
            record_auth_failure(identifier, ip, kind="login")
            log_auth_outcome(
                reason="invalid_credentials",
                identifier=identifier,
                ip=ip,
            )
            raise exceptions.AuthenticationFailed(INVALID_CREDENTIALS_DETAIL)
        if not active_occupancies(user).exists():
            # Unified external 401 (clarification 2); distinct internal reason.
            # Count toward the same login throttle as wrong-password failures so
            # correct-password / ineligible accounts cannot oracle around lockout.
            # Revoke any leftover knox tokens (bulk occupancy deactivation bypasses
            # post_save signals; login is the defensive cleanup path).
            record_auth_failure(identifier, ip, kind="login")
            revoke_tokens_if_no_active_occupancy(user)
            log_auth_outcome(
                reason="no_active_occupancy",
                identifier=identifier,
                user_id=user.pk,
                ip=ip,
            )
            raise exceptions.AuthenticationFailed(INVALID_CREDENTIALS_DETAIL)
        reset_auth_throttle(identifier, ip)
        stale = list(AuthToken.objects.filter(user=user).order_by("-created"))[
            TOKEN_CAP_PER_USER - 1 :
        ]
        for old_token in stale:
            old_token.delete()
        instance, token = AuthToken.objects.create(user=user)
        log_auth_outcome(
            reason="success",
            identifier=identifier,
            user_id=user.pk,
            ip=ip,
        )
        return Response(
            TokenResponseSerializer({"token": token, "expiry": instance.expiry}).data
        )


class LogoutView(KnoxLogoutView):
    # Use the resident auth class so spectacular sees one knox scheme only.
    authentication_classes = [ResidentTokenAuthentication]

    @extend_schema(
        parameters=[INSTALL_ID_HEADER_PARAMETER],
        request=LogoutInstallIdSerializer,
        responses={204: None, **problem_responses(401)},
    )
    def post(self, request, format=None):
        install_id = request.headers.get("X-Install-Id") or request.data.get(
            "install_id"
        )
        response = super().post(request, format)
        if install_id:
            deactivate_device(request.user, str(install_id))
        return response


class LogoutAllView(KnoxLogoutAllView):
    authentication_classes = [ResidentTokenAuthentication]

    @extend_schema(
        request=None,
        responses={204: None, **problem_responses(401)},
    )
    def post(self, request, format=None):
        response = super().post(request, format)
        from lamto.notifications.devices import deactivate_user_devices

        deactivate_user_devices(request.user)
        return response


class MeView(APIView):
    @extend_schema(responses={200: MeSerializer, **problem_responses(401, 403)})
    def get(self, request):
        occupancies = list(active_occupancies(request.user))
        if not occupancies:
            raise exceptions.PermissionDenied(
                "An active resident occupancy is required."
            )
        preferences = list(
            request.user.notification_preferences.order_by("event_code").values(
                "event_code", "email_enabled", "push_enabled"
            )
        )
        data = {
            "display_name": request.user.display_name,
            "email": request.user.email,
            "phone": request.user.phone,
            "occupancies": [
                {
                    "id": occupancy.pk,
                    "unit_label": occupancy.unit.label,
                    "building_name": occupancy.unit.building.name,
                }
                for occupancy in occupancies
            ],
            "notification_preferences": preferences,
        }
        return Response(MeSerializer(data).data)


class MeNotificationPreferencesView(APIView):
    """PATCH resident email/push preferences per event code (Flutter Account)."""

    @extend_schema(
        request=NotificationPreferenceUpdateSerializer,
        responses={
            200: NotificationPreferenceSerializer(many=True),
            **problem_responses(400, 401, 403),
        },
    )
    def patch(self, request):
        if not active_occupancies(request.user).exists():
            raise exceptions.PermissionDenied(
                "An active resident occupancy is required."
            )
        serializer = NotificationPreferenceUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        allowed_codes = {code for code, _label in PREFERENCE_EVENT_CHOICES}
        # Validate all items before writing so a bad row cannot partially apply.
        updates = []
        for item in serializer.validated_data["preferences"]:
            code = item["event_code"]
            if code not in allowed_codes:
                raise exceptions.ValidationError(
                    {"preferences": [f"Unknown event_code: {code}"]}
                )
            defaults = {}
            if "email_enabled" in item:
                defaults["email_enabled"] = bool(item["email_enabled"])
            if "push_enabled" in item:
                if code not in RESIDENT_PUSH_EVENT_CODES:
                    raise exceptions.ValidationError(
                        {
                            "preferences": [
                                f"push_enabled is not supported for event_code: {code}"
                            ]
                        }
                    )
                defaults["push_enabled"] = bool(item["push_enabled"])
            updates.append((code, defaults))
        with transaction.atomic():
            for code, defaults in updates:
                NotificationPreference.objects.update_or_create(
                    user=request.user, event_code=code, defaults=defaults
                )
        preferences = list(
            request.user.notification_preferences.order_by("event_code").values(
                "event_code", "email_enabled", "push_enabled"
            )
        )
        return Response(NotificationPreferenceSerializer(preferences, many=True).data)


class LedgerCursorPagination(pagination.CursorPagination):
    page_size = 20  # spec 3.1
    ordering = ("-published_at", "-pk")


@extend_schema_view(
    get=extend_schema(
        parameters=[LedgerFilterSerializer, OCCUPANCY_HEADER_PARAMETER],
        responses={
            200: LedgerEntryListSerializer,
            **problem_responses(400, 401, 403, 404, 422),
        },
    ),
)
class LedgerListView(generics.ListAPIView):
    serializer_class = LedgerEntryListSerializer
    pagination_class = LedgerCursorPagination

    def get_queryset(self):
        filters = LedgerFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)
        _occupancy, tenant = resolve_api_occupancy(self.request)
        entries = published_ledger_entries(tenant.building_id)
        year = filters.validated_data.get("year")
        month = filters.validated_data.get("month")
        if year is not None:
            entries = entries.filter(published_at__year=year)
        if month is not None:
            entries = entries.filter(published_at__month=month)
        return entries


class LedgerDetailView(APIView):
    @extend_schema(
        parameters=[OCCUPANCY_HEADER_PARAMETER],
        responses={
            200: LedgerEntryDetailSerializer,
            **problem_responses(401, 403, 404, 422),
        },
    )
    def get(self, request, pk):
        _occupancy, tenant = resolve_api_occupancy(request)
        entry = published_ledger_entry_for_proof(tenant.building_id, pk)
        if entry is None:
            raise exceptions.NotFound("Published ledger entry not found.")
        detail = ledger_entry_proof(entry)
        verification = detail["verification"]
        data = {
            "id": entry.pk,
            "contractor_name": entry.contractor_name,
            "actual_cost_vnd": entry.actual_cost_vnd,
            "published_at": entry.published_at,
            "proposed_amount_vnd": detail["proposed_amount"],
            "integrity_status": entry.effective_integrity_status,
            "what_was_fixed": detail["what_was_fixed"],
            "why": detail["why"],
            "payload": detail["payload"],
            "verification": (
                {
                    "decision": verification.decision,
                    "verified_by": verification.membership.user.display_name,
                    "verified_at": verification.verified_at,
                }
                if verification is not None
                else None
            ),
            "approvers": [],
            "corrections": [],
            "documents": [
                {
                    **doc,
                    "download_url": reverse(
                        "api:document-download",
                        args=[issue_download_token(request.user.pk, doc["version_id"])],
                    ),
                }
                for doc in detail["docs"]
            ],
            "proof": {
                "evidence_level": detail["evidence_level"],
                "anchoring_backend": settings.EVIDENCE_ANCHORING_BACKEND,
                "payload_hash": detail["settlement"]["payload_hash"],
                "events": [
                    {
                        "event_id": event.event_id,
                        "event_type": event.event_type,
                        "status": event.status,
                        "evidence_level": evidence_level(event.status),
                        "transaction_hash": event.transaction_hash,
                    }
                    for event in detail["events"]
                ],
                "proposal_version": detail["proposal_version"],
                "settlement": detail["settlement"],
            },
        }
        return Response(LedgerEntryDetailSerializer(data).data)


class FundSummaryView(APIView):
    @extend_schema(
        parameters=[OCCUPANCY_HEADER_PARAMETER],
        responses={
            200: FundSummarySerializer,
            **problem_responses(401, 403, 404, 422),
        },
    )
    def get(self, request):
        _occupancy, tenant = resolve_api_occupancy(request)
        inflows, outflows = fund_period_flows(tenant.building_id)
        data = {
            "balance_vnd": fund_balance(tenant.building_id, verified_only=True),
            "period_days": 30,
            "period_inflows_vnd": inflows,
            "period_outflows_vnd": outflows,
        }
        return Response(FundSummarySerializer(data).data)


class FundSeriesView(APIView):
    @extend_schema(
        parameters=[
            OCCUPANCY_HEADER_PARAMETER,
            OpenApiParameter(
                name="range",
                type=OpenApiTypes.STR,
                description="Chart range: 30d, 6m, or 12m. Defaults to 6m.",
            ),
        ],
        responses={
            200: FundSeriesSerializer,
            **problem_responses(400, 401, 403, 404, 422),
        },
    )
    def get(self, request):
        _occupancy, tenant = resolve_api_occupancy(request)
        range_key = request.query_params.get("range", "6m")
        if range_key not in FUND_SERIES_RANGE_KEYS:
            raise exceptions.ValidationError(
                {"range": f"must be one of {', '.join(FUND_SERIES_RANGE_KEYS)}"}
            )
        data = {
            "range": range_key,
            "points": fund_series(tenant.building_id, range_key=range_key),
        }
        return Response(FundSeriesSerializer(data).data)


class ReportCursorPagination(pagination.CursorPagination):
    page_size = 20
    ordering = ("-created_at", "-pk")


@extend_schema_view(
    post=extend_schema(
        parameters=[OCCUPANCY_HEADER_PARAMETER],
        request=ReportCreateSerializer,
        responses={
            201: ReportSummarySerializer,
            200: ReportSummarySerializer,
            **problem_responses(400, 401, 403, 404, 409, 422),
        },
    ),
)
class ReportListCreateView(generics.ListCreateAPIView):
    serializer_class = ReportSummarySerializer
    pagination_class = ReportCursorPagination

    def get_queryset(self):
        return resident_reports(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = ReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        occupancy, tenant = resolve_api_occupancy(request)
        location = BuildingLocation.objects.filter(
            pk=serializer.validated_data["location_id"],
            building_id=tenant.building_id,
            active=True,
        ).first()
        if location is None:
            raise exceptions.ValidationError(
                {"location_id": "Unknown active location for this building."}
            )
        try:
            report, created = submit_report_idempotent(
                request.user,
                occupancy.unit,
                serializer.validated_data["text"],
                location,
                [],
                serializer.validated_data["client_ref"],
                serializer.validated_data["is_private"],
            )
        except ReportClientRefConflict:
            raise problems.ClientRefConflict()
        except DjangoValidationError as error:
            raise exceptions.ValidationError(error.messages)
        except DjangoPermissionDenied:
            raise exceptions.PermissionDenied(
                "An active resident occupancy is required."
            )
        return Response(
            ReportSummarySerializer(report).data,
            status=201 if created else 200,
        )


class ReportDetailView(APIView):
    @extend_schema(responses={200: ReportDetailSerializer, **problem_responses(401, 403, 404)})
    def get(self, request, pk):
        report = (
            IssueReport.objects.select_related("unit", "triage_job", "triage_decision")
            .filter(pk=pk, reporter=request.user)
            .first()
        )
        if report is None:
            raise exceptions.NotFound("Report not found.")
        timeline = resident_report_timeline(report)
        for photo in timeline["photos"]:
            photo["download_url"] = reverse(
                "api:document-download",
                args=[issue_download_token(request.user.pk, photo["id"])],
            )
        return Response(ReportDetailSerializer(timeline).data)


class ReportInfoReplyView(APIView):
    @extend_schema(
        description=(
            "Step 1 of the resident's needs-info reply: commit the text. Text-only "
            "by design so a dropped connection can never lose the words; the client "
            "then attaches any photos one by one via POST /api/v1/reports/{id}/photos. "
            "A successful reply resolves the open information request and moves the "
            "report from NEEDS_INFO back to IN_REVIEW (photo uploads are not "
            "status-gated, so step 2 still works after the flip)."
        ),
        request=InfoReplySerializer,
        responses={200: InfoReplyResultSerializer, **problem_responses(400, 401, 403, 404)},
    )
    def post(self, request, pk):
        report = IssueReport.objects.filter(pk=pk, reporter=request.user).first()
        if report is None:
            raise exceptions.NotFound("Report not found.")
        serializer = InfoReplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            reply_information(request.user, report, serializer.validated_data["text"])
        except DjangoValidationError as error:
            raise exceptions.ValidationError(error.messages)
        except DjangoPermissionDenied:
            raise exceptions.PermissionDenied("Only the reporter may reply.")
        report.refresh_from_db(fields=["status"])
        return Response({"report_id": report.pk, "status": report.status})


class ReportPhotoUploadView(APIView):
    parser_classes = [parsers.MultiPartParser]

    @extend_schema(
        description=(
            "Attach one photo to a report the caller submitted (active occupancy in "
            "the report's building required). There is no report-status gate, so this "
            "also serves as step 2 of the needs-info reply choreography, after "
            "POST /api/v1/reports/{id}/info-reply commits the text. Uploads are "
            "virus-scanned before storage and idempotent per report by content "
            "SHA-256: replaying the same file returns 200 with the existing photo "
            "instead of creating a duplicate (201), so per-photo retries are safe."
        ),
        request=ReportPhotoUploadSerializer,
        responses={
            201: ReportPhotoSerializer,
            200: ReportPhotoSerializer,
            **problem_responses(400, 401, 403, 404),
        },
    )
    def post(self, request, pk):
        report = IssueReport.objects.filter(pk=pk, reporter=request.user).first()
        if report is None:
            raise exceptions.NotFound("Report not found.")
        serializer = ReportPhotoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            version, created = attach_report_photo(
                request.user, report, serializer.validated_data["photo"]
            )
        except (DocumentUploadRejected, DocumentUploadQuarantined) as error:
            raise exceptions.ValidationError({"photo": str(error)})
        except DjangoValidationError as error:
            raise exceptions.ValidationError(error.messages)
        except DjangoPermissionDenied:
            raise exceptions.PermissionDenied("Active occupancy in the report building is required.")
        download_url = reverse(
            "api:document-download",
            args=[issue_download_token(request.user.pk, version.pk)],
        )
        return Response(
            ReportPhotoSerializer(
                {
                    "id": version.pk,
                    "filename": version.filename,
                    "sha256": version.sha256,
                    "download_url": download_url,
                }
            ).data,
            status=201 if created else 200,
        )


class DocumentDownloadView(APIView):
    @extend_schema(responses={200: OpenApiTypes.BINARY, **problem_responses(401, 403, 404)})
    def get(self, request, token):
        try:
            payload = signing.loads(token, salt=DOWNLOAD_SALT, max_age=DOWNLOAD_MAX_AGE)
        except signing.BadSignature:
            raise exceptions.NotFound("Document not found.")
        if payload.get("u") != request.user.pk:
            raise exceptions.NotFound("Document not found.")
        version = (
            DocumentVersion.objects.select_related("document").filter(pk=payload.get("v")).first()
        )
        if version is None or not resident_can_download(request.user, version):
            raise exceptions.NotFound("Document not found.")
        try:
            data = read_version_bytes(version)
        except DocumentIntegrityError:
            raise exceptions.NotFound("Document not found.")
        response = HttpResponse(data, content_type=version.content_type)
        response["Cache-Control"] = "private, no-store"
        response["Content-Disposition"] = content_disposition_inline(version.filename)
        return response


class CaseRatingView(APIView):
    @extend_schema(
        request=CaseRatingSerializer,
        responses={201: CaseRatingResultSerializer, **problem_responses(400, 401, 403, 404)},
    )
    def post(self, request, pk):
        # Scope to a case the caller reported; do not reveal other tenants' cases.
        case = (
            MaintenanceCase.objects.filter(pk=pk, case_reports__report__reporter=request.user)
            .distinct()
            .first()
        )
        if case is None:
            raise exceptions.NotFound("Case not found.")
        serializer = CaseRatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            rating = rate_completed_case(
                request.user, case, serializer.validated_data["satisfied"],
                serializer.validated_data.get("comment", ""),
            )
        except DjangoValidationError as error:
            raise exceptions.ValidationError(error.messages)
        except DjangoPermissionDenied:
            raise exceptions.PermissionDenied("Only residents who reported this case may rate the work.")
        return Response(CaseRatingResultSerializer(
            {"id": rating.pk, "case_id": case.pk, "satisfied": rating.satisfied}
        ).data, status=201)


class ProposalCursorPagination(pagination.CursorPagination):
    page_size = 20
    ordering = ("-created_at", "-pk")


@extend_schema_view(
    get=extend_schema(
        operation_id="proposal_list",
        parameters=[OCCUPANCY_HEADER_PARAMETER],
        responses={
            200: ProposalSerializer,
            **problem_responses(401, 403, 404, 422),
        },
    )
)
class ProposalListView(generics.ListAPIView):
    serializer_class = ProposalSerializer
    pagination_class = ProposalCursorPagination

    def get_queryset(self):
        _occupancy, tenant = resolve_api_occupancy(self.request)
        return resident_proposals(tenant.building_id, self.request.user)


class ProposalDetailView(APIView):
    @extend_schema(operation_id="proposal_detail", parameters=[OCCUPANCY_HEADER_PARAMETER], responses={200: ProposalSerializer, **problem_responses(401, 403, 404, 422)})
    def get(self, request, pk):
        _occupancy, tenant = resolve_api_occupancy(request)
        proposal = resident_proposals(tenant.building_id, request.user).filter(pk=pk).first()
        if proposal is None:
            raise exceptions.NotFound("Proposal not found.")
        return Response(ProposalSerializer(proposal, context={"request": request}).data)


class ProposalRatingView(APIView):
    @extend_schema(parameters=[OCCUPANCY_HEADER_PARAMETER], request=CaseRatingSerializer, responses={201: ProposalRatingResultSerializer,
                   **problem_responses(400, 401, 403, 404)})
    def post(self, request, pk):
        _occupancy, tenant = resolve_api_occupancy(request)
        proposal = Proposal.objects.filter(pk=pk, building_id=tenant.building_id, case__isnull=True).first()
        if proposal is None:
            raise exceptions.NotFound("Proposal not found.")
        serializer = CaseRatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            rating = rate_completed_proposal(request.user, proposal,
                serializer.validated_data["satisfied"], serializer.validated_data.get("comment", ""))
        except DjangoValidationError as error:
            raise exceptions.ValidationError(error.messages)
        except DjangoPermissionDenied:
            raise exceptions.PermissionDenied("Active occupancy in the building is required.")
        return Response(ProposalRatingResultSerializer(
            {"id": rating.pk, "proposal_id": proposal.pk, "satisfied": rating.satisfied}
        ).data, status=201)


class LocationListView(APIView):
    @extend_schema(
        parameters=[OCCUPANCY_HEADER_PARAMETER],
        responses={200: LocationSerializer(many=True), **problem_responses(401, 403, 404, 422)},
    )
    def get(self, request):
        _occupancy, tenant = resolve_api_occupancy(request)
        locations = active_location_tree(tenant.building_id)
        return Response(LocationSerializer(locations, many=True).data)


class NotificationCursorPagination(pagination.CursorPagination):
    page_size = 20
    ordering = ("-created_at", "-pk")


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationFeedSerializer
    pagination_class = NotificationCursorPagination

    @extend_schema(
        parameters=[NotificationFilterSerializer, OCCUPANCY_HEADER_PARAMETER],
        responses={200: NotificationFeedSerializer(many=True), **problem_responses(401, 403, 404, 422)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        filters = NotificationFilterSerializer(data=self.request.query_params.dict())
        filters.is_valid(raise_exception=True)
        _occupancy, tenant = resolve_api_occupancy(self.request)
        queryset = resident_feed(self.request.user, tenant.building_id)
        event_code = filters.validated_data.get("event_code")
        if event_code:
            queryset = queryset.filter(event_code=event_code)
        if "unread" in filters.validated_data:
            queryset = queryset.filter(read_at__isnull=filters.validated_data["unread"])
        return queryset


class NotificationReadView(APIView):
    @extend_schema(request=None, responses={204: None, **problem_responses(401, 403, 404)})
    def post(self, request, pk):
        delivery = NotificationDelivery.objects.filter(
            pk=pk, recipient=request.user, channel=NotificationDelivery.Channel.IN_APP
        ).first()
        if delivery is None:
            raise exceptions.NotFound("Notification not found.")
        mark_notification_read(request.user, pk)
        return Response(status=204)


class DeviceRegisterView(APIView):
    @extend_schema(
        request=DeviceRegisterSerializer,
        responses={200: DeviceSerializer, **problem_responses(400, 401)},
    )
    def post(self, request):
        serializer = DeviceRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device = register_device(
            request.user,
            serializer.validated_data["install_id"],
            serializer.validated_data["fcm_token"],
            serializer.validated_data["platform"],
            serializer.validated_data.get("app_version", ""),
        )
        return Response(
            DeviceSerializer(
                {
                    "install_id": device.install_id,
                    "platform": device.platform,
                    "active": device.active,
                }
            ).data
        )


class DeviceDeleteView(APIView):
    @extend_schema(request=None, responses={204: None, **problem_responses(401)})
    def delete(self, request, install_id):
        deactivate_device(request.user, install_id)
        return Response(status=drf_status.HTTP_204_NO_CONTENT)
