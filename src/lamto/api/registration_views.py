from django.core.exceptions import PermissionDenied
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import exceptions, serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from lamto.accounts.backends import normalize_phone
from lamto.accounts.models import Building, RegistrationRequest, Unit
from lamto.accounts.registration import (
    RegistrationConflict,
    get_registration_status,
    submit_registration,
)
from lamto.accounts.security import record_registration_attempt
from lamto.api.problems import RegistrationConflictProblem, problem_responses
from lamto.api.registration_serializers import (
    RegistrationBuildingSerializer,
    RegistrationCreateSerializer,
    RegistrationStatusSerializer,
    RegistrationSubmissionSerializer,
)


STATUS_TOKEN_HEADER = OpenApiParameter(
    name="X-Registration-Status-Token",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.HEADER,
    required=True,
)


class PublicRegistrationView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]


class RegistrationOptionsView(PublicRegistrationView):
    @extend_schema(
        operation_id="registration_options",
        tags=["registration"],
        responses={200: RegistrationBuildingSerializer(many=True)},
    )
    def get(self, request):
        buildings = Building.objects.prefetch_related("unit_set").order_by("id")
        data = [
            {
                "id": building.id,
                "name": building.name,
                "units": [
                    {"id": unit.id, "label": unit.label}
                    for unit in building.unit_set.all().order_by("id")
                ],
            }
            for building in buildings
        ]
        return Response(RegistrationBuildingSerializer(data, many=True).data)


class RegistrationCreateView(PublicRegistrationView):
    @extend_schema(
        operation_id="registration_create",
        tags=["registration"],
        request=RegistrationCreateSerializer,
        responses={
            201: RegistrationSubmissionSerializer,
            **problem_responses(400, 409, 429),
        },
    )
    def post(self, request):
        ip = (request.META.get("REMOTE_ADDR") or "").strip()
        try:
            record_registration_attempt("registration-ip", ip)
        except PermissionDenied:
            raise exceptions.Throttled(
                detail="Too many registration attempts. Try again later."
            )

        raw_data = request.data
        raw_phone = raw_data.get("phone") if hasattr(raw_data, "get") else None
        normalized_phone = normalize_phone(raw_phone) if isinstance(raw_phone, str) else None
        if normalized_phone is not None:
            phone_key = f"registration-phone:{normalized_phone}"
            try:
                record_registration_attempt(phone_key, None)
            except PermissionDenied:
                raise exceptions.Throttled(
                    detail="Too many registration attempts. Try again later."
                )

        serializer = RegistrationCreateSerializer(data=raw_data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if not Unit.objects.filter(
            pk=data["unit_id"], building_id=data["building_id"]
        ).exists():
            raise serializers.ValidationError(
                {"unit_id": "Unit does not belong to the selected building."}
            )
        try:
            submission = submit_registration(**data)
        except RegistrationConflict:
            raise RegistrationConflictProblem()
        output = {
            "status": submission.request.status,
            "status_token": submission.status_token,
            "phone": submission.request.phone,
        }
        return Response(
            RegistrationSubmissionSerializer(output).data,
            status=status.HTTP_201_CREATED,
        )


class RegistrationStatusView(PublicRegistrationView):
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Cache-Control"] = "private, no-store"
        return response

    @extend_schema(
        operation_id="registration_status",
        tags=["registration"],
        parameters=[STATUS_TOKEN_HEADER],
        responses={200: RegistrationStatusSerializer, **problem_responses(400, 404)},
    )
    def get(self, request):
        token = request.headers.get("X-Registration-Status-Token")
        if not token:
            raise serializers.ValidationError(
                {"X-Registration-Status-Token": "This header is required."}
            )
        try:
            registration = get_registration_status(token)
        except RegistrationRequest.DoesNotExist:
            raise exceptions.NotFound()
        data = {
            "status": registration.status,
            "phone": registration.phone,
            "building": registration.building.name,
            "unit": registration.unit.label,
        }
        if registration.status == RegistrationRequest.Status.REJECTED:
            data["rejection_reason"] = registration.rejection_reason
        return Response(RegistrationStatusSerializer(data).data)
