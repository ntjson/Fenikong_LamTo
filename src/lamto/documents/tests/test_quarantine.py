import tempfile
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import storages
from django.test import TestCase, override_settings
from django.utils import timezone

from lamto.accounts.models import Building, ManagementMembership
from lamto.audit.models import AuditEvent
from lamto.documents.models import Document, DocumentVersion, QuarantinedUpload
from lamto.documents.scanner import DocumentScanUnavailable, scan_with_clamav
from lamto.documents.services import (
    DocumentUploadRejected,
    DocumentUploadQuarantined,
    create_document_version,
    purge_expired_quarantine,
)


@override_settings(
    STORAGES={
        "private": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": tempfile.gettempdir() + "/lamto-document-tests"},
        }
    }
)
class QuarantineTests(TestCase):
    def setUp(self):
        self.uploader = get_user_model().objects.create_user(
            email="operator@example.test", password="secret", display_name="Operator"
        )
        self.building = Building.objects.create(name="Minh An Residence")
        ManagementMembership.objects.create(user=self.uploader, building=self.building)
        self.document = Document.objects.create(
            building=self.building, kind=Document.Kind.QUOTATION
        )

    def test_type_rejection_keeps_no_bytes_and_is_audited(self):
        with self.assertRaises(DocumentUploadRejected):
            create_document_version(
                self.document,
                SimpleUploadedFile("quote.txt", b"not-a-pdf", content_type="text/plain"),
                self.uploader,
                scanner=lambda _: True,
            )

        quarantined = QuarantinedUpload.objects.get()
        self.assertIsNone(quarantined.storage_key)
        self.assertEqual(DocumentVersion.objects.count(), 0)
        self.assertEqual(AuditEvent.objects.get().action, "document.upload_rejected")

    @override_settings(DOCUMENT_MAX_UPLOAD_BYTES=1)
    def test_size_rejection_keeps_no_bytes(self):
        with self.assertRaises(DocumentUploadRejected):
            create_document_version(
                self.document,
                SimpleUploadedFile("quote.pdf", b"%PDF-1.7\\ntoo-large", content_type="application/pdf"),
                self.uploader,
                scanner=lambda _: True,
            )

        self.assertIsNone(QuarantinedUpload.objects.get().storage_key)

    def test_invalid_png_signature_is_rejected_without_storage(self):
        photo = Document.objects.create(building=self.building, kind=Document.Kind.REPORT_PHOTO)
        with self.assertRaises(DocumentUploadRejected):
            create_document_version(
                photo,
                SimpleUploadedFile("photo.png", b"\\x89PNG\\r\\n\\x1a\\nbroken", content_type="image/png"),
                self.uploader,
                scanner=lambda _: True,
            )

        self.assertIsNone(QuarantinedUpload.objects.get().storage_key)

    def test_malware_and_scanner_failure_keep_bytes_in_quarantine(self):
        payload = b"%PDF-1.7\\nmalware"
        for scanner in (lambda _: False, lambda _: (_ for _ in ()).throw(DocumentScanUnavailable())):
            with self.assertRaises(DocumentUploadQuarantined):
                create_document_version(
                    self.document,
                    SimpleUploadedFile("quote.pdf", payload, content_type="application/pdf"),
                    self.uploader,
                    scanner=scanner,
                )

        self.assertEqual(QuarantinedUpload.objects.count(), 2)
        self.assertTrue(all(upload.storage_key.startswith("quarantine/") for upload in QuarantinedUpload.objects.all()))
        self.assertEqual(DocumentVersion.objects.count(), 0)
        self.assertEqual(AuditEvent.objects.filter(action="document.upload_quarantined").count(), 2)

    @override_settings(DOCUMENT_QUARANTINE_RETENTION_DAYS=7)
    def test_quarantine_has_a_fixed_retention_deadline(self):
        with self.assertRaises(DocumentUploadQuarantined):
            create_document_version(
                self.document,
                SimpleUploadedFile("quote.pdf", b"%PDF-1.7\\nmalware", content_type="application/pdf"),
                self.uploader,
                scanner=lambda _: False,
            )

        quarantined = QuarantinedUpload.objects.get()
        self.assertLessEqual(
            abs((quarantined.retention_expires_at - timezone.now() - timedelta(days=7)).total_seconds()),
            1,
        )

    @override_settings(DOCUMENT_QUARANTINE_RETENTION_DAYS=0)
    def test_expired_quarantine_bytes_are_purged_but_its_row_is_retained(self):
        with self.assertRaises(DocumentUploadQuarantined):
            create_document_version(
                self.document,
                SimpleUploadedFile("quote.pdf", b"%PDF-1.7\\nmalware", content_type="application/pdf"),
                self.uploader,
                scanner=lambda _: False,
            )

        quarantined = QuarantinedUpload.objects.get()
        self.assertEqual(purge_expired_quarantine(timezone.now() + timedelta(seconds=1)), 1)
        self.assertFalse(storages["private"].exists(quarantined.storage_key))
        self.assertTrue(QuarantinedUpload.objects.filter(pk=quarantined.pk).exists())

    @patch("lamto.documents.services.storages")
    def test_expired_s3_quarantine_deletes_the_recorded_provider_version(self, private_storages):
        client = MagicMock()
        storage = SimpleNamespace(
            bucket_name="private",
            connection=SimpleNamespace(meta=SimpleNamespace(client=client)),
            delete=MagicMock(),
        )
        private_storages.__getitem__.return_value = storage
        upload = QuarantinedUpload.objects.create(
            uploader=self.uploader,
            filename="rejected.pdf",
            content_type="application/pdf",
            byte_size=1,
            sha256="",
            reason="malware detected",
            storage_key="quarantine/object-key",
            provider_version_id="provider-version-42",
            retention_expires_at=timezone.now(),
        )

        self.assertEqual(purge_expired_quarantine(timezone.now() + timedelta(seconds=1)), 1)
        client.delete_object.assert_called_once_with(
            Bucket="private", Key=upload.storage_key, VersionId=upload.provider_version_id
        )

    @patch("lamto.documents.scanner.socket.create_connection")
    def test_clamav_instream_accepts_only_ok(self, create_connection):
        connection = create_connection.return_value.__enter__.return_value
        connection.recv.return_value = b"stream: OK\x00"

        payload = b"%PDF-1.7\\nprivate"
        upload = SimpleUploadedFile("quote.pdf", payload)
        self.assertTrue(scan_with_clamav(upload))
        self.assertEqual(connection.sendall.call_count, 3)
        self.assertEqual(connection.sendall.call_args_list[1].args[0][4:], payload)

        connection.recv.return_value = b"stream: FOUND\x00"
        self.assertFalse(scan_with_clamav(SimpleUploadedFile("quote.pdf", payload)))
