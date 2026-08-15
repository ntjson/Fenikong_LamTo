import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from lamto.accounts.models import Building, ManagementMembership
from lamto.documents.models import QuarantinedUpload
from lamto.documents.services import quarantine_upload

_TEMP_STORAGE = tempfile.mkdtemp(prefix="lamto-quarantine-test-")


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": _TEMP_STORAGE},
        },
        "private": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": _TEMP_STORAGE},
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
)
class QuarantineBuildingTests(TestCase):
    def test_quarantine_upload_stamps_membership_building(self):
        building = Building.objects.create(name="Quarantine Building")
        user = get_user_model().objects.create_user(
            email="q@example.test", password="x", display_name="Q"
        )
        ManagementMembership.objects.create(user=user, building=building)
        upload = SimpleUploadedFile("bad.bin", b"x" * 10, content_type="application/octet-stream")
        quarantined = quarantine_upload(upload, user, "test reason")
        assert quarantined.building_id == building.pk
        assert QuarantinedUpload.objects.get(pk=quarantined.pk).building_id == building.pk
