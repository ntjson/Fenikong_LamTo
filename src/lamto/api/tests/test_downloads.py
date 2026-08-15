import logging
import tempfile
import time
import uuid
from datetime import timedelta
from unittest.mock import patch
from urllib.parse import quote, unquote

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from knox.models import AuthToken

from lamto.api.downloads import (
    DOWNLOAD_MAX_AGE,
    content_disposition_inline,
    issue_download_token,
    sanitize_download_filename,
)
from lamto.config.log_filters import DownloadTokenLogFilter, scrub_download_token_in_text
from lamto.accounts.models import ResidentOccupancy
from lamto.documents.models import Document
from lamto.maintenance.cases import publish_progress
from lamto.maintenance.models import CaseReport, MaintenanceCase, ReportPhoto, TriageDecision
from lamto.maintenance.reporting import submit_report_idempotent
from lamto.testing.factories import seed_pilot_world

_TEMP = tempfile.mkdtemp(prefix="lamto-api-dl-")
_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
    b"\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00"
    b"\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


_FS_STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {"location": _TEMP},
    },
    "private": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {"location": _TEMP},
    },
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


class SanitizeDownloadFilenameTests(TestCase):
    """Pure helpers used by DocumentDownloadView disposition headers."""

    def test_strips_crlf_quotes_and_path_components(self):
        assert sanitize_download_filename('a/b\\c\r\n"x".png') == "cx.png"
        assert sanitize_download_filename("") == "download"
        assert sanitize_download_filename(None) == "download"
        assert sanitize_download_filename("  normal.pdf  ") == "normal.pdf"

    def test_content_disposition_has_ascii_and_rfc5987_filename_star(self):
        header = content_disposition_inline("report photo.png")
        assert header.startswith("inline; ")
        assert 'filename="report photo.png"' in header
        assert "filename*=UTF-8''" in header
        assert "report%20photo.png" in header
        starred = header.split("filename*=UTF-8''", 1)[1]
        assert unquote(starred) == sanitize_download_filename("report photo.png")

    def test_content_disposition_encodes_non_ascii_in_filename_star(self):
        name = "hóa đơn.pdf"
        header = content_disposition_inline(name)
        assert "filename*=UTF-8''" in header
        assert "\r" not in header and "\n" not in header
        starred = header.split("filename*=UTF-8''", 1)[1]
        assert unquote(starred) == sanitize_download_filename(name)
        # ASCII fallback must be pure ASCII.
        ascii_part = header.split('filename="', 1)[1].split('"', 1)[0]
        assert ascii_part.encode("ascii")
        # Percent-encoding of non-ASCII is present.
        assert quote(sanitize_download_filename(name), safe="") in header


