import json
from unittest.mock import patch
from urllib.error import URLError

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from lamto.accounts.models import Building, ResidentOccupancy, Unit
from lamto.maintenance.ai import (
    MAX_CANDIDATE_CHARS,
    MAX_REPORT_CHARS,
    TriageValidationError,
    _endpoint_url,
    process_triage_job,
)
from lamto.maintenance.candidates import find_duplicate_candidates
from lamto.maintenance.models import BuildingLocation, IssueReport, TriageJob, TriageSuggestion
from lamto.maintenance.reporting import submit_report


def triage_payload(**overrides):
    payload = {
        "category": "Elevator",
        "interpreted_location": "Building B / Lift 2",
        "urgency": "HIGH",
        "confidence_percent": 87,
        "requires_manual_review": False,
        "duplicate_report_ids": [],
        "department": "Maintenance",
        "deadline_minutes": 240,
        "missing_information": [],
    }
    payload.update(overrides)
    return payload


def envelope(triage, request_id="cmpl-1"):
    body = {"choices": [{"message": {"content": json.dumps(triage)}}]}
    if request_id is not None:
        body["id"] = request_id
    return body


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        if isinstance(self.payload, bytes):
            return self.payload
        return json.dumps(self.payload).encode()


@override_settings(
    AI_TRIAGE_URL="https://triage.example.test/v1/chat/completions",
    AI_TRIAGE_TOKEN="token",
    AI_TRIAGE_MODEL="gpt-4o-mini",
)
class TriageTests(TestCase):
    @override_settings(AI_TRIAGE_MODEL="")
    def test_missing_model_is_rejected(self):
        with self.assertRaisesRegex(TriageValidationError, "AI_TRIAGE_MODEL"):
            _endpoint_url()

    @override_settings(AI_TRIAGE_URL="http://triage.example.test/v1/triage")
    def test_http_endpoint_is_rejected_without_explicit_opt_in(self):
        with self.assertRaisesRegex(TriageValidationError, "HTTPS"):
            _endpoint_url()

    @override_settings(
        AI_TRIAGE_URL="http://triage.example.test/v1/triage", AI_TRIAGE_ALLOW_HTTP=True
    )
    def test_http_endpoint_is_permitted_with_explicit_opt_in(self):
        self.assertEqual(_endpoint_url(), "http://triage.example.test/v1/triage")

    @override_settings(AI_TRIAGE_URL="https://[invalid/v1/chat/completions")
    def test_malformed_endpoint_routes_to_manual_triage(self):
        report = self.submit("Elevator shakes")

        job = process_triage_job(report.triage_job.id)

        self.assertEqual(job.status, TriageJob.Status.NEEDS_MANUAL)
        self.assertIn("config", job.failure_reason)
        report.refresh_from_db()
        self.assertEqual(report.status, IssueReport.Status.IN_REVIEW)

    @override_settings(AI_TRIAGE_URL="https://triage.example.test/bad path")
    @patch("lamto.maintenance.ai.urlopen")
    def test_whitespace_endpoint_routes_to_manual_triage(self, urlopen):
        report = self.submit("Elevator shakes")

        job = process_triage_job(report.triage_job.id)

        self.assertEqual(job.status, TriageJob.Status.NEEDS_MANUAL)
        self.assertIn("config", job.failure_reason)
        urlopen.assert_not_called()

    def submit(self, text):
        building = getattr(self, "building", None) or Building.objects.create(name="Building B")
        self.building = building
        resident = get_user_model().objects.create_user(
            email=f"resident-{IssueReport.objects.count()}@example.test",
            password="secret",
            display_name="Resident",
        )
        unit = Unit.objects.create(building=building, label=f"A-{IssueReport.objects.count()}")
        ResidentOccupancy.objects.create(user=resident, unit=unit)
        location, _ = BuildingLocation.objects.get_or_create(building=building, name="Lift 2")
        return submit_report(resident, unit, text, location, [])

    @patch("lamto.maintenance.ai.urlopen")
    def test_valid_response_creates_suggestion(self, urlopen):
        candidate = self.submit("Elevator shakes loudly")
        report = self.submit("Elevator shakes")
        urlopen.return_value = FakeResponse(
            envelope(triage_payload(duplicate_report_ids=[candidate.id]))
        )

        job = process_triage_job(report.triage_job.id)

        self.assertEqual(job.status, TriageJob.Status.SUCCEEDED)
        report.refresh_from_db()
        self.assertEqual(report.status, IssueReport.Status.IN_REVIEW)
        suggestion = TriageSuggestion.objects.get(job=job)
        self.assertEqual(suggestion.duplicate_report_ids, [candidate.id])
        self.assertEqual(suggestion.provider_request_id, "cmpl-1")
        request = urlopen.call_args.args[0]
        sent = request.data.decode()
        user_msg = json.loads(json.loads(sent)["messages"][1]["content"])
        self.assertNotIn("photo", json.dumps(user_msg))
        self.assertIn("Elevator shakes", sent)
        body = json.loads(request.data)
        self.assertEqual(body["model"], "gpt-4o-mini")
        self.assertEqual(body["temperature"], 0)
        self.assertEqual(body["response_format"], {"type": "json_object"})
        self.assertEqual(
            [message["role"] for message in body["messages"]], ["system", "user"]
        )

    @patch("lamto.maintenance.ai.urlopen")
    def test_category_is_normalized_to_a_code(self, urlopen):
        for raw, expected in [
            ("ELEVATOR", "ELEVATOR"),
            ("Water leak", "WATER_LEAK"),
            ("Heating / cooling", "HEATING_COOLING"),
            ("Plumbing", "OTHER"),
        ]:
            with self.subTest(raw=raw):
                report = self.submit("Elevator shakes")
                urlopen.return_value = FakeResponse(
                    envelope(triage_payload(category=raw))
                )

                job = process_triage_job(report.triage_job.id)

                self.assertEqual(job.status, TriageJob.Status.SUCCEEDED)
                suggestion = TriageSuggestion.objects.get(job=job)
                self.assertEqual(suggestion.category, expected)
                self.assertEqual(suggestion.raw_response["category"], raw)

    @patch("lamto.maintenance.ai.urlopen", side_effect=URLError("offline"))
    def test_transport_failure_preserves_report_for_manual_triage(self, _urlopen):
        report = self.submit("Elevator shakes")

        job = process_triage_job(report.triage_job.id)

        self.assertEqual(job.status, TriageJob.Status.NEEDS_MANUAL)
        report.refresh_from_db()
        self.assertEqual(report.status, IssueReport.Status.IN_REVIEW)
        self.assertTrue(IssueReport.objects.filter(pk=report.pk).exists())
        self.assertIn("transport", job.failure_reason)

    @patch("lamto.maintenance.ai.urlopen", side_effect=ValueError("invalid URL"))
    def test_request_value_error_routes_to_manual_triage(self, _urlopen):
        report = self.submit("Elevator shakes")

        job = process_triage_job(report.triage_job.id)

        self.assertEqual(job.status, TriageJob.Status.NEEDS_MANUAL)
        report.refresh_from_db()
        self.assertEqual(report.status, IssueReport.Status.IN_REVIEW)
        self.assertIn("transport", job.failure_reason)

    @patch("lamto.maintenance.ai.urlopen")
    def test_invalid_duplicate_id_routes_to_manual_triage(self, urlopen):
        report = self.submit("Elevator shakes")
        urlopen.return_value = FakeResponse(
            envelope(triage_payload(duplicate_report_ids=[999]))
        )

        job = process_triage_job(report.triage_job.id)

        self.assertEqual(job.status, TriageJob.Status.NEEDS_MANUAL)
        self.assertEqual(TriageSuggestion.objects.count(), 0)

    @patch("lamto.maintenance.ai.urlopen")
    def test_provider_manual_request_preserves_report(self, urlopen):
        report = self.submit("Elevator shakes")
        urlopen.return_value = FakeResponse(
            envelope(triage_payload(requires_manual_review=True))
        )

        job = process_triage_job(report.triage_job.id)

        self.assertEqual(job.status, TriageJob.Status.NEEDS_MANUAL)
        self.assertTrue(IssueReport.objects.filter(pk=report.pk).exists())
        self.assertIsNotNone(job.completed_at)

    @patch("lamto.maintenance.ai.urlopen")
    def test_non_list_missing_information_routes_to_manual_triage(self, urlopen):
        report = self.submit("Elevator shakes")
        urlopen.return_value = FakeResponse(
            envelope(triage_payload(missing_information="photo"))
        )

        job = process_triage_job(report.triage_job.id)

        self.assertEqual(job.status, TriageJob.Status.NEEDS_MANUAL)
        self.assertIn("missing_information", job.failure_reason)

    @patch("lamto.maintenance.ai.urlopen")
    def test_missing_response_id_routes_to_manual_triage(self, urlopen):
        report = self.submit("Elevator shakes")
        urlopen.return_value = FakeResponse(
            envelope(triage_payload(), request_id=None)
        )

        job = process_triage_job(report.triage_job.id)

        self.assertEqual(job.status, TriageJob.Status.NEEDS_MANUAL)
        self.assertEqual(TriageSuggestion.objects.count(), 0)
        self.assertIn("envelope", job.failure_reason)

    @patch("lamto.maintenance.ai.urlopen")
    def test_non_utf8_response_routes_to_manual_triage(self, urlopen):
        report = self.submit("Elevator shakes")
        urlopen.return_value = FakeResponse(b"\xff")

        job = process_triage_job(report.triage_job.id)

        self.assertEqual(job.status, TriageJob.Status.NEEDS_MANUAL)
        self.assertIn("invalid envelope", job.failure_reason)

    @patch("lamto.maintenance.ai.urlopen")
    def test_oversized_model_strings_route_to_manual_triage(self, urlopen):
        limits = {"category": 128, "department": 128, "interpreted_location": 1000}
        for field, limit in limits.items():
            with self.subTest(field=field):
                report = self.submit("Elevator shakes")
                urlopen.return_value = FakeResponse(
                    envelope(triage_payload(**{field: "x" * (limit + 1)}))
                )

                job = process_triage_job(report.triage_job.id)

                self.assertEqual(job.status, TriageJob.Status.NEEDS_MANUAL)
                self.assertIn(field, job.failure_reason)

    @patch("lamto.maintenance.ai.urlopen")
    def test_oversized_response_id_routes_to_manual_triage(self, urlopen):
        report = self.submit("Elevator shakes")
        urlopen.return_value = FakeResponse(envelope(triage_payload(), request_id="x" * 256))

        job = process_triage_job(report.triage_job.id)

        self.assertEqual(job.status, TriageJob.Status.NEEDS_MANUAL)
        self.assertIn("envelope", job.failure_reason)

    @patch("lamto.maintenance.ai.urlopen")
    def test_report_text_is_truncated_in_request(self, urlopen):
        long_text = ("leak " * MAX_REPORT_CHARS).strip()  # well over the char cap
        report = self.submit(long_text)
        urlopen.return_value = FakeResponse(envelope(triage_payload()))

        process_triage_job(report.triage_job.id)

        sent = json.loads(urlopen.call_args.args[0].data)
        user_msg = json.loads(sent["messages"][1]["content"])
        self.assertEqual(len(user_msg["text"]), MAX_REPORT_CHARS)
        report.refresh_from_db()
        self.assertEqual(report.text, long_text)

    @patch("lamto.maintenance.ai.urlopen")
    def test_candidate_text_is_truncated_in_request(self, urlopen):
        candidate = self.submit("Elevator " + "x" * MAX_CANDIDATE_CHARS * 2)
        report = self.submit("Elevator")
        urlopen.return_value = FakeResponse(envelope(triage_payload()))

        process_triage_job(report.triage_job.id)

        sent = json.loads(urlopen.call_args.args[0].data)
        candidates = json.loads(sent["messages"][1]["content"])["candidates"]
        sent_candidate = next(item for item in candidates if item["id"] == candidate.id)
        self.assertEqual(len(sent_candidate["text"]), MAX_CANDIDATE_CHARS)

    @patch("lamto.maintenance.ai.urlopen")
    def test_manual_log_includes_latency_and_response_id(self, urlopen):
        report = self.submit("Elevator shakes")
        urlopen.return_value = FakeResponse(
            envelope(triage_payload(requires_manual_review=True), request_id="cmpl-manual")
        )

        with self.assertLogs("lamto.maintenance.ai", level="INFO") as logs:
            process_triage_job(report.triage_job.id)

        message = logs.output[0]
        self.assertIn("request_id=cmpl-manual", message)
        self.assertRegex(message, r"latency_ms=\d+")
        self.assertNotIn("token", message)
        self.assertNotIn("Elevator shakes", message)

    def test_duplicate_candidates_are_limited_to_five(self):
        report = self.submit("Elevator shakes")
        for index in range(6):
            self.submit(f"Elevator shakes on floor {index}")

        candidates = list(find_duplicate_candidates(report))

        self.assertEqual(len(candidates), 5)
        self.assertTrue(all(candidate.similarity >= 0.2 for candidate in candidates))

    def test_private_reports_are_not_duplicate_candidates(self):
        private = self.submit("Elevator shakes loudly")
        private.is_private = True
        private.save(update_fields=["is_private"])
        report = self.submit("Elevator shakes")

        self.assertNotIn(private, find_duplicate_candidates(report))
