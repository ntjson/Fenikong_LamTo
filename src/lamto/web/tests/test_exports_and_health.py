"""Auditor exports, formula neutralization, and ops health/metrics."""

from __future__ import annotations

import csv
import io
import time

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex

from lamto.accounts.models import BackupMarker, Building, ManagementMembership
from lamto.accounts.security import RECENT_REAUTH_KEY
from lamto.audit.models import AuditEvent
from lamto.audit.services import record_audit
from lamto.web.views.exports import neutralize_cell


class ExportsAndHealthTests(TestCase):
    def _unique(self, base):
        n = getattr(self, "_seq", 0) + 1
        self._seq = n
        return f"{base}-{n}"

    def make_membership(self, suffix, *, building=None, management=True):
        building = building or self.building
        suffix = self._unique(suffix)
        user = get_user_model().objects.create_user(
            email=f"{suffix}@example.test",
            password="secret-pass-123",
            display_name=suffix,
        )
        if management:
            return ManagementMembership.objects.create(user=user, building=building)
        return user

    def enroll_and_bind(self, user):
        device = TOTPDevice.objects.create(
            user=user, name="test", confirmed=True, key=random_hex()
        )
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session[RECENT_REAUTH_KEY] = time.time()
        session.save()
        return device

    def setUp(self):
        self.building = Building.objects.create(name=self._unique("Export Building"))
        self.auditor = self.make_membership("auditor")
        self.resident = self.make_membership("resident", management=False)
        self.tech = self.make_membership("tech")

    def test_neutralize_spreadsheet_formula_prefixes(self):
        self.assertEqual(neutralize_cell("=CMD()"), "'=CMD()")
        self.assertEqual(neutralize_cell("+1234"), "'+1234")
        self.assertEqual(neutralize_cell("-1+1"), "'-1+1")
        self.assertEqual(neutralize_cell("@SUM(A1)"), "'@SUM(A1)")
        self.assertEqual(neutralize_cell("normal text"), "normal text")
        self.assertEqual(neutralize_cell(None), "")

    def test_auditor_export_streams_csv_and_audits_success(self):
        record_audit(
            self.auditor.user,
            self.auditor,
            "test.action",
            "Thing",
            "1",
            "accepted",
            {"note": "=HACK()"},
        )
        self.client.force_login(self.auditor.user)
        self.enroll_and_bind(self.auditor.user)
        response = self.client.get(reverse("web:audit-export"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])
        body = b"".join(response.streaming_content).decode("utf-8")
        reader = csv.reader(io.StringIO(body))
        rows = list(reader)
        self.assertGreaterEqual(len(rows), 2)
        self.assertEqual(rows[0][0], "id")
        # Success audited
        self.assertTrue(
            AuditEvent.objects.filter(
                action="audit.export", result="accepted", actor=self.auditor.user
            ).exists()
        )
        # No raw private key material markers in export body
        self.assertNotIn("private_key", body.lower())
        self.assertNotIn("bank_account", body.lower())

    def test_non_management_export_denied(self):
        self.client.force_login(self.resident)
        self.enroll_and_bind(self.resident)
        response = self.client.get(reverse("web:audit-export"))
        self.assertEqual(response.status_code, 403)

    def test_export_document_kind_has_hash_columns_not_bytes(self):
        self.client.force_login(self.auditor.user)
        self.enroll_and_bind(self.auditor.user)
        response = self.client.get(reverse("web:audit-export") + "?kind=documents")
        self.assertEqual(response.status_code, 200)
        body = b"".join(response.streaming_content).decode("utf-8")
        header = next(csv.reader(io.StringIO(body)))
        self.assertIn("sha256", header)
        self.assertNotIn("raw_bytes", header)
        self.assertNotIn("storage_body", header)

    def test_health_requires_management(self):
        self.client.force_login(self.tech.user)
        self.enroll_and_bind(self.tech.user)
        response = self.client.get(reverse("web:ops-health") + "?format=json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for key in (
            "queue_age_seconds",
            "queue_count",
            "quarantined_files",
            "notification_failures",
            "push_failures",
            "push_sent_success",
            "push_suppressed",
            "dead_devices",
            "stale_device_max_inactive_days",
            "outbox_status_counts",
            "last_confirmed_block",
            "latest_backup_marker",
            "integrity_mismatches",
        ):
            self.assertIn(key, data)
        # No document content or private keys
        blob = str(data).lower()
        self.assertNotIn("private_key", blob)
        self.assertNotIn("document_content", blob)

    def test_health_includes_backup_marker(self):
        BackupMarker.objects.create(
            marker_id="m1",
            signed_at=timezone.now(),
            signature="abc",
            storage_key="ops/backups/markers/m1.json",
            metadata={"object_count": 0},
        )
        self.client.force_login(self.tech.user)
        self.enroll_and_bind(self.tech.user)
        data = self.client.get(reverse("web:ops-health") + "?format=json").json()
        self.assertIsNotNone(data["latest_backup_marker"])
        self.assertEqual(data["latest_backup_marker"]["marker_id"], "m1")

    def test_health_push_metric_values_from_seeded_rows(self):
        """Ops push metrics reflect real delivery/device state, not key presence alone."""
        from datetime import timedelta

        from django.contrib.auth import get_user_model

        from lamto.notifications.models import Device, NotificationDelivery
        from lamto.notifications.services import EVENT_PUBLICATION, PUSH_SUPPRESSED_PREFIX
        from lamto.web.views.health import collect_health_snapshot

        user = get_user_model().objects.create_user(
            email=self._unique("push-ops") + "@example.test",
            password="x",
            display_name="Push Ops",
        )
        ManagementMembership.objects.create(user=user, building=self.building)
        now = timezone.now()
        # True FCM success
        NotificationDelivery.objects.create(
            recipient=user,
            building=self.building,
            channel=NotificationDelivery.Channel.PUSH,
            status=NotificationDelivery.Status.SENT,
            event_key=f"{EVENT_PUBLICATION}:entry:ok",
            event_code=EVENT_PUBLICATION,
            subject="s",
            body="b",
            last_error="",
        )
        # Suppressed (not FCM success)
        NotificationDelivery.objects.create(
            recipient=user,
            building=self.building,
            channel=NotificationDelivery.Channel.PUSH,
            status=NotificationDelivery.Status.SENT,
            event_key=f"{EVENT_PUBLICATION}:entry:cap",
            event_code=EVENT_PUBLICATION,
            subject="s",
            body="b",
            last_error=f"{PUSH_SUPPRESSED_PREFIX}daily_cap",
        )
        # Failure
        NotificationDelivery.objects.create(
            recipient=user,
            building=self.building,
            channel=NotificationDelivery.Channel.PUSH,
            status=NotificationDelivery.Status.FAILED,
            event_key=f"{EVENT_PUBLICATION}:entry:fail",
            event_code=EVENT_PUBLICATION,
            subject="s",
            body="b",
            last_error="transient",
        )
        # Inactive device unseen for 40 days → max inactive age ≥ 40
        Device.objects.create(
            user=user,
            install_id="stale-install",
            fcm_token="stale-tok",
            platform=Device.Platform.ANDROID,
            active=False,
            last_seen_at=now - timedelta(days=40),
        )
        # Active device must not inflate dead_devices
        Device.objects.create(
            user=user,
            install_id="live-install",
            fcm_token="live-tok",
            platform=Device.Platform.IOS,
            active=True,
            last_seen_at=now,
        )

        snap = collect_health_snapshot(self.building.pk)
        self.assertEqual(snap["push_sent_success"], 1)
        self.assertEqual(snap["push_suppressed"], 1)
        self.assertEqual(snap["push_failures"], 1)
        self.assertEqual(snap["dead_devices"], 1)
        self.assertGreaterEqual(snap["stale_device_max_inactive_days"], 40)

        self.client.force_login(self.tech.user)
        self.enroll_and_bind(self.tech.user)
        data = self.client.get(reverse("web:ops-health") + "?format=json").json()
        self.assertEqual(data["push_sent_success"], snap["push_sent_success"])
        self.assertEqual(data["push_suppressed"], snap["push_suppressed"])
        self.assertEqual(data["push_failures"], snap["push_failures"])
        self.assertEqual(data["dead_devices"], snap["dead_devices"])
        self.assertEqual(
            data["stale_device_max_inactive_days"], snap["stale_device_max_inactive_days"]
        )

    def test_pilot_metrics_non_authoritative(self):
        self.client.force_login(self.tech.user)
        self.enroll_and_bind(self.tech.user)
        response = self.client.get(reverse("web:pilot-metrics") + "?format=json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["authoritative"])
        self.assertIn("ai_suggestion_accepted", data)
        self.assertIn("triage_latency_ms_avg", data)

    def test_health_and_pilot_metrics_exclude_other_building_rows(self):
        from lamto.accounts.models import Unit
        from lamto.maintenance.models import (
            BuildingLocation,
            IssueReport,
            TriageJob,
            TriageSuggestion,
        )
        from lamto.notifications.models import NotificationDelivery
        from lamto.web.views.health import collect_health_snapshot, collect_pilot_metrics

        other = Building.objects.create(name=self._unique("Other Building"))
        other_user = self.make_membership("other-manager", building=other).user
        NotificationDelivery.objects.create(
            recipient=other_user,
            building=other,
            event_key="other:failed",
            channel=NotificationDelivery.Channel.PUSH,
            status=NotificationDelivery.Status.FAILED,
            subject="s",
            body="b",
        )
        unit = Unit.objects.create(building=other, label="1A")
        location = BuildingLocation.objects.create(building=other, name="Lobby")
        report = IssueReport.objects.create(
            reporter=other_user,
            unit=unit,
            text="x",
            selected_location=location,
            location_path_snapshot="Other / Lobby",
        )
        job = TriageJob.objects.create(report=report)
        TriageSuggestion.objects.create(
            job=job,
            category="x",
            interpreted_location="Lobby",
            urgency="LOW",
            confidence_percent=90,
            department="x",
            deadline_minutes=60,
            raw_response={},
            provider_request_id="other",
            elapsed_ms=999,
        )

        self.assertEqual(collect_health_snapshot(self.building.pk)["push_failures"], 0)
        self.assertEqual(collect_pilot_metrics(self.building.pk)["ai_suggestions_total"], 0)
        self.client.force_login(self.tech.user)
        self.enroll_and_bind(self.tech.user)
        health = self.client.get(reverse("web:ops-health") + "?format=json").json()
        metrics = self.client.get(reverse("web:pilot-metrics") + "?format=json").json()
        self.assertEqual(health["push_failures"], 0)
        self.assertEqual(metrics["ai_suggestions_total"], 0)

    def test_backup_objects_command_filesystem_mode(self):
        from django.core.management import call_command
        from io import StringIO
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            manifest = os.path.join(tmp, "manifest.json")
            out = StringIO()
            with override_settings(
                STORAGES={
                    "default": {
                        "BACKEND": "django.core.files.storage.FileSystemStorage",
                        "OPTIONS": {"location": tmp},
                    },
                    "private": {
                        "BACKEND": "django.core.files.storage.FileSystemStorage",
                        "OPTIONS": {"location": tmp},
                    },
                    "staticfiles": {
                        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
                    },
                }
            ):
                os.environ["LAMTO_BACKUP_ALLOW_FS"] = "1"
                try:
                    call_command(
                        "backup_objects",
                        dest_prefix="object-backups",
                        manifest_path=manifest,
                        stdout=out,
                    )
                finally:
                    os.environ.pop("LAMTO_BACKUP_ALLOW_FS", None)
            self.assertTrue(os.path.isfile(manifest))
            self.assertTrue(BackupMarker.objects.exists())
            # restore dry structural path
            out2 = StringIO()
            os.environ["LAMTO_BACKUP_ALLOW_FS"] = "1"
            try:
                with override_settings(
                    STORAGES={
                        "default": {
                            "BACKEND": "django.core.files.storage.FileSystemStorage",
                            "OPTIONS": {"location": tmp},
                        },
                        "private": {
                            "BACKEND": "django.core.files.storage.FileSystemStorage",
                            "OPTIONS": {"location": tmp},
                        },
                        "staticfiles": {
                            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
                        },
                    }
                ):
                    call_command(
                        "restore_object_backup",
                        manifest=manifest,
                        dest_prefix="restore-drill",
                        dry_run=True,
                        stdout=out2,
                    )
            finally:
                os.environ.pop("LAMTO_BACKUP_ALLOW_FS", None)
            self.assertIn("restore_object_backup", out2.getvalue())
