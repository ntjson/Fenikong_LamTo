from unittest.mock import patch

from django.test import SimpleTestCase, TestCase

from lamto.config.worker import (
    CycleResult,
    ProcessorResult,
    process_notifications_batch,
    process_registration_expiry_batch,
    run_worker_cycle,
)


class WorkerCycleTests(TestCase):
    def test_failed_adapter_does_not_stop_other_queues(self):
        def boom(**kwargs):
            raise RuntimeError("triage down")

        def ok_notifications(**kwargs):
            return ProcessorResult(name="notifications", ok=True, count=0, detail="ok")

        with patch(
            "lamto.config.worker.PROCESSORS",
            (
                boom,
                ok_notifications,
            ),
        ):
            result = run_worker_cycle()

        self.assertEqual(len(result.processors), 2)
        self.assertFalse(result.processors[0].ok)
        self.assertIn("triage down", result.processors[0].detail)
        self.assertTrue(result.processors[1].ok)

    def test_processor_result_isolation_with_real_notifications(self):
        # Notifications batch should succeed even if empty
        res = process_notifications_batch(limit=5)
        self.assertTrue(res.ok)
        self.assertEqual(res.name, "notifications")

    @patch("lamto.accounts.registration.expire_registration_requests", return_value=3)
    def test_registration_expiry_processor(self, expire):
        result = process_registration_expiry_batch(limit=7)

        expire.assert_called_once_with(limit=7)
        self.assertTrue(result.ok)
        self.assertEqual(result.name, "registration_expiry")
        self.assertEqual(result.count, 3)

    @patch(
        "lamto.accounts.registration.expire_registration_requests",
        side_effect=RuntimeError("database unavailable"),
    )
    def test_registration_expiry_failure_is_a_processor_result(self, expire):
        result = process_registration_expiry_batch()

        self.assertFalse(result.ok)
        self.assertIn("database unavailable", result.detail)

    def test_cycle_runs_all_named_processors(self):
        calls = []

        def make(name, fail=False):
            def _fn(**kwargs):
                calls.append(name)
                if fail:
                    raise RuntimeError(f"{name} failed")
                return ProcessorResult(name=name, ok=True, count=0)

            return _fn

        processors = (
            make("triage"),
            make("blockchain_outbox", fail=True),
            make("publication_finalize"),
            make("integrity"),
            make("notifications"),
        )
        with patch("lamto.config.worker.PROCESSORS", processors):
            result = run_worker_cycle()

        self.assertEqual(
            calls,
            [
                "triage",
                "blockchain_outbox",
                "publication_finalize",
                "integrity",
                "notifications",
            ],
        )
        self.assertFalse(result.all_ok)
        self.assertTrue(result.processors[0].ok)
        self.assertFalse(result.processors[1].ok)
        self.assertTrue(result.processors[2].ok)
        self.assertTrue(result.processors[-1].ok)
