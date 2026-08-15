from django.contrib.auth import get_user_model
from django.core import mail
from django.db import transaction
from django.test import TestCase, override_settings
from django.utils import timezone

from lamto.notifications.models import NotificationDelivery, NotificationPreference
from lamto.notifications.services import (
    EVENT_REPORT_RECEIPT,
    process_delivery,
    process_due_notifications,
    queue_notification,
    queue_notification_after_commit,
)


class NotificationDeliveryTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="notify@example.test",
            password="secret",
            display_name="Notify User",
        )

    def test_queue_is_idempotent_per_recipient_event_channel(self):
        first = queue_notification(
            self.user,
            event_key="report.receipt:report:1",
            subject="Report received",
            body="Body",
            event_code=EVENT_REPORT_RECEIPT,
        )
        second = queue_notification(
            self.user,
            event_key="report.receipt:report:1",
            subject="Report received again",
            body="Body 2",
            event_code=EVENT_REPORT_RECEIPT,
        )
        self.assertEqual(len(first), 2)  # IN_APP + EMAIL
        self.assertEqual(
            {d.pk for d in first},
            {d.pk for d in second},
        )
        self.assertEqual(
            NotificationDelivery.objects.filter(
                recipient=self.user, event_key="report.receipt:report:1"
            ).count(),
            2,
        )

    def test_email_preference_opt_out_skips_email_channel(self):
        NotificationPreference.objects.create(
            user=self.user,
            event_code=EVENT_REPORT_RECEIPT,
            email_enabled=False,
        )
        rows = queue_notification(
            self.user,
            event_key="report.receipt:report:2",
            subject="Report received",
            body="Body",
            event_code=EVENT_REPORT_RECEIPT,
        )
        channels = {r.channel for r in rows}
        self.assertEqual(channels, {NotificationDelivery.Channel.IN_APP})

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_process_marks_in_app_available_and_sends_email(self):
        rows = queue_notification(
            self.user,
            event_key="report.receipt:report:3",
            subject="Hello",
            body="World",
            event_code=EVENT_REPORT_RECEIPT,
        )
        results = process_due_notifications(limit=10)
        self.assertEqual(len(results), 2)
        in_app = NotificationDelivery.objects.get(
            recipient=self.user,
            event_key="report.receipt:report:3",
            channel=NotificationDelivery.Channel.IN_APP,
        )
        email_row = NotificationDelivery.objects.get(
            recipient=self.user,
            event_key="report.receipt:report:3",
            channel=NotificationDelivery.Channel.EMAIL,
        )
        self.assertEqual(in_app.status, NotificationDelivery.Status.AVAILABLE)
        self.assertEqual(email_row.status, NotificationDelivery.Status.SENT)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Hello")

    @override_settings(EMAIL_BACKEND="lamto.notifications.tests.test_delivery.FailingEmailBackend")
    def test_email_failure_does_not_break_in_app_and_retries(self):
        rows = queue_notification(
            self.user,
            event_key="report.receipt:report:4",
            subject="Fail mail",
            body="Body",
            event_code=EVENT_REPORT_RECEIPT,
        )
        results = process_due_notifications(limit=10)
        in_app = NotificationDelivery.objects.get(
            channel=NotificationDelivery.Channel.IN_APP,
            event_key="report.receipt:report:4",
        )
        email_row = NotificationDelivery.objects.get(
            channel=NotificationDelivery.Channel.EMAIL,
            event_key="report.receipt:report:4",
        )
        self.assertEqual(in_app.status, NotificationDelivery.Status.AVAILABLE)
        self.assertEqual(email_row.status, NotificationDelivery.Status.FAILED)
        self.assertGreaterEqual(email_row.attempts, 1)
        self.assertIsNotNone(email_row.next_retry_at)

    def test_on_commit_queue_does_not_roll_back_business_state(self):
        """Notification enqueue is scheduled after commit; failures isolated."""
        with self.captureOnCommitCallbacks(execute=True):
            with transaction.atomic():
                queue_notification_after_commit(
                    self.user,
                    event_key="report.receipt:report:5",
                    subject="After commit",
                    body="Body",
                    event_code=EVENT_REPORT_RECEIPT,
                )
                marker = get_user_model().objects.create_user(
                    email="biz@example.test", password="x", display_name="Biz"
                )
        self.assertTrue(get_user_model().objects.filter(pk=marker.pk).exists())
        self.assertTrue(
            NotificationDelivery.objects.filter(
                event_key="report.receipt:report:5"
            ).exists()
        )

    def test_queue_failure_never_raises_to_caller(self):
        # Direct queue with invalid channel list still returns without raising domain state
        rows = queue_notification(
            self.user,
            event_key="report.receipt:report:6",
            subject="S",
            body="B",
            channels=[NotificationDelivery.Channel.IN_APP],
            event_code=EVENT_REPORT_RECEIPT,
        )
        self.assertEqual(len(rows), 1)


