"""In-process OpenAI-compatible triage provider."""

import json
import logging
import time
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .candidates import find_duplicate_candidates
from .models import (
    IssueReport,
    TriageJob,
    TriageSuggestion,
    normalize_category,
    normalize_management_queue,
)
from .triage_prompt import build_system_prompt

logger = logging.getLogger(__name__)


class TriageValidationError(ValueError):
    pass


RESPONSE_KEYS = {
    "category",
    "interpreted_location",
    "urgency",
    "confidence_percent",
    "requires_manual_review",
    "duplicate_report_ids",
    "management_queue",
    "deadline_minutes",
    "missing_information",
    "provider_request_id",
}
URGENCIES = {"LOW", "MEDIUM", "HIGH"}
MODEL_KEYS = RESPONSE_KEYS - {"provider_request_id"}
MAX_REPORT_CHARS = 4000
MAX_CANDIDATE_CHARS = 1000
MODEL_STRING_LIMITS = {
    "category": 128,
    "management_queue": 32,
    "interpreted_location": 1000,
}
MAX_PROVIDER_REQUEST_ID_CHARS = 255


def _claim_triage_job(job_id=None):
    with transaction.atomic():
        jobs = (
            TriageJob.objects.select_for_update(skip_locked=True)
            .select_related("report__unit", "report__selected_location")
            .filter(status=TriageJob.Status.PENDING)
        )
        if job_id is not None:
            jobs = jobs.filter(pk=job_id)
        job = jobs.order_by("pk").first()
        if job is None:
            return None
        job.status = TriageJob.Status.PROCESSING
        job.started_at = timezone.now()
        job.failure_reason = ""
        job.save(update_fields=["status", "started_at", "failure_reason"])
        return job


def _endpoint_url():
    url = settings.AI_TRIAGE_URL
    if any(
        character.isspace() or ord(character) < 32 or ord(character) == 127
        for character in url
    ):
        raise TriageValidationError(
            "AI_TRIAGE_URL must not contain whitespace or control characters"
        )
    try:
        parsed = urlsplit(url)
    except ValueError as error:
        raise TriageValidationError(f"AI_TRIAGE_URL is invalid: {error}") from error
    if not parsed.scheme or not parsed.netloc:
        raise TriageValidationError("AI_TRIAGE_URL must be an absolute URL")
    if parsed.scheme != "https" and not (
        parsed.scheme == "http" and settings.AI_TRIAGE_ALLOW_HTTP
    ):
        raise TriageValidationError(
            "AI_TRIAGE_URL must use HTTPS outside local/test mode"
        )
    if not settings.AI_TRIAGE_TOKEN:
        raise TriageValidationError("AI_TRIAGE_TOKEN is required")
    if not settings.AI_TRIAGE_MODEL:
        raise TriageValidationError("AI_TRIAGE_MODEL is required")
    return url


def _valid_string(value):
    return type(value) is str and bool(value)


def _validate_response(payload, candidate_ids):
    if type(payload) is not dict or set(payload) != MODEL_KEYS:
        raise TriageValidationError("response keys do not match the contract")
    if not all(
        _valid_string(payload[key])
        for key in ("category", "interpreted_location", "management_queue")
    ):
        raise TriageValidationError("response strings must be non-empty strings")
    for key, limit in MODEL_STRING_LIMITS.items():
        if len(payload[key]) > limit:
            raise TriageValidationError(f"response {key} exceeds {limit} characters")
    if payload["urgency"] not in URGENCIES:
        raise TriageValidationError("response urgency is invalid")
    if (
        type(payload["confidence_percent"]) is not int
        or not 0 <= payload["confidence_percent"] <= 100
    ):
        raise TriageValidationError("response confidence_percent is invalid")
    if type(payload["requires_manual_review"]) is not bool:
        raise TriageValidationError("response requires_manual_review is invalid")
    duplicate_ids = payload["duplicate_report_ids"]
    if type(duplicate_ids) is not list or any(
        type(report_id) is not int for report_id in duplicate_ids
    ):
        raise TriageValidationError("response duplicate_report_ids is invalid")
    if not set(duplicate_ids).issubset(candidate_ids):
        raise TriageValidationError(
            "response duplicate_report_ids were not supplied as candidates"
        )
    if type(payload["deadline_minutes"]) is not int or payload["deadline_minutes"] <= 0:
        raise TriageValidationError("response deadline_minutes is invalid")
    missing = payload["missing_information"]
    if type(missing) is not list or any(not _valid_string(item) for item in missing):
        raise TriageValidationError("response missing_information is invalid")
    return payload


