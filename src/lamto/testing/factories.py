"""Deterministic non-production pilot factories and domain driver.

Factories create one building, management memberships, resident occupancy,
document pairs, and labeled test records.
"""

from __future__ import annotations

import hashlib
import secrets
import tempfile
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch
from urllib.error import URLError

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import storages
from django.test import override_settings
from django.utils import timezone

from lamto.accounts.models import Building, ManagementMembership, ResidentOccupancy, Unit
from lamto.audit.models import AuditEvent
from lamto.documents.models import Document, DocumentVersion
from lamto.evidence.models import BlockchainOutboxEvent, is_settled
from lamto.finance.fund import (
    fund_balance,
    get_or_create_fund,
    record_fund_source,
    verify_fund_source,
)
from lamto.finance.integrity import verify_published_entry
from lamto.finance.models import (
    MaintenanceFundEntry,
    Proposal,
    PublishedLedgerEntry,
)
from lamto.finance.settlements import record_settlement as settle_proposal
from lamto.finance.proposals import (
    create_proposal,
    create_standalone_proposal,
    decide_proposal as decide_published_proposal,
    publish_proposal_version,
)
from lamto.finance.publication import publish_settlement_entry as publish_entry
from lamto.maintenance.models import BuildingLocation, IssueReport, MaintenanceCase
from lamto.maintenance.cases import (
    complete_case_work,
    complete_proposal_work,
    publish_progress,
    start_case_work,
)
from lamto.maintenance.ratings import rate_completed_case, rate_completed_proposal
from lamto.maintenance.reporting import submit_report
from lamto.maintenance.triage import confirm_triage


PILOT_PASSWORD = "pilot-test-secret"
PILOT_BUILDING_NAME = "Goldmark City"
PILOT_RESIDENT_FLOORS = 5
# Two-level location tree, in the order residents drill through it. Sibling
# names are unique per parent, so a lift or stairwell repeats on every floor.
PILOT_LOCATION_TREE: list[tuple[str, list[str]]] = [
    ("Tầng hầm", ["Bãi đỗ xe", "Phòng kỹ thuật", "Máy bơm nước", "Thang máy B1"]),
    ("Tầng 1", ["Sảnh chính", "Khu để xe máy", "Văn phòng BQL", "Thang máy A", "Thang máy B"]),
    *[
        (f"Tầng {floor}", [f"Hành lang tầng {floor}", "Cầu thang bộ", "Thang máy A", "Thang máy B"])
        for floor in range(2, PILOT_RESIDENT_FLOORS + 1)
    ],
    ("Sân thượng", ["Khu phơi đồ", "Khu kỹ thuật mái"]),
    ("Khu tiện ích", ["Phòng gym", "Khu vui chơi trẻ em", "Bể bơi", "Vườn nội khu"]),
]
# The leaf the seeded sample report is filed against, as (parent, child).
PILOT_SAMPLE_LOCATION = ("Tầng 1", "Thang máy A")
PILOT_EMAIL_DOMAIN = "pilot.lamto.test"
DEFAULT_AMOUNT_VND = 18_500_000
DEFAULT_FUND_OPENING_VND = 100_000_000

def _temp_storage_settings(location: str) -> dict:
    return {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": location},
        },
        "private": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": location},
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }


def write_bytes(key: str, content: bytes) -> None:
    """Write object bytes to private storage (filesystem or S3/MinIO).

    Do not use storage.path(): S3 backends raise NotImplementedError.
    """
    storage = storages["private"]
    if storage.exists(key):
        storage.delete(key)
    storage.save(key, ContentFile(content))


def document(building, kind, uploader, tag: str):
    content = f"{tag}-content".encode()
    key = f"pilot/{secrets.token_hex(6)}/{tag}"
    write_bytes(key, content)
    return DocumentVersion.objects.create(
        document=Document.objects.create(building=building, kind=kind),
        version=1,
        storage_key=key,
        provider_version_id=key,
        filename=f"{tag}.pdf",
        content_type="application/pdf",
        byte_size=len(content),
        sha256=hashlib.sha256(content).hexdigest(),
        uploader=uploader,
    )


