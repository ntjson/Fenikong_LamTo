import tempfile
import time
from types import SimpleNamespace
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex

from lamto.accounts.security import RECENT_REAUTH_KEY
from lamto.documents.models import DocumentVersion
from lamto.finance.models import MaintenanceFundEntry, PublishedLedgerEntry
from lamto.finance.selectors import pending_reconciliation_proposals
from lamto.testing.factories import PilotDomainDriver, seed_pilot_world

_TEMP = tempfile.mkdtemp(prefix="lamto-fundops-")


def _pdf(name, body):
    return SimpleUploadedFile(name, b"%PDF-1.4\n" + body, content_type="application/pdf")


def _full_publish(seed):
    """Run the pilot expenditure through verified payment (not yet published)."""
    d = PilotDomainDriver(seed)
    d.submit_report("Lift noise", "Lift 2")
    d.confirm_triage_case()
    d.publish_proposal()
    d.complete_assigned_work()
    d.record_settlement_transfer()
    d.record_settlement_ack()
    d.confirm_all_chain_events()
    return d


@override_settings(
    ROOT_URLCONF="lamto.config.urls",
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _TEMP}},
        "private": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _TEMP}},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    },
)
class FundSelectorTests(TestCase):
    def test_pending_reconciliation_lists_paid_but_unpublished(self):
        seed = seed_pilot_world(building_name="Fund Sel B", email_prefix="fs")
        _full_publish(seed)  # verified payment, settled chain, no publication yet
        pending = list(pending_reconciliation_proposals(seed.building.pk))
        self.assertEqual(pending, [])

    def test_pending_reconciliation_excludes_unsettled_verification(self):
        """Eligibility matches domain gates: settled prerequisites required, not only VERIFIED."""
        from lamto.evidence.models import BlockchainOutboxEvent

        seed = seed_pilot_world(building_name="Fund Sel Unsettled", email_prefix="fsu")
        _full_publish(seed)
        v_event = seed.proposal.settlement.outbox_event
        # QUEUED is not a status in this codebase; PENDING is non-settled.
        BlockchainOutboxEvent.objects.filter(pk=v_event.pk).update(
            status=BlockchainOutboxEvent.Status.PENDING
        )
        pending = list(pending_reconciliation_proposals(seed.building.pk))
        self.assertEqual(pending, [])

    def test_pending_fund_verification_is_not_verified_fund_entries(self):
        from lamto.finance.selectors import (
            pending_fund_verification_entries,
            verified_fund_entries,
        )
        seed = seed_pilot_world(building_name="Fund Sel Pend", email_prefix="fsp")
        verified_ids = {e.pk for e in verified_fund_entries(seed.building.pk)}
        pending_ids = {e.pk for e in pending_fund_verification_entries(seed.building.pk)}
        self.assertTrue(verified_ids.isdisjoint(pending_ids))