@override_settings(STORAGES=_FS_STORAGES)
class DownloadTests(TestCase):
    def setUp(self):
        self.seed = seed_pilot_world(building_name="API DL B", email_prefix="apidl", create_sample_report=False)
        self.resident = self.seed.residents[0]
        self.report, _ = submit_report_idempotent(
            self.resident, self.seed.unit, "Lift jerks", self.seed.location, [], uuid.uuid4()
        )

    def _auth(self, user=None):
        _instance, token = AuthToken.objects.create(user=user or self.resident)
        return {"authorization": f"Token {token}"}

    @patch("lamto.maintenance.reporting.scan_with_clamav", lambda _f: True)
    def _upload_photo(self):
        self.client.post(
            reverse("api:report-photos", kwargs={"pk": self.report.pk}),
            data={"photo": SimpleUploadedFile("p.png", _PNG, content_type="image/png")},
            headers=self._auth(),
        )
        return ReportPhoto.objects.get(report=self.report).version

    def _work_update_photo(self):
        manager = self.seed.management_users[0]
        decision = TriageDecision.objects.create(
            report=self.report,
            operator=manager,
            category="Lift",
            urgency="HIGH",
            location=self.seed.location,
            department="Maintenance",
            deadline_minutes=1440,
        )
        case = MaintenanceCase.objects.create(
            decision=decision,
            building=self.seed.building,
            category="Lift",
            urgency="HIGH",
            location=self.seed.location,
            department="Maintenance",
            deadline_at=timezone.now() + timedelta(days=1),
        )
        CaseReport.objects.create(case=case, report=self.report, grouped_by=manager)
        version = self.seed.photo(Document.Kind.BEFORE_PHOTO, manager, "before")
        publish_progress(
            case, manager, "Inspected lift", "Found worn guide", before_versions=[version]
        )
        return version

    def test_own_photo_download_url_streams_bytes(self):
        version = self._upload_photo()
        detail = self.client.get(reverse("api:report-detail", kwargs={"pk": self.report.pk}), headers=self._auth())
        url = detail.json()["photos"][0]["download_url"]
        assert url.startswith("/api/v1/documents/")
        got = self.client.get(url, headers=self._auth())
        assert got.status_code == 200
        assert got["Cache-Control"] == "private, no-store"
        assert got.content == _PNG
        # Happy-path disposition: ASCII filename + RFC 5987 filename*.
        cd = got["Content-Disposition"]
        assert 'filename="p.png"' in cd
        assert "filename*=UTF-8''p.png" in cd

    def test_reported_case_work_update_photo_downloads_for_owner(self):
        version = self._work_update_photo()
        token = issue_download_token(self.resident.pk, version.pk)

        response = self.client.get(
            reverse("api:document-download", args=[token]), headers=self._auth()
        )

        assert response.status_code == 200

    def test_reported_case_work_update_photo_is_denied_to_foreign_resident(self):
        version = self._work_update_photo()
        foreign = get_user_model().objects.create_user(
            email="apidl-foreign@example.com", password="x", display_name="Foreign"
        )
        ResidentOccupancy.objects.create(user=foreign, unit=self.seed.unit, active=True)
        token = issue_download_token(foreign.pk, version.pk)

        response = self.client.get(
            reverse("api:document-download", args=[token]), headers=self._auth(foreign)
        )

        assert response.status_code == 404

    def test_content_disposition_filename_is_sanitized(self):
        """CR/LF/quotes/path components must not appear raw in Content-Disposition.

        DocumentVersion rows are append-only, so the hostile name is set at create.
        """
        import hashlib

        from django.core.files.base import ContentFile
        from django.core.files.storage import storages

        from lamto.documents.models import Document, DocumentVersion

        hostile = 'evil\r\nPath/../../x"inject".png'
        doc = Document.objects.create(
            building=self.seed.building, kind=Document.Kind.REPORT_PHOTO
        )
        data = _PNG
        storage = storages["private"]
        storage_key = f"hostile/{self.report.pk}/p.png"
        storage.save(storage_key, ContentFile(data))
        version = DocumentVersion.objects.create(
            document=doc,
            version=1,
            filename=hostile,
            content_type="image/png",
            byte_size=len(data),
            sha256=hashlib.sha256(data).hexdigest(),
            storage_key=storage_key,
            provider_version_id="v-hostile",
            scan_status=DocumentVersion.ScanStatus.CLEAN,
            uploader=self.resident,
        )
        ReportPhoto.objects.create(
            report=self.report, version=version, content_sha=version.sha256
        )
        token = issue_download_token(self.resident.pk, version.pk)
        got = self.client.get(
            reverse("api:document-download", args=[token]), headers=self._auth()
        )
        assert got.status_code == 200, got.content
        cd = got["Content-Disposition"]
        assert "\r" not in cd and "\n" not in cd
        assert ".." not in cd
        assert "Path" not in cd
        expected = sanitize_download_filename(hostile)
        # Real view uses content_disposition_inline (filename + filename*).
        assert cd == content_disposition_inline(hostile)
        assert f'filename="{expected}"' in cd or 'filename="' in cd
        assert "filename*=UTF-8''" in cd
        starred = cd.split("filename*=UTF-8''", 1)[1]
        assert unquote(starred) == expected
        assert got.content == data

    def test_token_bound_to_user_and_expiry(self):
        version = self._upload_photo()
        # A token minted for this user cannot be redeemed by another user.
        from django.contrib.auth import get_user_model

        from lamto.accounts.models import ResidentOccupancy

        stranger = get_user_model().objects.create_user(email="apidl-x@example.com", password="x", display_name="X")
        ResidentOccupancy.objects.create(user=stranger, unit=self.seed.unit, active=True)
        token = issue_download_token(self.resident.pk, version.pk)
        miss = self.client.get(reverse("api:document-download", args=[token]), headers=self._auth(stranger))
        assert miss.status_code == 404
        # A tampered/garbage token is 404.
        bad = self.client.get(reverse("api:document-download", args=["not-a-real-token"]), headers=self._auth())
        assert bad.status_code == 404

    def test_expired_token_is_404(self):
        """Tokens older than DOWNLOAD_MAX_AGE fail at signing.loads on the real view."""
        version = self._upload_photo()
        past = time.time() - (DOWNLOAD_MAX_AGE + 60)
        with patch("time.time", return_value=past):
            # issue_download_token → signing.dumps embeds the backdated timestamp.
            expired = issue_download_token(self.resident.pk, version.pk)
        # Redeem with real clock: max_age check rejects the aged signature.
        resp = self.client.get(
            reverse("api:document-download", args=[expired]), headers=self._auth()
        )
        assert resp.status_code == 404

    def test_staff_document_is_unreachable(self):
        # Forge a token for a staff-only, non-photo document version;
        # resident_can_download must refuse it -> 404.
        import hashlib

        from lamto.documents.models import Document, DocumentVersion

        doc = Document.objects.create(building=self.seed.building, kind=Document.Kind.INVOICE)
        original = DocumentVersion.objects.create(
            document=doc,
            version=1,
            filename="inv.pdf",
            content_type="application/pdf",
            byte_size=3,
            sha256=hashlib.sha256(b"pdf").hexdigest(),
            storage_key="k",
            provider_version_id="v",
            scan_status=DocumentVersion.ScanStatus.CLEAN,
            uploader=self.resident,
        )
        token = issue_download_token(self.resident.pk, original.pk)
        resp = self.client.get(reverse("api:document-download", args=[token]), headers=self._auth())
        assert resp.status_code == 404

    def test_fund_contract_is_unreachable_even_inside_the_residents_building(self):
        """CONTRACT is fund-source evidence: staff-only, and not merely by
        accident of the reference queries. The allowlist must refuse it before
        any lookup runs."""
        from lamto.api.downloads import RESIDENT_DOWNLOADABLE_KINDS, resident_can_download
        from lamto.documents.models import Document

        resident = self.seed.residents[0]
        manager = self.seed.management_users[0]
        contract = self.seed.document(Document.Kind.CONTRACT, manager, "fund-contract")

        self.assertNotIn(Document.Kind.CONTRACT, RESIDENT_DOWNLOADABLE_KINDS)
        with self.assertNumQueries(0):
            self.assertIs(resident_can_download(resident, contract), False)


class DownloadTokenLogScrubTests(TestCase):
    """Signed download tokens must not appear in formatted log messages (spec 3.6)."""

    def test_scrub_helper_redacts_token_path_segment(self):
        raw = "GET /api/v1/documents/abc.def:ghi 200"
        assert scrub_download_token_in_text(raw) == "GET /api/v1/documents/[redacted] 200"
        assert "abc.def:ghi" not in scrub_download_token_in_text(raw)
        # Non-download paths are unchanged.
        other = "GET /api/v1/reports/12 200"
        assert scrub_download_token_in_text(other) == other

    def test_log_filter_removes_token_from_emitted_message(self):
        token = "signed.token:value-with-parts"
        record = logging.LogRecord(
            name="django.server",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg='"GET /api/v1/documents/%s HTTP/1.1" 200',
            args=(token,),
            exc_info=None,
        )
        assert token in record.getMessage()
        assert DownloadTokenLogFilter().filter(record) is True
        emitted = record.getMessage()
        assert token not in emitted
        assert "/api/v1/documents/[redacted]" in emitted
