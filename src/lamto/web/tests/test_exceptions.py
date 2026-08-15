"""Exceptions review surface: list, per-kind review pages, named responses."""

from __future__ import annotations

import secrets
import time
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex

from lamto.accounts.models import Building, ManagementMembership
from lamto.audit.models import AuditEvent
from lamto.documents.models import QuarantinedUpload
from lamto.evidence.models import BlockchainOutboxEvent, EvidenceType
from lamto.evidence.services import queue_platform_event


@override_settings(LANGUAGE_CODE="en-us")  # assertions target English msgids
class ExceptionReviewTests(TestCase):
    def setUp(self):
        self.building = Building.objects.create(name="Exception Building")
        user = get_user_model().objects.create_user(
            email="exceptions-manager@example.test",
            password="secret-pass-123",
            display_name="Bà Quản lý",
        )
        self.membership = ManagementMembership.objects.create(
            user=user, building=self.building
        )
        self.client.force_login(user)
        device = TOTPDevice.objects.create(
            user=user, name="test", confirmed=True, key=random_hex()
        )
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session["recent_reauth_at"] = time.time()
        session.save()

    def _failed_event(self, *, status=BlockchainOutboxEvent.Status.FAILED):
        # Inserts must go through the platform queue procedure (DB trigger);
        # status transitions afterwards mirror what the delivery worker does.
        event = queue_platform_event(
            "0x" + secrets.token_hex(32),
            EvidenceType.PROPOSAL_CREATED,
            {
                "proposal_id": 1,
                "proposal_version": 1,
                "record_id": 1,
                "amount_vnd": 1,
                "proposal_snapshot_hash": "1" * 64,
                "quotation_hash": "2" * 64,
                "building_id": self.building.pk,
            },
            "0x" + "00" * 32,
            self.building,
        )
        BlockchainOutboxEvent.objects.filter(pk=event.pk).update(
            status=status, last_error="RPC unreachable"
        )
        event.refresh_from_db()
        return event

    def _quarantined(self):
        return QuarantinedUpload.objects.create(
            uploader=self.membership.user,
            building=self.building,
            filename="hoa-don.pdf",
            byte_size=123,
            reason="virus signature",
            retention_expires_at=timezone.now() + timedelta(days=7),
        )

    def test_list_groups_failed_anchor_and_quarantine_with_response_state(self):
        event = self._failed_event()
        upload = self._quarantined()
        response = self.client.get(reverse("web:exception-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, reverse("web:exception-review", args=["failed_outbox", event.pk])
        )
        self.assertContains(
            response,
            reverse("web:exception-review", args=["quarantined_upload", upload.pk]),
        )

    def test_inbox_exception_rows_point_at_review_pages(self):
        event = self._failed_event()
        upload = self._quarantined()
        response = self.client.get(reverse("web:action-inbox"))
        self.assertContains(
            response, reverse("web:exception-review", args=["failed_outbox", event.pk])
        )
        self.assertContains(
            response,
            reverse("web:exception-review", args=["quarantined_upload", upload.pk]),
        )
        self.assertNotContains(response, "?outbox=")
        self.assertNotContains(response, "?entry=")

    def test_review_page_records_named_append_only_response(self):
        event = self._failed_event()
        url = reverse("web:exception-review", args=["failed_outbox", event.pk])

        page = self.client.get(url)
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "RPC unreachable")

        response = self.client.post(url, {"note": "Đã kiểm tra RPC; nhà cung cấp xác nhận sự cố."})
        self.assertRedirects(response, url)
        recorded = AuditEvent.objects.get(
            action="exception.review",
            target_type="BlockchainOutboxEvent",
            target_id=str(event.pk),
        )
        self.assertEqual(recorded.metadata["note"], "Đã kiểm tra RPC; nhà cung cấp xác nhận sự cố.")
        self.assertEqual(recorded.actor, self.membership.user)

        followup = self.client.get(url)
        self.assertContains(followup, "Đã kiểm tra RPC")
        self.assertContains(followup, "Bà Quản lý")

    def test_empty_response_is_rejected_without_recording(self):
        event = self._failed_event()
        url = reverse("web:exception-review", args=["failed_outbox", event.pk])
        response = self.client.post(url, {"note": "   "})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            AuditEvent.objects.filter(action="exception.review").exists()
        )

    def test_cleared_failure_states_current_delivery_status(self):
        event = self._failed_event(status=BlockchainOutboxEvent.Status.CONFIRMED)
        response = self.client.get(
            reverse("web:exception-review", args=["failed_outbox", event.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No longer failing")

    def test_unknown_kind_is_a_404(self):
        response = self.client.get(
            reverse("web:exception-review", args=["nonsense", 1])
        )
        self.assertEqual(response.status_code, 404)
