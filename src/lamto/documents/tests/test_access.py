import hashlib
import io
import tempfile
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.files.storage import storages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from lamto.accounts.models import Building, ManagementMembership, ResidentOccupancy, Unit
from lamto.audit.models import AuditEvent
from lamto.documents.access import DocumentIntegrityError, authorize_download
from lamto.documents.models import Document, DocumentVersion
from lamto.documents.services import create_document_version


@override_settings(
    STORAGES={
        "private": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": tempfile.gettempdir() + "/lamto-document-tests"},
        }
    }
)
class DocumentAccessTests(TestCase):
    def make_management(self, building=None, suffix="management"):
        building = building or Building.objects.create(name=f"Building {suffix}")
        user = get_user_model().objects.create_user(
            email=f"{suffix}-{get_user_model().objects.count()}@example.test",
            password="secret",
            display_name=suffix,
        )
        return user, ManagementMembership.objects.create(user=user, building=building)

    def make_version(self, uploader, building, payload=b"%PDF-1.7\nprivate"):
        return create_document_version(
            Document.objects.create(building=building, kind=Document.Kind.QUOTATION),
            SimpleUploadedFile("quote.pdf", payload, content_type="application/pdf"),
            uploader,
            scanner=lambda _: True,
        )

    def test_management_can_download_document_in_its_building(self):
        manager, membership = self.make_management()
        version = self.make_version(manager, membership.building)

        self.assertEqual(authorize_download(manager, membership.id, version), b"%PDF-1.7\nprivate")
        self.assertEqual(AuditEvent.objects.last().result, "allowed")

    def test_management_cannot_download_document_in_another_building(self):
        uploader, uploader_membership = self.make_management(suffix="uploader")
        outsider, outsider_membership = self.make_management(suffix="outsider")
        version = self.make_version(uploader, uploader_membership.building)

        with self.assertRaises(PermissionDenied):
            authorize_download(outsider, outsider_membership.id, version)

        audit = AuditEvent.objects.last()
        self.assertEqual(audit.result, "denied")
        self.assertEqual(audit.membership_id, outsider_membership.id)

    def test_resident_can_download_document_in_occupied_building(self):
        manager, membership = self.make_management()
        resident = get_user_model().objects.create_user(
            email="resident@example.test", password="secret", display_name="Resident"
        )
        occupancy = ResidentOccupancy.objects.create(
            user=resident, unit=Unit.objects.create(building=membership.building, label="A-1")
        )
        version = self.make_version(manager, membership.building)

        self.assertEqual(authorize_download(resident, None, version), b"%PDF-1.7\nprivate")
        audit = AuditEvent.objects.last()
        self.assertIsNone(audit.membership_id)
        self.assertEqual(audit.metadata["occupancy_id"], occupancy.id)

    def test_unaffiliated_user_is_denied_and_audited(self):
        manager, membership = self.make_management()
        user = get_user_model().objects.create_user(
            email="unaffiliated@example.test", password="secret", display_name="Other"
        )
        version = self.make_version(manager, membership.building)

        with self.assertRaises(PermissionDenied):
            authorize_download(user, None, version)

        self.assertEqual(AuditEvent.objects.last().result, "denied")

    def test_hash_mismatch_is_audited(self):
        manager, membership = self.make_management()
        version = self.make_version(manager, membership.building)
        with storages["private"].open(version.storage_key, "wb") as file_obj:
            file_obj.write(b"tampered")

        with self.assertRaises(DocumentIntegrityError):
            authorize_download(manager, membership.id, version)

        self.assertEqual(AuditEvent.objects.last().result, "integrity_mismatch")

    @patch("lamto.documents.access.storages")
    def test_download_reads_exact_provider_version(self, private_storages):
        manager, membership = self.make_management()
        payload = b"%PDF-1.7\nprivate"
        version = DocumentVersion.objects.create(
            document=Document.objects.create(
                building=membership.building, kind=Document.Kind.QUOTATION
            ),
            version=1,
            storage_key="documents/immutable-key",
            provider_version_id="provider-version-42",
            filename="quote.pdf",
            content_type="application/pdf",
            byte_size=len(payload),
            sha256=hashlib.sha256(payload).hexdigest(),
            uploader=manager,
        )
        storage = MagicMock(bucket_name="private")
        storage.connection.meta.client.get_object.return_value = {"Body": io.BytesIO(payload)}
        private_storages.__getitem__.return_value = storage

        self.assertEqual(authorize_download(manager, membership.id, version), payload)
        storage.connection.meta.client.get_object.assert_called_once_with(
            Bucket="private", Key=version.storage_key, VersionId="provider-version-42"
        )

    @patch("lamto.documents.access.storages")
    def test_s3_read_without_provider_version_fails_closed(self, private_storages):
        manager, membership = self.make_management()
        payload = b"%PDF-1.7\nprivate"
        version = DocumentVersion.objects.create(
            document=Document.objects.create(
                building=membership.building, kind=Document.Kind.QUOTATION
            ),
            version=1,
            storage_key="documents/missing-version-id",
            provider_version_id="",
            filename="quote.pdf",
            content_type="application/pdf",
            byte_size=len(payload),
            sha256=hashlib.sha256(payload).hexdigest(),
            uploader=manager,
        )
        storage = MagicMock(bucket_name="private")
        private_storages.__getitem__.return_value = storage

        with self.assertRaises(DocumentIntegrityError):
            authorize_download(manager, membership.id, version)
        storage.connection.meta.client.get_object.assert_not_called()
