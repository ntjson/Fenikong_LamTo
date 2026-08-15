"""LOCAL_SIGNED never borrows CHAIN_CONFIRMED presentation (spec 5.1/5.2)."""

import tempfile

from django.template.loader import render_to_string
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from lamto.evidence.models import BlockchainOutboxEvent
from lamto.finance.models import PublishedLedgerEntry
from lamto.testing.factories import PilotDomainDriver, seed_pilot_world
from lamto.web.views.exports import _outbox_rows
from lamto.web.views.health import collect_health_snapshot, collect_pilot_metrics

_TEMP_STORAGE = tempfile.mkdtemp(prefix="lamto-evidence-labels-")


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
@override_settings(LANGUAGE_CODE="en-us")  # asserts English source strings
class EvidenceLevelLabelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.seed = seed_pilot_world(
            building_name="Label Building", create_sample_report=False
        )
        driver = PilotDomainDriver(cls.seed)
        driver.prepare_local_normal_work(None)
        driver.complete_assigned_work()
        driver.record_settlement()
        driver.confirm_all_chain_events()
        driver.publish_settlement_entry()
        driver.confirm_all_chain_events()
        cls.entry = PublishedLedgerEntry.objects.get(case__building=cls.seed.building)


    def _proposal_event_ids(self):
        version = self.entry.proposal.current_version
        return [version.outbox_event_id]

    def test_staff_label_is_three_way(self):
        version = self.entry.proposal.current_version
        self.assertEqual(version.verification_label, "Chain confirmed")

        BlockchainOutboxEvent.objects.filter(pk__in=self._proposal_event_ids()).update(
            status=BlockchainOutboxEvent.Status.LOCAL, confirmed_at=None
        )
        version.outbox_event.refresh_from_db()
        self.assertEqual(version.verification_label, "Locally signed (anchoring disabled)")

        BlockchainOutboxEvent.objects.filter(pk=version.outbox_event_id).update(
            status=BlockchainOutboxEvent.Status.PENDING
        )
        version.outbox_event.refresh_from_db()
        self.assertEqual(version.verification_label, "Pending anchoring")

    def test_staff_label_mismatch_is_distinct(self):
        version = self.entry.proposal.current_version
        BlockchainOutboxEvent.objects.filter(pk__in=self._proposal_event_ids()).update(
            status=BlockchainOutboxEvent.Status.MISMATCH
        )
        version.outbox_event.refresh_from_db()
        label = version.verification_label
        self.assertEqual(label, "Mismatch detected")

    def test_local_signed_pill_is_informational_not_amber(self):
        # Disabled anchoring is a permanent informational state (Open Blue),
        # not a warning awaiting resolution (DESIGN.md status colors).
        event = self.entry.settlement.outbox_event
        BlockchainOutboxEvent.objects.filter(pk=event.pk).update(
            status=BlockchainOutboxEvent.Status.LOCAL, confirmed_at=None
        )
        event.refresh_from_db()
        html = render_to_string("web/staff/_evidence_level.html", {"event": event})
        self.assertIn("status-info", html)
        self.assertNotIn("status-warning", html)
        self.assertIn("Locally signed (anchoring disabled)", html)

        # A genuinely pending event under a live backend stays amber.
        BlockchainOutboxEvent.objects.filter(pk=event.pk).update(
            status=BlockchainOutboxEvent.Status.PENDING
        )
        event.refresh_from_db()
        html = render_to_string("web/staff/_evidence_level.html", {"event": event})
        self.assertIn("status-warning", html)
        self.assertNotIn("status-info", html)

    def test_outbox_export_carries_evidence_level_verbatim(self):
        BlockchainOutboxEvent.objects.filter(
            pk=self.entry.settlement.outbox_event_id
        ).update(status=BlockchainOutboxEvent.Status.LOCAL, confirmed_at=None)

        header, rows = _outbox_rows(self.seed.building.pk)

        self.assertIn("evidence_level", header)
        level_by_event = {
            row[header.index("event_id")]: row[header.index("evidence_level")]
            for row in rows
        }
        snapshot_event = self.entry.settlement.outbox_event
        self.assertEqual(level_by_event[snapshot_event.event_id], "LOCAL_SIGNED")
        self.assertIn("CHAIN_CONFIRMED", set(level_by_event.values()))

    def test_health_snapshot_reports_anchoring_backend(self):
        self.assertEqual(collect_health_snapshot(self.seed.building.pk)["anchoring_backend"], "besu")
        with override_settings(EVIDENCE_ANCHORING_BACKEND="disabled"):
            self.assertEqual(
                collect_health_snapshot(self.seed.building.pk)["anchoring_backend"], "disabled"
            )

    def test_pilot_metrics_reports_anchoring_backend(self):
        self.assertEqual(collect_pilot_metrics(self.seed.building.pk)["anchoring_backend"], "besu")
        with override_settings(EVIDENCE_ANCHORING_BACKEND="disabled"):
            self.assertEqual(collect_pilot_metrics(self.seed.building.pk)["anchoring_backend"], "disabled")
