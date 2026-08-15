import secrets

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from lamto.accounts.models import Building, ManagementMembership, ResidentOccupancy, Unit, User
from lamto.documents.models import Document, DocumentVersion
from lamto.evidence.signatures import platform_signer_address
from lamto.finance.models import Proposal
from lamto.finance.proposals import (
    create_proposal, create_standalone_proposal, decide_proposal, publish_proposal_version,
)
from lamto.maintenance.models import (
    BuildingLocation, CaseReport, IssueReport, MaintenanceCase, TriageDecision, WorkUpdate,
)
from lamto.maintenance.ratings import rate_completed_proposal


class StandaloneProposalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.building = Building.objects.create(name="B1")
        cls.unit = Unit.objects.create(building=cls.building, label="A-101")
        cls.manager = User.objects.create_user(email="m@x.vn", password="pw", display_name="M")
        cls.membership = ManagementMembership.objects.create(user=cls.manager, building=cls.building)
        cls.resident = User.objects.create_user(email="r@x.vn", password="pw", display_name="R")
        ResidentOccupancy.objects.create(user=cls.resident, unit=cls.unit)

    def quotation(self):
        key = secrets.token_hex(8)
        document = Document.objects.create(building=self.building, kind=Document.Kind.QUOTATION)
        return DocumentVersion.objects.create(
            document=document, version=1,
            storage_key=f"o-{key}", provider_version_id=f"o-{key}", filename="q.pdf",
            content_type="application/pdf", byte_size=1, sha256="1" * 64, uploader=self.manager,
        )

    def case(self):
        location = BuildingLocation.objects.create(building=self.building, name="Lobby")
        report = IssueReport.objects.create(
            reporter=self.resident, unit=self.unit, text="Leak", selected_location=location,
            location_path_snapshot="B1 / Lobby",
        )
        decision = TriageDecision.objects.create(
            report=report, operator=self.manager, category="Roof", urgency="HIGH",
            location=location, department="Maintenance", deadline_minutes=60,
        )
        case = MaintenanceCase.objects.create(
            decision=decision, building=self.building, category="Roof", urgency="HIGH",
            location=location, department="Maintenance", deadline_at=timezone.now(),
        )
        CaseReport.objects.create(case=case, report=report, grouped_by=self.manager)
        return case

    def publish(self, proposal, **overrides):
        values = dict(
            amount_vnd=1_000_000, contractor_name="Acme", fund_code="GENERAL",
            purpose="Leaking roof", proposed_action="Replace membrane",
            expected_schedule="August 2026", quotation_versions=[self.quotation()],
            event_id="0x" + secrets.token_hex(32),
        )
        values.update(overrides)
        return publish_proposal_version(proposal, self.membership, **values)

    def test_create_publish_and_republish_platform_anchor_seven_fields(self):
        proposal = create_standalone_proposal(self.building, self.membership)
        first = self.publish(proposal)
        proposal.refresh_from_db()
        self.assertIsNone(proposal.case_id)
        self.assertEqual(proposal.building, self.building)
        self.assertEqual(proposal.status, Proposal.Status.PUBLISHED)
        self.assertEqual(first.outbox_event.signer_address, platform_signer_address())
        self.assertEqual(first.snapshot["proposed_action"], "Replace membrane")
        self.assertEqual(first.snapshot["expected_schedule"], "August 2026")
        self.assertIsNone(first.snapshot["case_id"])
        self.assertEqual(first.snapshot["building_id"], self.building.pk)
        second = self.publish(proposal, proposed_action="Replace roof")
        self.assertEqual(second.number, 2)
        self.assertEqual(second.outbox_event.previous_hash, "0x" + first.outbox_event.payload_hash)

    def test_decision_transitions(self):
        proposal = create_standalone_proposal(self.building, self.membership)
        self.publish(proposal)
        decide_proposal(proposal, self.manager, proceed=True, note="Approved")
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, Proposal.Status.IN_PROGRESS)
        self.assertEqual(proposal.decision_note, "Approved")
        other = create_standalone_proposal(self.building, self.membership)
        self.publish(other)
        decide_proposal(other, self.manager, proceed=False)
        other.refresh_from_db()
        self.assertEqual(other.status, Proposal.Status.NOT_PROCEEDING)
        self.assertIsNotNone(other.closed_at)

    def test_case_backed_proposal_publish_is_platform_anchored(self):
        case = self.case()
        proposal = create_proposal(case, self.membership)

        version = self.publish(proposal)

        proposal.refresh_from_db()
        self.assertEqual(proposal.case, case)
        self.assertEqual(proposal.building, self.building)
        self.assertEqual(proposal.status, Proposal.Status.PUBLISHED)
        self.assertEqual(version.snapshot["case_id"], case.pk)
        self.assertEqual(version.outbox_event.signer_address, platform_signer_address())

    def test_work_update_target_xor_is_database_enforced(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            WorkUpdate.objects.create(cause="x", result="y")
        proposal = create_standalone_proposal(self.building, self.membership)
        case = self.case()
        with self.assertRaises(IntegrityError), transaction.atomic():
            WorkUpdate.objects.create(case=case, proposal=proposal, cause="x", result="y")

    def test_completed_proposal_rating_requires_occupancy_and_is_once(self):
        proposal = create_standalone_proposal(self.building, self.membership)
        with self.assertRaises(ValidationError):
            rate_completed_proposal(self.resident, proposal, True)
        proposal.completed_at = timezone.now()
        proposal.status = Proposal.Status.COMPLETED
        proposal.save(update_fields=["completed_at", "status"])
        rating = rate_completed_proposal(self.resident, proposal, True, "Good")
        self.assertEqual(rating.proposal, proposal)
        with self.assertRaises(ValidationError):
            rate_completed_proposal(self.resident, proposal, False)
        stranger = User.objects.create_user(email="s@x.vn", password="pw", display_name="S")
        with self.assertRaises(PermissionDenied):
            rate_completed_proposal(stranger, proposal, True)