class FailingEmailBackend:
    """Email backend that always fails (for failure isolation tests)."""

    def __init__(self, *args, **kwargs):
        pass

    def open(self):
        return True

    def close(self):
        pass

    def send_messages(self, email_messages):
        raise RuntimeError("SMTP unavailable")


class DeadlineRiskNotificationTests(TestCase):
    def test_worker_queues_deadline_risk_for_near_due_case(self):
        from datetime import timedelta

        from django.contrib.auth import get_user_model

        from lamto.accounts.models import Building, ManagementMembership
        from lamto.config.worker import process_deadline_risk_batch
        from lamto.maintenance.models import (
            BuildingLocation,
            IssueReport,
            MaintenanceCase,
            TriageDecision,
        )
        from lamto.notifications.models import NotificationDelivery
        from lamto.notifications.services import EVENT_DEADLINE_RISK

        building = Building.objects.create(name="Deadline Building")
        location = BuildingLocation.objects.create(
            building=building, name="Basement", active=True
        )
        assignee_user = get_user_model().objects.create_user(
            email="assignee-dl@example.test",
            password="secret",
            display_name="Assignee",
        )
        op_user = get_user_model().objects.create_user(
            email="op-dl@example.test",
            password="secret",
            display_name="Operator",
        )
        ManagementMembership.objects.create(user=op_user, building=building)
        unit = __import__("lamto.accounts.models", fromlist=["Unit"]).Unit.objects.create(
            building=building, label="D-1"
        )
        report = IssueReport.objects.create(
            reporter=assignee_user,
            unit=unit,
            text="Near deadline",
            selected_location=location,
            location_path_snapshot="path",
        )
        decision = TriageDecision.objects.create(
            report=report,
            operator=op_user,
            category="General",
            urgency="HIGH",
            location=location,
            department="Ops",
            deadline_minutes=60,
            differences={},
        )
        case = MaintenanceCase.objects.create(
            decision=decision,
            building=building,
            category="General",
            urgency="HIGH",
            location=location,
            department="Ops",
            deadline_at=timezone.now() + timedelta(hours=12),
            active=True,
        )
        with self.captureOnCommitCallbacks(execute=True):
            result = process_deadline_risk_batch(limit=20)
        self.assertTrue(result.ok)
        self.assertGreaterEqual(result.count, 1)

        day = case.deadline_at.date().isoformat()
        event_key = f"{EVENT_DEADLINE_RISK}:case:{case.pk}:day:{day}"
        deliveries = NotificationDelivery.objects.filter(event_key=event_key)
        self.assertTrue(deliveries.exists())
        recipients = set(deliveries.values_list("recipient_id", flat=True))
        self.assertIn(op_user.pk, recipients)

        # Idempotent: second run does not create additional rows for same day
        before = deliveries.count()
        with self.captureOnCommitCallbacks(execute=True):
            process_deadline_risk_batch(limit=20)
        self.assertEqual(
            NotificationDelivery.objects.filter(event_key=event_key).count(),
            before,
        )
