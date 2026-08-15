from rest_framework import serializers


class VehiclePlateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    plate = serializers.CharField()
    status = serializers.CharField()
    submitted_at = serializers.DateTimeField()
    review_note = serializers.CharField(allow_blank=True)


class FaceEnrollmentSerializer(serializers.Serializer):
    status = serializers.CharField()
    submitted_at = serializers.DateTimeField()
    review_note = serializers.CharField(allow_blank=True)


class GateRegistrationsSerializer(serializers.Serializer):
    face = FaceEnrollmentSerializer(allow_null=True)
    plates = VehiclePlateSerializer(many=True)


class PlateCreateSerializer(serializers.Serializer):
    plate = serializers.CharField(max_length=32)


class FaceUploadSerializer(serializers.Serializer):
    photo = serializers.FileField()


class RecognitionOutcomeSerializer(serializers.Serializer):
    matched = serializers.BooleanField()
    display_name = serializers.CharField(allow_blank=True)
    unit_label = serializers.CharField(allow_blank=True)
    direction = serializers.CharField()
    score = serializers.FloatField(allow_null=True)


class GateDeviceSerializer(serializers.Serializer):
    label = serializers.CharField()
    direction = serializers.ChoiceField(choices=["ENTRY", "EXIT"])


class PlateRecognizeSerializer(serializers.Serializer):
    plate = serializers.CharField(max_length=64)


class FaceRecognizeSerializer(serializers.Serializer):
    photo = serializers.FileField()
