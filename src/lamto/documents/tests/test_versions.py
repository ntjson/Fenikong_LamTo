import hashlib
import io
import tempfile
from types import SimpleNamespace
from unittest.mock import MagicMock

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.db import IntegrityError, connection, transaction
from django.utils import timezone

from lamto.accounts.models import Building, ManagementMembership
from lamto.documents.models import Document, DocumentVersion, QuarantinedUpload
from lamto.documents.services import (
    DocumentStorageError,
    _store,
    create_document_version,
)


@override_settings(
    STORAGES={
        "private": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": tempfile.gettempdir() + "/lamto-document-tests"},
        }
    }
)
class DocumentVersionTests(TestCase):
    def make_operator_and_building(self):
        uploader = get_user_model().objects.create_user(
            email="operator@example.test", password="secret", display_name="Operator"
        )
        building = Building.objects.create(name="Minh An Residence")
        ManagementMembership.objects.create(user=uploader, building=building)
        return uploader, building

    def test_a_document_accumulates_versions_and_hashes_are_immutable(self):
        """One upload creates one version — but a document is not capped at one.
        A genuine later revision still inserts version 2."""
        uploader, building = self.make_operator_and_building()
        document = Document.objects.create(building=building, kind=Document.Kind.QUOTATION)
        first_bytes = b"%PDF-1.7\\nfirst-quotation"
        second_bytes = b"%PDF-1.7\\ncorrected-quotation"

        first = create_document_version(
            document,
            SimpleUploadedFile("quote.pdf", first_bytes, content_type="application/pdf"),
            uploader,
            scanner=lambda _: True,
        )
        second = create_document_version(
            document,
            SimpleUploadedFile("quote-v2.pdf", second_bytes, content_type="application/pdf"),
            uploader,
            scanner=lambda _: True,
        )

        self.assertEqual(first.version, 1)
        self.assertEqual(second.version, 2)
        self.assertEqual(first.sha256, hashlib.sha256(first_bytes).hexdigest())
        self.assertNotEqual(first.sha256, second.sha256)
        self.assertNotEqual(first.storage_key, second.storage_key)
        self.assertEqual(first.provider_version_id, first.storage_key)

        first.sha256 = "0" * 64
        with self.assertRaises(ValueError):
            first.save()

    def test_database_trigger_rejects_version_update_and_delete(self):
        uploader, building = self.make_operator_and_building()
        version = create_document_version(
            Document.objects.create(building=building, kind=Document.Kind.QUOTATION),
            SimpleUploadedFile("quote.pdf", b"%PDF-1.7\\nprivate", content_type="application/pdf"),
            uploader,
            scanner=lambda _: True,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            DocumentVersion.objects.filter(pk=version.pk).update(filename="changed.pdf")
        with self.assertRaises(IntegrityError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM documents_documentversion WHERE id = %s", [version.pk])

        with self.assertRaises(IntegrityError), transaction.atomic():
            Document.objects.filter(pk=version.document_id).update(kind=Document.Kind.INVOICE)

    def test_database_trigger_rejects_quarantine_mutation(self):
        uploader, _ = self.make_operator_and_building()
        quarantined = QuarantinedUpload.objects.create(
            uploader=uploader,
            filename="rejected.pdf",
            content_type="application/pdf",
            byte_size=1,
            sha256="",
            reason="unsupported content type",
            retention_expires_at=timezone.now(),
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            QuarantinedUpload.objects.filter(pk=quarantined.pk).update(reason="changed")


@override_settings(LANGUAGE_CODE="en-us")  # asserts English source strings
class StorageVersionTests(TestCase):
    def test_s3_write_without_version_id_fails_closed(self):
        storage = MagicMock(bucket_name="private")
        storage.connection.meta.client.get_bucket_versioning.return_value = {"Status": "Enabled"}
        storage.connection.meta.client.put_object.return_value = {}

        with self.assertRaisesRegex(DocumentStorageError, "VersionId"):
            _store(storage, "documents/immutable-key", io.BytesIO(b"payload"), "application/pdf")

    def test_s3_write_requires_enabled_versioning_and_non_null_version_id(self):
        class FakeS3Client:
            def __init__(self, status, version_id):
                self.status = status
                self.version_id = version_id
                self.put_calls = 0

            def get_bucket_versioning(self, **kwargs):
                return {"Status": self.status} if self.status else {}

            def put_object(self, **kwargs):
                self.put_calls += 1
                return {"VersionId": self.version_id}

        for status, version_id in (
            ("Suspended", "provider-version-42"),
            ("Enabled", ""),
            ("Enabled", "null"),
        ):
            with self.subTest(status=status, version_id=version_id):
                client = FakeS3Client(status, version_id)
                storage = SimpleNamespace(
                    bucket_name="private",
                    connection=SimpleNamespace(
                        meta=SimpleNamespace(client=client)
                    ),
                )

                with self.assertRaises(DocumentStorageError):
                    _store(storage, "documents/immutable-key", io.BytesIO(b"payload"), "application/pdf")

                if status != "Enabled":
                    self.assertEqual(client.put_calls, 0)
