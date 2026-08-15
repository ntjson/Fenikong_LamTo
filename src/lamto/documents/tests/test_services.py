import io
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from lamto.accounts.models import Building, ManagementMembership
from lamto.documents.models import Document
from lamto.documents.services import DocumentUploadRejected, create_document_version


_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
    b"\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00"
    b"\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


@override_settings(
    STORAGES={
        "private": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": tempfile.gettempdir() + "/lamto-document-tests"},
        }
    }
)
class DocumentServiceTests(TestCase):
    def make_manager_and_bill(self):
        building = Building.objects.create(name="Tower A")
        manager = get_user_model().objects.create_user(email="m@x.test", password="pw")
        ManagementMembership.objects.create(user=manager, building=building)
        return manager, Document.objects.create(
            building=building, kind=Document.Kind.RESIDENT_BILL
        )

    def test_resident_bill_accepts_pdf_jpeg_and_png(self):
        manager, document = self.make_manager_and_bill()
        jpeg = io.BytesIO()
        Image.new("RGB", (1, 1)).save(jpeg, format="JPEG")

        for filename, content_type, content in (
            ("bill.pdf", "application/pdf", b"%PDF-1.7\nbill"),
            ("bill.jpg", "image/jpeg", jpeg.getvalue()),
            ("bill.png", "image/png", _PNG),
        ):
            with self.subTest(content_type=content_type):
                version = create_document_version(
                    document,
                    SimpleUploadedFile(filename, content, content_type=content_type),
                    manager,
                    scanner=lambda _: True,
                )

                self.assertEqual(version.content_type, content_type)

    def test_resident_bill_rejects_other_content_types(self):
        manager, document = self.make_manager_and_bill()

        with self.assertRaises(DocumentUploadRejected):
            create_document_version(
                document,
                SimpleUploadedFile("bill.txt", b"bill", content_type="text/plain"),
                manager,
                scanner=lambda _: True,
            )