@override_settings(
    ROOT_URLCONF="lamto.config.urls",
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _TEMP}},
        "private": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _TEMP}},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    },
)
class FundHomeTests(TestCase):
    def test_pending_fund_row_can_publish_from_proposal_detail(self):
        seed = seed_pilot_world(building_name="Publish Recovery B", email_prefix="pr")
        driver = PilotDomainDriver(seed)
        driver.submit_report("Lift noise", "Lift 2")
        driver.confirm_triage_case()
        driver.publish_proposal()
        driver.complete_assigned_work()
        driver.record_settlement_transfer()
        with patch("lamto.finance.publication.publish_settlement_entry"):
            driver.record_settlement_ack()
        driver.confirm_all_chain_events()
        self._login(seed, "fund_recorder")

        fund = self.client.get(reverse("web:fund-home"))
        detail_url = reverse("web:proposal-detail", args=[seed.proposal.pk])
        self.assertContains(fund, detail_url)
        detail = self.client.get(detail_url)
        self.assertContains(detail, 'name="action" value="publish"', html=False)

        response = self.client.post(detail_url, {"action": "publish", "confirm": "on"})

        self.assertRedirects(response, detail_url)
        self.assertTrue(PublishedLedgerEntry.objects.filter(proposal=seed.proposal).exists())
    @patch("lamto.web.views.fund.fund_series", return_value=[])
    def test_new_building_fund_home_handles_empty_series(self, _series):
        seed = seed_pilot_world(building_name="Empty Fund B", email_prefix="ef", create_opening_fund=False)
        self._login(seed, "fund_recorder")

        response = self.client.get(reverse("web:fund-home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["window_closing_vnd"], 0)
    def _login(self, seed, role_key):
        membership = seed.management_memberships[0]
        self.client.force_login(membership.user)
        device = TOTPDevice.objects.create(
            user=membership.user, name="t", confirmed=True, key=random_hex()
        )
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session[RECENT_REAUTH_KEY] = time.time()
        session["active_management_id"] = membership.pk
        session.save()
        return membership

    def test_fund_home_shows_balance_entries_and_pending(self):
        seed = seed_pilot_world(building_name="Fund Home B", email_prefix="fh")
        _full_publish(seed)
        self._login(seed, "fund_recorder")
        resp = self.client.get(reverse("web:fund-home"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Quỹ bảo trì")           # Maintenance fund
        self.assertContains(resp, "<h2>Bút toán đã xác minh</h2>")  # Verified entries
        # The seeded opening balance is a verified entry.
        self.assertContains(resp, "Số dư đầu kỳ")          # Opening balance

    def test_verified_fund_rows_lead_with_record_state(self):
        seed = seed_pilot_world(building_name="Fund Row B", email_prefix="fhr")
        self._login(seed, "fund_recorder")

        resp = self.client.get(reverse("web:fund-home"))

        self.assertContains(resp, '<span class="task-action">Bút toán đã xác minh</span>')

    @patch("lamto.web.views.fund.pending_fund_verification_entries")
    @patch("lamto.web.views.fund.pending_reconciliation_proposals")
    def test_pending_proposals_render_once(self, pending_proposals, pending_entries):
        seed = seed_pilot_world(building_name="Fund Pending B", email_prefix="fhp")
        pending_proposals.return_value = [
            SimpleNamespace(
                pk=7,
                current_version=SimpleNamespace(amount_vnd=250_000),
            )
        ]
        pending_entries.return_value = [
            SimpleNamespace(
                pk=8,
                amount_vnd=100_000,
                get_entry_type_display=lambda: "Inflow",
                recorded_at=timezone.now(),
            )
        ]
        self._login(seed, "fund_recorder")

        resp = self.client.get(reverse("web:fund-home"))

        self.assertEqual(resp.content.count("Chuẩn bị công bố".encode()), 1)

    def test_fund_home_renders_chart_and_window_stats(self):
        seed = seed_pilot_world(building_name="Fund Chart B", email_prefix="fch")
        self._login(seed, "fund_recorder")
        resp = self.client.get(reverse("web:fund-home"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'id="fund-chart-data"')
        self.assertContains(resp, "Số dư đầu kỳ")   # Opening balance
        self.assertContains(resp, "Số dư cuối kỳ")  # Closing balance
        self.assertContains(resp, "Tổng thu")       # Total inflows
        self.assertContains(resp, "Tổng chi")       # Total outflows
        self.assertEqual(resp.context["chart_range"], "6m")
        self.assertEqual(len(resp.context["chart_points"]), 6)
        first = resp.context["chart_points"][0]
        self.assertIsInstance(first["period_start"], str)

    def test_fund_home_range_toggle_and_fallback(self):
        seed = seed_pilot_world(building_name="Fund Chart R", email_prefix="fcr")
        self._login(seed, "fund_recorder")
        resp = self.client.get(reverse("web:fund-home"), {"range": "30d"})
        self.assertEqual(len(resp.context["chart_points"]), 30)
        resp = self.client.get(reverse("web:fund-home"), {"range": "bogus"})
        self.assertEqual(resp.context["chart_range"], "6m")

    def test_fund_home_window_stats_reconcile(self):
        seed = seed_pilot_world(building_name="Fund Chart S", email_prefix="fcs")
        self._login(seed, "fund_recorder")
        ctx = self.client.get(reverse("web:fund-home")).context
        self.assertEqual(
            ctx["window_opening_vnd"]
            + ctx["window_inflows_vnd"]
            + ctx["window_outflows_vnd"],
            ctx["window_closing_vnd"],
        )

    def test_management_can_open_fund_home(self):
        seed = seed_pilot_world(building_name="Fund Home Deny", email_prefix="fhd")
        self._login(seed, "maintenance")
        self.assertEqual(self.client.get(reverse("web:fund-home")).status_code, 200)


@override_settings(
    ROOT_URLCONF="lamto.config.urls",
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _TEMP}},
        "private": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _TEMP}},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    },
)
class FundRecordTests(TestCase):
    def _login(self, seed, role_key):
        membership = seed.management_memberships[0]
        self.client.force_login(membership.user)
        device = TOTPDevice.objects.create(
            user=membership.user, name="t", confirmed=True, key=random_hex()
        )
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session[RECENT_REAUTH_KEY] = time.time()
        session["active_management_id"] = membership.pk
        session.save()
        return membership

    @patch("lamto.web.staff_documents.scan_with_clamav", lambda _f: True)
    def test_prepare_then_sign_records_inflow(self):
        seed = seed_pilot_world(building_name="Fund Rec B", email_prefix="fr")
        self._login(seed, "fund_recorder")
        url = reverse("web:fund-record")
        response = self.client.post(
            url,
            {
                "entry_type": MaintenanceFundEntry.EntryType.INFLOW,
                "amount_vnd": 2_000_000,
                "evidence": _pdf("e.pdf", b"orig"),
            },
        )
        self.assertRedirects(response, reverse("web:fund-home"))
        entry = MaintenanceFundEntry.objects.filter(fund__building=seed.building).latest("pk")
        self.assertEqual(entry.entry_type, MaintenanceFundEntry.EntryType.INFLOW)
        self.assertEqual(entry.amount_vnd, 2_000_000)
        self.assertFalse(hasattr(entry, "verification"))

    def test_management_can_open_fund_record(self):
        seed = seed_pilot_world(building_name="Fund Rec Deny", email_prefix="frd")
        self._login(seed, "fund_verifier")  # verify-only cannot record
        self.assertEqual(self.client.get(reverse("web:fund-record")).status_code, 200)


