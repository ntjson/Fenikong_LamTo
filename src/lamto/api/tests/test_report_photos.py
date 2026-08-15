import tempfile
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection, IntegrityError
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from knox.models import AuthToken

from lamto.documents.models import DocumentVersion
from lamto.maintenance.models import ReportPhoto
from lamto.maintenance.reporting import attach_report_photo, submit_report_idempotent
from lamto.testing.factories import seed_pilot_world

_TEMP = tempfile.mkdtemp(prefix="lamto-api-photos-")
_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
    b"\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00"
    b"\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)

_STORAGES = {
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


@override_settings(STORAGES=_STORAGES)
class ReportPhotoUploadTests(TestCase):
    def setUp(self):
        self.seed = seed_pilot_world(
            building_name="API Photos B", email_prefix="apip", create_sample_report=False
        )
        self.resident = self.seed.residents[0]
        self.report, _ = submit_report_idempotent(
            self.resident, self.seed.unit, "Lift jerks", self.seed.location, [], uuid.uuid4()
        )

    def _auth(self, user=None):
        _instance, token = AuthToken.objects.create(user=user or self.resident)
        return {"authorization": f"Token {token}"}

    @patch("lamto.maintenance.reporting.scan_with_clamav", lambda _f: True)
    def test_upload_attaches_photo_to_own_report(self):
        resp = self.client.post(
            reverse("api:report-photos", kwargs={"pk": self.report.pk}),
            data={"photo": SimpleUploadedFile("p.png", _PNG, content_type="image/png")},
            headers=self._auth(),
        )
        assert resp.status_code == 201, resp.content
        assert ReportPhoto.objects.filter(report=self.report).count() == 1
        assert resp.json()["sha256"]
        photo = ReportPhoto.objects.get(report=self.report)
        assert photo.content_sha == resp.json()["sha256"]

    @patch("lamto.maintenance.reporting.scan_with_clamav", lambda _f: True)
    def test_same_bytes_replay_returns_200_without_duplicate(self):
        """Amendment 10: lost-response retry with identical content is idempotent."""
        url = reverse("api:report-photos", kwargs={"pk": self.report.pk})
        auth = self._auth()
        first = self.client.post(
            url,
            data={"photo": SimpleUploadedFile("p.png", _PNG, content_type="image/png")},
            headers=auth,
        )
        assert first.status_code == 201, first.content
        second = self.client.post(
            url,
            data={"photo": SimpleUploadedFile("p.png", _PNG, content_type="image/png")},
            headers=auth,
        )
        assert second.status_code == 200, second.content
        assert ReportPhoto.objects.filter(report=self.report).count() == 1
        assert second.json()["id"] == first.json()["id"]
        assert second.json()["sha256"] == first.json()["sha256"]

    @patch("lamto.maintenance.reporting.scan_with_clamav", lambda _f: True)
    def test_locked_recheck_prevents_duplicate_when_precheck_misses(self):
        """TOCTOU: unlocked pre-check misses an already-inserted same-hash row."""
        attach_report_photo(
            self.resident,
            self.report,
            SimpleUploadedFile("p.png", _PNG, content_type="image/png"),
        )
        assert ReportPhoto.objects.filter(report=self.report).count() == 1
        versions_before = DocumentVersion.objects.count()

        real_select_related = ReportPhoto.objects.select_related
        state = {"calls": 0}

        class _Qs:
            def __init__(self, real, force_empty_first):
                self._real = real
                self._force_empty = force_empty_first

            def filter(self, *args, **kwargs):
                return _Qs(self._real.filter(*args, **kwargs), self._force_empty)

            def first(self):
                if self._force_empty:
                    return None
                return self._real.first()

        def select_related_proxy(*args, **kwargs):
            state["calls"] += 1
            real_qs = real_select_related(*args, **kwargs)
            return _Qs(real_qs, force_empty_first=(state["calls"] == 1))

        with patch.object(
            ReportPhoto.objects, "select_related", side_effect=select_related_proxy
        ):
            _version, created = attach_report_photo(
                self.resident,
                self.report,
                SimpleUploadedFile("p.png", _PNG, content_type="image/png"),
            )

        assert created is False
        assert ReportPhoto.objects.filter(report=self.report).count() == 1
        # Version create runs only after lock recheck — no orphan on miss path.
        assert DocumentVersion.objects.count() == versions_before
        assert state["calls"] >= 2

    @patch("lamto.maintenance.reporting.scan_with_clamav", lambda _f: True)
    def test_content_sha_unique_rejects_second_row(self):
        """DB unique(report, content_sha) blocks double insert of same hash."""
        _, created = attach_report_photo(
            self.resident,
            self.report,
            SimpleUploadedFile("p.png", _PNG, content_type="image/png"),
        )
        assert created is True
        photo = ReportPhoto.objects.get(report=self.report)
        # Attempt a second row with a different version but same content_sha.
        from lamto.documents.models import Document, DocumentVersion

        doc = Document.objects.create(
            building=self.report.building, kind=Document.Kind.REPORT_PHOTO
        )
        v2 = DocumentVersion.objects.create(
            document=doc,
            version=1,
            filename="dup.png",
            content_type="image/png",
            byte_size=len(_PNG),
            sha256=photo.content_sha,
            storage_key=f"dup/{uuid.uuid4().hex}",
            provider_version_id="v-dup",
            scan_status=DocumentVersion.ScanStatus.CLEAN,
            uploader=self.resident,
        )
        with self.assertRaises(IntegrityError):
            ReportPhoto.objects.create(
                report=self.report, version=v2, content_sha=photo.content_sha
            )

    @patch("lamto.maintenance.reporting.scan_with_clamav", lambda _f: True)
    def test_upload_to_foreign_report_is_404(self):
        from django.contrib.auth import get_user_model
        from lamto.accounts.models import ResidentOccupancy

        stranger = get_user_model().objects.create_user(
            email="apip-x@example.com", password="x", display_name="X"
        )
        ResidentOccupancy.objects.create(user=stranger, unit=self.seed.unit, active=True)
        resp = self.client.post(
            reverse("api:report-photos", kwargs={"pk": self.report.pk}),
            data={"photo": SimpleUploadedFile("p.png", _PNG, content_type="image/png")},
            headers=self._auth(stranger),
        )
        assert resp.status_code == 404


@override_settings(STORAGES=_STORAGES)
class ReportPhotoConcurrentAttachTests(TransactionTestCase):
    """Real multi-thread same-bytes attach; fixtures committed across connections.

    Skips TRUNCATE flush (append-only document triggers) like DeviceRegistryRaceTests.
    """

    def _fixture_teardown(self):
        pass

    def setUp(self):
        self.seed = seed_pilot_world(
            building_name="API Photos Conc", email_prefix="apipc", create_sample_report=False
        )
        self.resident = self.seed.residents[0]
        self.report, _ = submit_report_idempotent(
            self.resident, self.seed.unit, "Lift jerks", self.seed.location, [], uuid.uuid4()
        )

    @patch("lamto.maintenance.reporting.scan_with_clamav", lambda _f: True)
    def test_concurrent_same_bytes_attach_yields_one_row_no_orphan_version(self):
        versions_before = DocumentVersion.objects.count()
        barrier = threading.Barrier(2)
        results = []

        def worker():
            connection.close()
            barrier.wait(timeout=10)
            try:
                version, created = attach_report_photo(
                    self.resident,
                    self.report,
                    SimpleUploadedFile("p.png", _PNG, content_type="image/png"),
                )
                return version.pk, created
            finally:
                connection.close()

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(worker) for _ in range(2)]
            for fut in as_completed(futures):
                results.append(fut.result())

        assert ReportPhoto.objects.filter(report=self.report).count() == 1
        created_flags = [c for _, c in results]
        assert created_flags.count(True) == 1
        assert created_flags.count(False) == 1
        # Exactly one new DocumentVersion from the race (winner only).
        assert DocumentVersion.objects.count() == versions_before + 1
        linked_ids = set(
            ReportPhoto.objects.filter(report=self.report).values_list("version_id", flat=True)
        )
        assert len(linked_ids) == 1