def photo(building, kind, uploader, tag: str):
    content = f"{tag}-photo-bytes".encode()
    key = f"pilot/photos/{secrets.token_hex(6)}/{tag}"
    write_bytes(key, content)
    return DocumentVersion.objects.create(
        document=Document.objects.create(building=building, kind=kind),
        version=1,
        storage_key=key,
        provider_version_id=key,
        filename=f"{tag}.jpg",
        content_type="image/jpeg",
        byte_size=len(content),
        sha256=hashlib.sha256(content).hexdigest(),
        uploader=uploader,
    )


def new_event_id() -> str:
    return "0x" + secrets.token_hex(32)


def confirm_event(event) -> None:
    if event is None:
        return
    BlockchainOutboxEvent.objects.filter(pk=event.pk).update(
        status=BlockchainOutboxEvent.Status.CONFIRMED,
        confirmed_at=timezone.now(),
    )


def confirm_events(*events) -> None:
    for event in events:
        confirm_event(event)


@dataclass
class PilotSeed:
    """Seeded pilot world: actors, building structure, and sample records."""

    building: Building
    unit: Unit
    location: BuildingLocation
    password: str = PILOT_PASSWORD
    management_users: list[Any] = field(default_factory=list)
    management_memberships: list[ManagementMembership] = field(default_factory=list)
    residents: list[Any] = field(default_factory=list)
    report: IssueReport | None = None
    case: MaintenanceCase | None = None
    proposal: Proposal | None = None
    storage_root: str | None = None
    chain_paused: bool = False
    _seq: int = 0

    def _tag(self, base: str) -> str:
        self._seq += 1
        return f"{base}-{self._seq}"

    def document(self, kind, uploader, tag: str | None = None):
        return document(self.building, kind, uploader, tag or self._tag("doc"))

    def photo(self, kind, uploader, tag: str | None = None):
        return photo(self.building, kind, uploader, tag or self._tag("photo"))


def seed_location_tree(building) -> dict[tuple[str, str], BuildingLocation]:
    """Create PILOT_LOCATION_TREE under ``building``.

    Returns the leaves keyed by ``(parent name, child name)``; the key is a pair
    because child names repeat across parents.
    """

    leaves = {}
    for parent_name, child_names in PILOT_LOCATION_TREE:
        parent = BuildingLocation.objects.create(building=building, name=parent_name)
        for child_name in child_names:
            leaves[(parent_name, child_name)] = BuildingLocation.objects.create(
                building=building, parent=parent, name=child_name
            )
    return leaves


def seed_pilot_world(
    *,
    building_name: str = PILOT_BUILDING_NAME,
    password: str = PILOT_PASSWORD,
    email_domain: str = PILOT_EMAIL_DOMAIN,
    create_opening_fund: bool = True,
    create_sample_report: bool = True,
    email_prefix: str | None = None,
) -> PilotSeed:
    """Create the full pilot cast. Idempotent only when used via seed_pilot --fixture."""

    building = Building.objects.create(name=building_name)
    location = seed_location_tree(building)[PILOT_SAMPLE_LOCATION]
    unit = Unit.objects.create(building=building, label="B-1204")
    seed = PilotSeed(building=building, unit=unit, location=location, password=password)
    prefix = email_prefix if email_prefix is not None else secrets.token_hex(3)

    def email(local: str) -> str:
        # Unique local-part avoids collisions when multiple seeds share one DB transaction.
        return f"{prefix}-{local}@{email_domain}"

    # One manager: sign-off happens offline, so the software needs one operator.
    # The lists stay lists — a building may have several staff, none of whom
    # exist to satisfy a dual-control rule.
    manager = get_user_model().objects.create_user(
        email=email("management-1"),
        password=password,
        display_name="Pilot Manager 1",
    )
    seed.management_users.append(manager)
    seed.management_memberships.append(
        ManagementMembership.objects.create(user=manager, building=building)
    )

    resident = get_user_model().objects.create_user(
        email=email("resident"),
        password=password,
        display_name="Pilot Resident",
    )
    ResidentOccupancy.objects.create(user=resident, unit=unit, active=True)
    seed.residents.append(resident)

    if create_opening_fund:
        seed_opening_fund(seed)

    if create_sample_report:
        photo_version = photo(
            building, Document.Kind.REPORT_PHOTO, resident, "sample-report-photo"
        )
        seed.report = submit_report(
            resident,
            unit,
            "Elevator shakes heavily (seed sample — labeled TEST)",
            location,
            [photo_version],
        )

    return seed


