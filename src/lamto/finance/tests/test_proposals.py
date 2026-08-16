from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.utils import timezone

from lamto.accounts.models import Building, ManagementMembership, Unit
from lamto.documents.models import Document, DocumentVersion
from lamto.maintenance.models import (
    BuildingLocation,
    CaseReport,
    IssueReport,
    MaintenanceCase,
    TriageDecision,
    TriageJob,
)
from lamto.finance.models import Proposal, ProposalDocument, ProposalVersion

from lamto.finance.proposals import (
    build_proposal_evidence_payload,
    create_proposal,
    publish_proposal_version,
)


@override_settings(LANGUAGE_CODE="en-us")  # asserts English source strings
class ProposalVersionTests(TestCase):
    def make_signed_proposal_inputs(self):
        building = Building.objects.create(name="Minh An Residence")
        location = BuildingLocation.objects.create(building=building, name="Lobby")
        unit = Unit.objects.create(building=building, label="A-1")
        operator = get_user_model().objects.create_user(
            email="operator@example.test", password="secret", display_name="Operator"
        )
        membership = ManagementMembership.objects.create(user=operator, building=building)
        report = IssueReport.objects.create(
            reporter=get_user_model().objects.create_user(
                email="resident@example.test", password="secret", display_name="Resident"
            ),
            unit=unit,
            text="Elevator shakes",
            selected_location=location,
            location_path_snapshot="Minh An Residence / Lobby",
        )
        TriageJob.objects.create(report=report)
        decision = TriageDecision.objects.create(
            report=report,
            suggestion=None,
            operator=operator,
            category="Elevator",
            urgency="HIGH",
            location=location,
            management_queue="MAINTENANCE",
            deadline_minutes=240,
        )
        case = MaintenanceCase.objects.create(
            decision=decision,
            building=building,
            category="Elevator",
            urgency="HIGH",
            location=location,
            management_queue="MAINTENANCE",
            deadline_at="2026-07-20T12:00:00Z",
        )
        CaseReport.objects.create(case=case, report=report, grouped_by=operator)
        document = Document.objects.create(building=building, kind=Document.Kind.QUOTATION)
        quotation = DocumentVersion.objects.create(
            document=document,
            version=1,
            storage_key="quotation-original",
            provider_version_id="quotation-original",
            filename="quotation.pdf",
            content_type="application/pdf",
            byte_size=10,
            sha256="1" * 64,
            uploader=operator,
        )
        return membership, case, quotation, None

    def test_create_proposal_is_case_anchored_and_proposes_linked_reports(self):
        operator, case, _quotation, _account = self.make_signed_proposal_inputs()

        proposal = create_proposal(case, operator)

        self.assertEqual(proposal.case, case)
        case.decision.report.refresh_from_db()
        self.assertEqual(case.decision.report.status, IssueReport.Status.PROPOSED)

    def test_create_proposal_rejects_case_with_private_report(self):
        operator, case, _quotation, _account = self.make_signed_proposal_inputs()
        report = case.decision.report
        report.is_private = True
        report.save(update_fields=["is_private"])

        with self.assertRaisesMessage(
            ValidationError, "Private requests cannot become community proposals."
        ):
            create_proposal(case, operator)

    def test_create_proposal_rejects_active_completed_case(self):
        operator, case, _quotation, _account = self.make_signed_proposal_inputs()
        case.completed_at = timezone.now()
        case.save(update_fields=["completed_at"])

        with self.assertRaisesMessage(
            ValidationError, "An active uncompleted case is required."
        ):
            create_proposal(case, operator)

    def test_create_proposal_proposes_all_non_terminal_linked_reports_only(self):
        operator, case, _quotation, _account = self.make_signed_proposal_inputs()
        case = case
        source = case.decision.report
        pending = IssueReport.objects.create(
            reporter=source.reporter,
            unit=source.unit,
            text="Also shaking",
            selected_location=source.selected_location,
            location_path_snapshot=source.location_path_snapshot,
            status=IssueReport.Status.IN_REVIEW,
        )
        completed = IssueReport.objects.create(
            reporter=source.reporter,
            unit=source.unit,
            text="Already completed",
            selected_location=source.selected_location,
            location_path_snapshot=source.location_path_snapshot,
            status=IssueReport.Status.COMPLETED,
        )
        CaseReport.objects.create(case=case, report=pending, grouped_by=operator.user)
        CaseReport.objects.create(case=case, report=completed, grouped_by=operator.user)

        create_proposal(case, operator)

        source.refresh_from_db()
        pending.refresh_from_db()
        completed.refresh_from_db()
        self.assertEqual(source.status, IssueReport.Status.PROPOSED)
        self.assertEqual(pending.status, IssueReport.Status.PROPOSED)
        self.assertEqual(completed.status, IssueReport.Status.COMPLETED)

    def publish_version(self, proposal, membership, quotation, amount_vnd=18_500_000,
                        contractor_name="Company X", event_id=None):
        return publish_proposal_version(
            proposal, membership, amount_vnd=amount_vnd,
            contractor_name=contractor_name,
            purpose="Elevator", proposed_action="Repair elevator",
            expected_schedule="Within 14 days", quotation_versions=[quotation],
            event_id=event_id or "0x" + "aa" * 32,
        )

    def test_submitted_version_is_signed_immutable_and_tied_to_case(self):
        operator, case, quotation, account = self.make_signed_proposal_inputs()
        proposal = create_proposal(case, operator)
        event_id = "0x" + "aa" * 32
        version = self.publish_version(proposal, operator, quotation, event_id=event_id)

        self.assertEqual(version.number, 1)
        self.assertEqual(version.amount_vnd, 18_500_000)
        self.assertEqual(version.proposal_id, proposal.pk)
        self.assertEqual(version.outbox_event.event_id, event_id)
        version.amount_vnd = 1
        with self.assertRaises(ValueError):
            version.save()

    def test_revision_is_a_new_version_and_resets_normal_authorization(self):
        operator, case, quotation, account = self.make_signed_proposal_inputs()
        proposal = create_proposal(case, operator)
        first = self.publish_version(proposal, operator, quotation)
        second_event_id = "0x" + "bb" * 32
        second = self.publish_version(
            proposal, operator, quotation, amount_vnd=19_000_000,
            contractor_name="Company Y", event_id=second_event_id,
        )

        first.refresh_from_db()
        proposal.refresh_from_db()
        self.assertEqual(second.number, 2)
        self.assertEqual(first.amount_vnd, 18_500_000)
        self.assertEqual(proposal.current_version_id, second.pk)
        self.assertEqual(proposal.status, proposal.Status.PUBLISHED)

    def test_submission_requires_positive_amount_and_safe_quotation(self):
        operator, case, quotation, account = self.make_signed_proposal_inputs()
        proposal = create_proposal(case, operator)
        with self.assertRaises(ValidationError):
            self.publish_version(proposal, operator, quotation, amount_vnd=0)

        unsafe_document = Document.objects.create(
            building=case.building, kind=Document.Kind.QUOTATION
        )
        unsafe_quotation = DocumentVersion.objects.create(
            document=unsafe_document,
            version=1,
            storage_key="quotation-pending-scan",
            provider_version_id="quotation-pending-scan",
            filename="quotation.pdf",
            content_type="application/pdf",
            byte_size=10,
            sha256="3" * 64,
            uploader=operator.user,
        )
        version = self.publish_version(proposal, operator, unsafe_quotation)
        self.assertEqual(version.snapshot["quotation_versions"][0]["version_id"], unsafe_quotation.pk)

    def test_publication_uses_platform_signature(self):
        operator, case, quotation, account = self.make_signed_proposal_inputs()
        proposal = create_proposal(case, operator)
        version = self.publish_version(
            proposal, operator, quotation, event_id="0x" + "cc" * 32
        )
        self.assertTrue(version.outbox_event.signer_address)

    def test_database_trigger_rejects_proposal_version_update_and_delete(self):
        operator, case, quotation, account = self.make_signed_proposal_inputs()
        proposal = create_proposal(case, operator)
        version = self.publish_version(proposal, operator, quotation)

        with self.assertRaises(IntegrityError), transaction.atomic():
            ProposalVersion.objects.filter(pk=version.pk).update(amount_vnd=1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            ProposalVersion.objects.filter(pk=version.pk).delete()

        link = ProposalDocument.objects.filter(proposal_version=version).first()
        with self.assertRaises(ValueError):
            link.document_version = quotation
            link.save()
        with self.assertRaises(IntegrityError), transaction.atomic():
            ProposalDocument.objects.filter(pk=link.pk).update(document_version_id=quotation.pk)
        with self.assertRaises(IntegrityError), transaction.atomic():
            ProposalDocument.objects.filter(pk=link.pk).delete()

    def test_publish_proposal_version_with_start_and_end_dates(self):
        import datetime
        operator, case, quotation, account = self.make_signed_proposal_inputs()
        proposal = create_proposal(case, operator)
        version = publish_proposal_version(
            proposal,
            operator,
            amount_vnd=10_000_000,
            contractor_name="Company X",
            purpose="Elevator repair",
            proposed_action="Replace cables",
            expected_start=datetime.date(2026, 8, 1),
            expected_end=datetime.date(2026, 8, 15),
            quotation_versions=[quotation],
            event_id="0x" + "dd" * 32,
        )
        self.assertEqual(version.expected_start, datetime.date(2026, 8, 1))
        self.assertEqual(version.expected_end, datetime.date(2026, 8, 15))
        self.assertEqual(version.expected_schedule, "01/08/2026 \u2013 15/08/2026")
        self.assertEqual(version.snapshot["expected_start"], "2026-08-01")
        self.assertEqual(version.snapshot["expected_end"], "2026-08-15")
        self.assertEqual(version.snapshot["expected_schedule"], "01/08/2026 \u2013 15/08/2026")

    def test_publish_proposal_version_atomic_and_order_validation(self):
        import datetime
        operator, case, quotation, account = self.make_signed_proposal_inputs()
        proposal = create_proposal(case, operator)

        # Only start date
        with self.assertRaises(ValidationError):
            publish_proposal_version(
                proposal,
                operator,
                amount_vnd=10_000_000,
                contractor_name="Company X",
                purpose="Elevator repair",
                proposed_action="Replace cables",
                expected_start=datetime.date(2026, 8, 1),
                quotation_versions=[quotation],
                event_id="0x" + "ee" * 32,
            )

        # End date before start date
        with self.assertRaises(ValidationError):
            publish_proposal_version(
                proposal,
                operator,
                amount_vnd=10_000_000,
                contractor_name="Company X",
                purpose="Elevator repair",
                proposed_action="Replace cables",
                expected_start=datetime.date(2026, 8, 15),
                expected_end=datetime.date(2026, 8, 1),
                quotation_versions=[quotation],
                event_id="0x" + "ef" * 32,
            )

    def test_publish_proposal_version_links_matching_prediction(self):
        from lamto.finance.models import PricePrediction
        operator, case, quotation, _account = self.make_signed_proposal_inputs()
        proposal = create_proposal(case, operator)
        prediction = PricePrediction.objects.create(
            building=case.building,
            case=case,
            category="Elevator",
            amount_vnd=460_000_000,
            minimum_vnd=390_000_000,
            central_vnd=460_000_000,
            maximum_vnd=530_000_000,
            reasoning="Reasoning text.",
            source=PricePrediction.Source.PREDICTED,
            requested_by=operator,
        )
        version = publish_proposal_version(
            proposal,
            operator,
            amount_vnd=460_000_000,
            contractor_name="Company X",
            purpose="Elevator repair",
            proposed_action="Replace cables",
            quotation_versions=[quotation],
            event_id="0x" + "f1" * 32,
            price_prediction_id=prediction.pk,
        )
        prediction.refresh_from_db()
        self.assertEqual(prediction.proposal_version, version)
        self.assertEqual(version.price_prediction, prediction)
        # Snapshot, hash, and outbox payload remain untouched
        self.assertNotIn("prediction", version.snapshot)
        self.assertNotIn("price_comparison", version.snapshot)
        self.assertNotIn("prediction", version.outbox_event.payload)
        self.assertNotIn("price_comparison", version.outbox_event.payload)

    def test_publish_proposal_version_refuses_prediction_from_different_building(self):
        from lamto.finance.models import PricePrediction
        operator, case, quotation, _account = self.make_signed_proposal_inputs()
        other_building = Building.objects.create(name="Other Residence")
        other_membership = ManagementMembership.objects.create(user=operator.user, building=other_building)
        prediction = PricePrediction.objects.create(
            building=other_building,
            case=None,
            category="Elevator",
            amount_vnd=460_000_000,
            minimum_vnd=390_000_000,
            central_vnd=460_000_000,
            maximum_vnd=530_000_000,
            reasoning="Reasoning text.",
            source=PricePrediction.Source.PREDICTED,
            requested_by=other_membership,
        )
        proposal = create_proposal(case, operator)
        version = publish_proposal_version(
            proposal,
            operator,
            amount_vnd=460_000_000,
            contractor_name="Company X",
            purpose="Elevator repair",
            proposed_action="Replace cables",
            quotation_versions=[quotation],
            event_id="0x" + "f2" * 32,
            price_prediction_id=prediction.pk,
        )
        prediction.refresh_from_db()
        self.assertIsNone(prediction.proposal_version)
        self.assertFalse(hasattr(version, "price_prediction"))

    def test_publish_proposal_version_refuses_prediction_from_different_case(self):
        from lamto.finance.models import PricePrediction
        operator, case, quotation, _account = self.make_signed_proposal_inputs()
        other_report = IssueReport.objects.create(
            reporter=get_user_model().objects.create_user(
                email="resident2@example.test", password="secret", display_name="Resident 2"
            ),
            unit=Unit.objects.create(building=case.building, label="A-2"),
            text="Second elevator shakes",
            selected_location=case.location,
            location_path_snapshot="Minh An Residence / Lobby",
        )
        other_decision = TriageDecision.objects.create(
            report=other_report,
            suggestion=None,
            operator=operator.user,
            category="Elevator",
            urgency="HIGH",
            location=case.location,
            management_queue="MAINTENANCE",
            deadline_minutes=240,
        )
        other_case = MaintenanceCase.objects.create(
            decision=other_decision,
            building=case.building,
            category="Elevator",
            urgency="HIGH",
            location=case.location,
            management_queue="MAINTENANCE",
            deadline_at="2026-07-20T12:00:00Z",
        )
        prediction = PricePrediction.objects.create(
            building=case.building,
            case=other_case,
            category="Elevator",
            amount_vnd=460_000_000,
            minimum_vnd=390_000_000,
            central_vnd=460_000_000,
            maximum_vnd=530_000_000,
            reasoning="Reasoning text.",
            source=PricePrediction.Source.PREDICTED,
            requested_by=operator,
        )
        proposal = create_proposal(case, operator)
        version = publish_proposal_version(
            proposal,
            operator,
            amount_vnd=460_000_000,
            contractor_name="Company X",
            purpose="Elevator repair",
            proposed_action="Replace cables",
            quotation_versions=[quotation],
            event_id="0x" + "f3" * 32,
            price_prediction_id=prediction.pk,
        )
        prediction.refresh_from_db()
        self.assertIsNone(prediction.proposal_version)
        self.assertFalse(hasattr(version, "price_prediction"))

    def test_publish_proposal_version_discards_prediction_when_amount_mismatches(self):
        from lamto.finance.models import PricePrediction
        operator, case, quotation, _account = self.make_signed_proposal_inputs()
        prediction = PricePrediction.objects.create(
            building=case.building,
            case=case,
            category="Elevator",
            amount_vnd=20_000_000,
            minimum_vnd=15_000_000,
            central_vnd=20_000_000,
            maximum_vnd=25_000_000,
            reasoning="Reasoning text.",
            source=PricePrediction.Source.PREDICTED,
            requested_by=operator,
        )
        proposal = create_proposal(case, operator)
        version = publish_proposal_version(
            proposal,
            operator,
            amount_vnd=400_000_000,
            contractor_name="Company X",
            purpose="Elevator repair",
            proposed_action="Replace cables",
            quotation_versions=[quotation],
            event_id="0x" + "f4" * 32,
            price_prediction_id=prediction.pk,
        )
        prediction.refresh_from_db()
        self.assertIsNone(prediction.proposal_version)
        self.assertFalse(hasattr(version, "price_prediction"))

    def test_prediction_links_to_at_most_one_proposal_version(self):
        from lamto.finance.models import PricePrediction
        operator, case, quotation, _account = self.make_signed_proposal_inputs()
        proposal = create_proposal(case, operator)
        prediction = PricePrediction.objects.create(
            building=case.building,
            case=case,
            category="Elevator",
            amount_vnd=460_000_000,
            minimum_vnd=390_000_000,
            central_vnd=460_000_000,
            maximum_vnd=530_000_000,
            reasoning="Reasoning text.",
            source=PricePrediction.Source.PREDICTED,
            requested_by=operator,
        )
        version1 = publish_proposal_version(
            proposal,
            operator,
            amount_vnd=460_000_000,
            contractor_name="Company X",
            purpose="Elevator repair",
            proposed_action="Replace cables",
            quotation_versions=[quotation],
            event_id="0x" + "f5" * 32,
            price_prediction_id=prediction.pk,
        )
        # Attempt to publish another version claiming the same prediction
        version2 = publish_proposal_version(
            proposal,
            operator,
            amount_vnd=460_000_000,
            contractor_name="Company X",
            purpose="Elevator repair",
            proposed_action="Replace cables",
            quotation_versions=[quotation],
            event_id="0x" + "f6" * 32,
            price_prediction_id=prediction.pk,
        )
        prediction.refresh_from_db()
        self.assertEqual(prediction.proposal_version, version1)
        self.assertFalse(hasattr(version2, "price_prediction"))