def _manual(job, reason, error_class, started, request_id=None):
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    job.status = TriageJob.Status.NEEDS_MANUAL
    job.failure_reason = reason[:255]
    job.completed_at = timezone.now()
    job.save(update_fields=["status", "failure_reason", "completed_at"])
    IssueReport.objects.filter(
        pk=job.report_id, status=IssueReport.Status.SUBMITTED
    ).update(status=IssueReport.Status.IN_REVIEW)
    logger.info(
        "triage.processed job=%s report=%s model=%s request_id=%s latency_ms=%s outcome=manual error_class=%s",
        job.pk,
        job.report_id,
        settings.AI_TRIAGE_MODEL,
        request_id or "-",
        elapsed_ms,
        error_class,
    )
    return job


def _chat_body(job, candidates):
    user_payload = {
        "report_id": job.report_id,
        "text": job.report.text[:MAX_REPORT_CHARS],
        "location_path_snapshot": job.report.location_path_snapshot,
        "candidates": [
            {
                "id": candidate.pk,
                "text": candidate.text[:MAX_CANDIDATE_CHARS],
                "location_path_snapshot": candidate.location_path_snapshot,
            }
            for candidate in candidates
        ],
    }
    return {
        "model": settings.AI_TRIAGE_MODEL,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": json.dumps(user_payload)},
        ],
    }


def _extract_triage(envelope):
    if type(envelope) is not dict:
        raise TriageValidationError("provider envelope is not an object")
    request_id = envelope.get("id")
    if not _valid_string(request_id):
        raise TriageValidationError("provider envelope is missing id")
    if len(request_id) > MAX_PROVIDER_REQUEST_ID_CHARS:
        raise TriageValidationError("provider envelope id exceeds 255 characters")
    try:
        content = envelope["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise TriageValidationError(f"missing choices/message/content: {error}")
    if not _valid_string(content):
        raise TriageValidationError("provider message content is empty")
    return request_id, json.loads(content)


def _process_claimed_job(job):
    started = time.perf_counter()
    candidates = list(find_duplicate_candidates(job.report))
    candidate_ids = {candidate.pk for candidate in candidates}
    try:
        request = Request(
            _endpoint_url(),
            data=json.dumps(_chat_body(job, candidates)).encode(),
            headers={
                "Authorization": f"Bearer {settings.AI_TRIAGE_TOKEN}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        with urlopen(request, timeout=settings.AI_TRIAGE_TIMEOUT_SECONDS) as response:
            raw = response.read()
    except TriageValidationError as error:
        return _manual(job, f"config: {error}", "config", started)
    except (URLError, TimeoutError, OSError, ValueError) as error:
        return _manual(job, f"transport: {error}", "transport", started)

    try:
        request_id, triage = _extract_triage(json.loads(raw))
    except (
        TriageValidationError,
        json.JSONDecodeError,
        UnicodeDecodeError,
        KeyError,
        IndexError,
        TypeError,
    ) as error:
        return _manual(job, f"invalid envelope: {error}", "invalid_envelope", started)

    try:
        payload = _validate_response(triage, candidate_ids)
    except (TriageValidationError, ValueError, TypeError) as error:
        return _manual(job, f"schema: {error}", "schema", started, request_id)

    if payload["requires_manual_review"]:
        return _manual(
            job,
            "provider requested manual review",
            "provider_manual",
            started,
            request_id,
        )

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    payload["provider_request_id"] = request_id
    TriageSuggestion.objects.create(
        job=job,
        category=normalize_category(payload["category"]),
        interpreted_location=payload["interpreted_location"],
        urgency=payload["urgency"],
        confidence_percent=payload["confidence_percent"],
        duplicate_report_ids=payload["duplicate_report_ids"],
        management_queue=normalize_management_queue(payload["management_queue"]),
        deadline_minutes=payload["deadline_minutes"],
        missing_information=payload["missing_information"],
        raw_response=payload,
        provider_request_id=request_id,
        validation_metadata={"candidate_ids": sorted(candidate_ids)},
        elapsed_ms=elapsed_ms,
    )
    job.status = TriageJob.Status.SUCCEEDED
    job.completed_at = timezone.now()
    job.save(update_fields=["status", "completed_at"])
    IssueReport.objects.filter(
        pk=job.report_id, status=IssueReport.Status.SUBMITTED
    ).update(status=IssueReport.Status.IN_REVIEW)
    logger.info(
        "triage.processed job=%s report=%s model=%s request_id=%s latency_ms=%s outcome=succeeded",
        job.pk,
        job.report_id,
        settings.AI_TRIAGE_MODEL,
        request_id,
        elapsed_ms,
    )
    return job


def process_triage_job(job_id) -> TriageJob:
    job = _claim_triage_job(job_id)
    if job is None:
        return TriageJob.objects.get(pk=job_id)
    return _process_claimed_job(job)