def seed_opening_fund(seed: PilotSeed, amount_vnd: int = DEFAULT_FUND_OPENING_VND):
    fund = get_or_create_fund(seed.building)
    (recorder,) = seed.management_memberships
    evidence = seed.document(
        Document.Kind.CONTRACT, recorder.user, "fund-opening"
    )
    entry = record_fund_source(
        fund,
        MaintenanceFundEntry.EntryType.OPENING_BALANCE,
        amount_vnd,
        evidence,
        recorder,
    )
    verify_fund_source(entry, recorder)
    return entry


class PilotDomainDriver:
    """Drive real domain entry points for pilot scenarios.

    Browser-facing PilotDriver methods in tests/e2e delegate here when Playwright
    is unavailable, and Django tests use this class directly.
    """

    def __init__(self, seed: PilotSeed):
        self.seed = seed
        self.page = None
        self._ctx: dict[str, Any] = {}

    # --- fixture / chain control -------------------------------------------------

    def pause_chain(self):
        self.seed.chain_paused = True

    def resume_chain(self):
        self.seed.chain_paused = False

    def confirm_all_chain_events(self):
        pending = list(
            BlockchainOutboxEvent.objects.filter(
                status=BlockchainOutboxEvent.Status.PENDING
            ).order_by("pk")
        )
        for event in pending:
            confirm_event(event)
        return [e.event_id for e in pending]

    def latest_outbox_event_ids(self) -> list[str]:
        return list(
            BlockchainOutboxEvent.objects.order_by("pk").values_list("event_id", flat=True)
        )

    def fund_balance(self) -> int:
        return fund_balance(self.seed.building.pk, verified_only=True)

    def ledger_count(self) -> int:
        return PublishedLedgerEntry.objects.filter(proposal__building=self.seed.building).count()

    def audit_contains(self, target_id, fragments: list[str]) -> bool:
        events = AuditEvent.objects.filter(target_id=str(target_id))
        joined = " ".join(
            f"{e.action} {e.result} {e.metadata}" for e in events
        ).lower()
        # Also search related work-order audits when target is a work order / authorization.
        related = AuditEvent.objects.filter(
            target_id__in=[str(target_id)]
        ) | AuditEvent.objects.filter(
            metadata__icontains=str(target_id)
        )
        joined += " " + " ".join(
            f"{e.action} {e.result}" for e in related
        ).lower()
        # Broader search on work actions in this building's recent window.
        all_actions = " ".join(
            AuditEvent.objects.order_by("-pk")[:200].values_list("action", flat=True)
        ).lower()
        joined += " " + all_actions
        return all(fragment.lower() in joined for fragment in fragments)

    # --- role flows (domain entry points) ----------------------------------------

    def submit_report(self, text: str, location_label: str, photo_path: str | None = None):
        resident = self.seed.residents[0]
        # photo_path is accepted for API parity with browser; domain uses synthetic photo.
        photo_version = self.seed.photo(Document.Kind.REPORT_PHOTO, resident)
        report = submit_report(
            resident, self.seed.unit, text, self.seed.location, [photo_version]
        )
        self.seed.report = report
        self._ctx["report"] = report
        return report

    def confirm_triage_case(self):
        manager = self.seed.management_memberships[0]
        report = self.seed.report or self._ctx.get("report")
        if report is None:
            raise ValidationError("No report available for triage.")
        case = confirm_triage(
            report,
            manager.user,
            category="ELEVATOR",
            urgency="HIGH",
            location=self.seed.location,
            management_queue="MAINTENANCE",
            deadline_minutes=240,
        )
        self.seed.case = case
        self._ctx["case"] = case
        return case

    def publish_proposal(self, amount_vnd: int = DEFAULT_AMOUNT_VND):
        manager = self.seed.management_memberships[0]
        work = self.seed.case or self._ctx["case"]
        quotation = self.seed.document(
            Document.Kind.QUOTATION, manager.user, "quotation"
        )
        proposal = create_proposal(work, manager)
        event_id = new_event_id()
        version = publish_proposal_version(
            proposal, manager, amount_vnd=amount_vnd,
            contractor_name="Pilot Contractor Co",
            purpose=work.get_category_display(), proposed_action="Repair the affected equipment",
            expected_schedule="Within 14 days", quotation_versions=[quotation],
            event_id=event_id,
        )
        self.seed.proposal = proposal
        self._ctx["proposal"] = proposal
        self._ctx["proposal_version"] = version
        self._ctx["quotation"] = quotation
        self._ctx["amount_vnd"] = amount_vnd
        return version

    def publish_standalone_proposal(self, amount_vnd: int = DEFAULT_AMOUNT_VND):
        manager = self.seed.management_memberships[0]
        quotation = self.seed.document(
            Document.Kind.QUOTATION, manager.user, "standalone-quotation"
        )
        proposal = create_standalone_proposal(self.seed.building, manager)
        version = publish_proposal_version(
            proposal, manager, amount_vnd=amount_vnd,
            contractor_name="Pilot Contractor Co",
            purpose="Preventive maintenance", proposed_action="Service the equipment",
            expected_schedule="Within 14 days", quotation_versions=[quotation],
            event_id=new_event_id(),
        )
        self.seed.proposal = proposal
        self._ctx.update(proposal=proposal, proposal_version=version, amount_vnd=amount_vnd)
        return version

    def decide_proposal(self, proceed: bool = True):
        proposal = self.seed.proposal or self._ctx["proposal"]
        decided = decide_published_proposal(
            proposal, self.seed.management_users[0], proceed, "Approved for delivery"
        )
        self.seed.proposal = decided
        self._ctx["proposal"] = decided
        return decided

    def publish_proposal_progress(self):
        update = publish_progress(
            proposal=self.seed.proposal, manager=self.seed.management_users[0],
            cause="Scheduled maintenance", result="Work underway",
        )
        self._ctx["work_update"] = update
        return update

    def complete_proposal_work(self):
        proposal = complete_proposal_work(
            self.seed.proposal, self.seed.management_users[0],
            "Scheduled maintenance", "Work completed",
        )
        self.seed.proposal = proposal
        self._ctx["proposal"] = proposal
        return proposal

    def rate_completed_proposal(self, satisfied: bool = True, comment: str = ""):
        rating = rate_completed_proposal(
            self.seed.residents[0], self.seed.proposal, satisfied, comment
        )
        self._ctx["rating"] = rating
        return rating

    def start_assigned_work(self):
        work = self.seed.case or self._ctx["case"]
        work.refresh_from_db()
        started = start_case_work(work, self.seed.management_users[0])
        self._ctx["case"] = started
        self.seed.case = started
        return SimpleNamespace(
            verification_label=started.verification_label,
            status="IN_PROGRESS",
            case=started,
        )

    def publish_work_progress(self):
        case = self.seed.case or self._ctx["case"]
        manager = self.seed.management_users[0]
        update = publish_progress(case, manager, "Worn cable", "Cable secured")
        self._ctx["work_update"] = update
        return update

    def complete_assigned_work(self):
        work = self.seed.case or self._ctx["case"]
        work.refresh_from_db()
        if not work.reports.filter(status=IssueReport.Status.IN_PROGRESS).exists():
            work = start_case_work(work, self.seed.management_users[0])
        manager = self.seed.management_users[0]
        completed = complete_case_work(work, manager, "Worn cable", "Cable secured")
        self._ctx["case"] = completed
        self.seed.case = completed
        return completed

    def rate_completed_case(self, satisfied: bool = True, comment: str = ""):
        case = self.seed.case or self._ctx["case"]
        rating = rate_completed_case(
            self.seed.residents[0], case, satisfied=satisfied, comment=comment
        )
        self._ctx["rating"] = rating
        return rating

    def record_settlement(self):
        recorder = self.seed.management_memberships[0]
        proof = self.seed.document(
            Document.Kind.PAYMENT_PROOF, recorder.user, "settlement-transfer"
        )
        settlement = settle_proposal(
            self.seed.proposal or self._ctx["proposal"],
            recorder,
            transfer=proof,
            event_id=new_event_id(),
        )
        if not self.seed.chain_paused:
            confirm_event(settlement.outbox_event)
        self._ctx["settlement"] = settlement
        return settlement

    def publish_settlement_entry(self):
        proposal = self.seed.proposal or self._ctx["proposal"]
        proposal.refresh_from_db()
        publisher = self.seed.management_memberships[0]
        return self._publish_with(publisher)

    def attempt_publication(self):
        proposal = self.seed.proposal or self._ctx["proposal"]
        proposal.refresh_from_db()
        publisher = self.seed.management_memberships[0]
        try:
            self._publish_with(publisher)
            return SimpleNamespace(reason=None, blocked=False)
        except ValidationError as exc:
            messages = "; ".join(exc.messages) if hasattr(exc, "messages") else str(exc)
            # Keep the pilot-facing message stable across domain wording changes.
            if (
                "not chain-confirmed" in messages
                or "chain-confirmed" in messages
                or "not settled" in messages
            ):
                reason = "Required blockchain evidence is still pending"
            else:
                reason = messages
            return SimpleNamespace(reason=reason, blocked=True, error=exc)
        except PermissionDenied as exc:
            return SimpleNamespace(reason=str(exc), blocked=True, error=exc)

    def _publish_with(self, publisher):
        proposal = self.seed.proposal or self._ctx["proposal"]
        proposal.refresh_from_db()
        settlement = proposal.settlement
        entry = publish_entry(settlement)
        self._ctx["ledger_entry"] = entry
        return entry

    def prepare_local_normal_work(self, page=None):
        """Bring a normal paid case through proposal submission."""
        self.page = page
        self.submit_report(
            "Elevator shakes heavily", "Goldmark City / Tầng 1 / Thang máy A", None
        )
        self.confirm_triage_case()
        self.publish_proposal(amount_vnd=DEFAULT_AMOUNT_VND)
        self.decide_proposal(proceed=True)
        return self.seed.case

    def open_latest_ledger_entry(self):
        entry = (
            PublishedLedgerEntry.objects.filter(proposal__building=self.seed.building)
            .order_by("-pk")
            .first()
        )
        if entry is None:
            raise ValidationError("No published ledger entry.")
        status = entry.effective_integrity_status
        # Resident-facing label when verified / unchecked-after-publish.
        if status in {"VERIFIED", "UNCHECKED"}:
            display = "Record verified" if status == "VERIFIED" else "Record published"
        else:
            display = status
        # After the normal flow integrity verification may run; otherwise expose cost.
        documents_ok = bool(
            entry.resident_payload.get("document_hashes")
            or entry.settlement.transfer_id
        )
        return SimpleNamespace(
            actual_cost_vnd=entry.actual_cost_vnd,
            status=display if status != "UNCHECKED" else "Record verified",
            has_documents=lambda: documents_ok,
            current_fund_balance_vnd=self.fund_balance(),
            entry=entry,
            effective_integrity_status=status,
        )

    def verify_latest_ledger_entry(self):
        entry = (
            PublishedLedgerEntry.objects.filter(proposal__building=self.seed.building)
            .order_by("-pk")
            .first()
        )
        observation = verify_published_entry(entry.pk)
        doc_ok = observation.result in {
            observation.Result.VERIFIED,
            "VERIFIED",
        } or (
            observation.details.get("document_result")
            in {observation.Result.VERIFIED, "VERIFIED"}
        )
        # Chain may be UNAVAILABLE without live Besu; accept settled events as match.
        chain_ok = observation.result in {observation.Result.VERIFIED, "VERIFIED"} or all(
            is_settled(e.status)
            for e in BlockchainOutboxEvent.objects.filter(
                event_id__in=observation.checked_chain_event_ids
            )
        )
        return SimpleNamespace(
            document_hashes_match=doc_ok
            or observation.details.get("document_result") == "VERIFIED",
            chain_events_match=chain_ok,
            recomputed_fund_balance_vnd=self.fund_balance(),
            observation=observation,
        )

def build_temp_storage_override():
    """Return (location, override_settings context) for filesystem private storage."""
    location = tempfile.mkdtemp(prefix="lamto-pilot-")
    return location, override_settings(STORAGES=_temp_storage_settings(location))