@override_settings(
    ROOT_URLCONF="lamto.config.urls",
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _TEMP}},
        "private": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _TEMP}},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    },
)
class FundVerifyTests(TestCase):
    def _login(self, seed, role_key):
        membership = seed.management_memberships[0]
        self.client.force_login(membership.user)
        device = TOTPDevice.objects.create(
            user=membership.user, name="t", confirmed=True, key=random_hex()
        )
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session[RECENT_REAUTH_KEY] = time.time()
        session["active_management_id"] = membership.pk
        session.save()
        return membership

    def _unverified_entry(self, seed):
        """Record an inflow via the recorder domain path (unverified)."""
        from lamto.finance.fund import (
            get_or_create_fund,
            record_fund_source,
        )
        from lamto.documents.models import Document

        fund = get_or_create_fund(seed.building)
        recorder = seed.management_memberships[0]
        evidence = seed.document(Document.Kind.CONTRACT, recorder.user, "inflow")
        return record_fund_source(
            fund, MaintenanceFundEntry.EntryType.INFLOW, 1_000_000, evidence,
            recorder,
        )

    def test_verifier_signs_and_verifies(self):
        seed = seed_pilot_world(building_name="Fund Ver B", email_prefix="fv")
        entry = self._unverified_entry(seed)
        verifier = self._login(seed, "fund_verifier")
        url = reverse("web:fund-verify", kwargs={"pk": entry.pk})
        resp = self.client.post(url)
        self.assertRedirects(resp, reverse("web:fund-home"))
        entry.refresh_from_db()
        self.assertTrue(hasattr(entry, "verification"))

@override_settings(
    ROOT_URLCONF="lamto.config.urls",
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _TEMP}},
        "private": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _TEMP}},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    },
)
class ActionInboxChartTests(TestCase):
    @patch("lamto.web.views.staff_common.fund_series", return_value=[])
    def test_new_building_inbox_handles_empty_series(self, _series):
        seed = seed_pilot_world(building_name="Empty Inbox B", email_prefix="ei", create_opening_fund=False)
        self._login(seed, "fund_recorder")

        response = self.client.get(reverse("web:action-inbox"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["fund_balance_vnd"], 0)
    def _login(self, seed, role_key):
        membership = seed.management_memberships[0]
        self.client.force_login(membership.user)
        device = TOTPDevice.objects.create(
            user=membership.user, name="t", confirmed=True, key=random_hex()
        )
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session[RECENT_REAUTH_KEY] = time.time()
        session["active_management_id"] = membership.pk
        session.save()
        return membership

    def test_inbox_shows_compact_chart_with_fund_link_for_fund_staff(self):
        seed = seed_pilot_world(building_name="Inbox Chart B", email_prefix="ich")
        self._login(seed, "fund_recorder")
        resp = self.client.get(reverse("web:action-inbox"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'id="fund-chart-data"')
        self.assertContains(resp, 'data-compact="1"')
        self.assertContains(resp, reverse("web:fund-home"))
        self.assertEqual(len(resp.context["fund_chart_points"]), 6)
        self.assertTrue(resp.context["fund_link_ok"])

    def test_inbox_chart_has_fund_link_for_management(self):
        seed = seed_pilot_world(building_name="Inbox Chart D", email_prefix="icd")
        self._login(seed, "maintenance")
        resp = self.client.get(reverse("web:action-inbox"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'id="fund-chart-data"')
        self.assertContains(resp, reverse("web:fund-home"))
        self.assertTrue(resp.context["fund_link_ok"])
