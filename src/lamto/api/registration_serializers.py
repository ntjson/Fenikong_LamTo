from django.core.validators import validate_email
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from lamto.accounts.models import RegistrationRequest


@extend_schema_field(OpenApiTypes.STR)
class RegistrationEmailField(serializers.CharField):
    pass


class RegistrationUnitSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    label = serializers.CharField()


class RegistrationBuildingSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    units = RegistrationUnitSerializer(many=True)


class RegistrationCreateSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=32)
    email = RegistrationEmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    building_id = serializers.IntegerField()
    unit_id = serializers.IntegerField()

    def validate_email(self, value):
        if value:
            validate_email(value)
        return value


class RegistrationSubmissionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=RegistrationRequest.Status.choices)
    status_token = serializers.CharField()
    phone = serializers.CharField()


class RegistrationStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=RegistrationRequest.Status.choices)
    phone = serializers.CharField()
    building = serializers.CharField()
    unit = serializers.CharField()
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
