import threading

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, close_old_connections, connection, transaction
from django.test import TestCase, TransactionTestCase, override_settings

from lamto.accounts.models import Building, ManagementMembership, Unit
from lamto.audit.models import AuditEvent
from lamto.finance.proposals import create_proposal
from lamto.maintenance.cases import start_case_work
from lamto.maintenance.models import (
    BuildingLocation,
    CaseReport,
    IssueReport,
    MaintenanceCase,
    TriageJob,
    TriageSuggestion,
)
from lamto.maintenance.triage import confirm_triage, group_report


class CaseFixture:
    def setUp(self):
        self.fixture_id = self._testMethodName
        self.building = Building.objects.create(name="Minh An Residence")
        self.location = BuildingLocation.objects.create(building=self.building, name="Lift 2")
        self.operator = get_user_model().objects.create_user(
            email=f"operator-{self.fixture_id}@example.test", password="secret", display_name="Operator"
        )
        self.membership = ManagementMembership.objects.create(user=self.operator, building=self.building)

    def make_report(self, number, building=None, location=None):
        building = building or self.building
        location = location or self.location
        resident = get_user_model().objects.create_user(
            email=f"resident-{number}-{self.fixture_id}@example.test",
            password="secret",
            display_name="Resident",
        )
        report = IssueReport.objects.create(
            reporter=resident,
            unit=Unit.objects.create(building=building, label=f"A-{number}"),
            text="Elevator shakes",
            selected_location=location,
            location_path_snapshot="Minh An Residence / Lift 2",
        )
        job = TriageJob.objects.create(report=report)
        TriageSuggestion.objects.create(
            job=job,
            category="ELEVATOR",
            interpreted_location="Lift 2",
            urgency="MEDIUM",
            confidence_percent=90,
            duplicate_report_ids=[],
            management_queue="MAINTENANCE",
            deadline_minutes=60,
            raw_response={},
            provider_request_id=f"request-{number}",
            elapsed_ms=1,
        )
        return report


@override_settings(LANGUAGE_CODE="en-us")  # asserts English source strings
class CaseTests(CaseFixture, TestCase):

    def test_late_grouping_adopts_in_progress_case_phase(self):
        case = confirm_triage(
            self.make_report(1), self.operator, "Elevator", "HIGH", self.location, "Maintenance", 60
        )
        start_case_work(case, self.operator)
        late = self.make_report(2)

        group_report(case, late, self.operator)

        late.refresh_from_db()
        self.assertEqual(late.status, IssueReport.Status.IN_PROGRESS)

    def test_late_grouping_adopts_proposed_case_phase(self):
        case = confirm_triage(
            self.make_report(1), self.operator, "Elevator", "HIGH", self.location, "Maintenance", 60
        )
        create_proposal(case, self.membership)
        late = self.make_report(2)

        group_report(case, late, self.operator)

        late.refresh_from_db()
        self.assertEqual(late.status, IssueReport.Status.PROPOSED)

    def test_late_grouping_adopts_ordinary_review_case_phase(self):
        case = confirm_triage(
            self.make_report(1), self.operator, "Elevator", "HIGH", self.location, "Maintenance", 60
        )
        late = self.make_report(2)

        group_report(case, late, self.operator)

        late.refresh_from_db()
        self.assertEqual(late.status, IssueReport.Status.IN_REVIEW)

    def test_private_report_cannot_join_case_with_proposal(self):
        case = confirm_triage(
            self.make_report(1), self.operator, "Elevator", "HIGH", self.location, "Maintenance", 60
        )
        create_proposal(case, self.membership)
        private = self.make_report(2)
        private.is_private = True
        private.save(update_fields=["is_private"])

        with self.assertRaisesMessage(ValidationError, "Private requests"):
            group_report(case, private, self.operator)

        private.refresh_from_db()
        self.assertEqual(private.status, IssueReport.Status.SUBMITTED)
        self.assertFalse(CaseReport.objects.filter(case=case, report=private).exists())

    def test_confirmation_records_operator_difference_and_grouping_is_idempotent(self):
        first, second = self.make_report(1), self.make_report(2)

        case = confirm_triage(
            first,
            self.operator,
            category="Elevator",
            urgency="HIGH",
            location=self.location,
            management_queue="MAINTENANCE",
            deadline_minutes=240,
        )
        self.assertEqual(case.reports.get(), first)
        self.assertEqual(case.decision.differences["urgency"], {"suggested": "MEDIUM", "chosen": "HIGH"})
        self.assertEqual(case.decision.differences["deadline_minutes"], {"suggested": 60, "chosen": 240})
        self.assertEqual(confirm_triage(first, self.operator, "x", "LOW", self.location, "x", 1), case)

        link = group_report(case, second, self.operator)
        self.assertEqual(group_report(case, second, self.operator), link)
        self.assertEqual(set(case.reports.values_list("id", flat=True)), {first.id, second.id})
        self.assertEqual(CaseReport.objects.filter(case=case, report=second).count(), 1)
        self.assertEqual(AuditEvent.objects.filter(action="case.group", result="accepted").count(), 1)

    def test_confirmation_normalizes_category_to_codes(self):
        legacy = confirm_triage(
            self.make_report(1), self.operator, "Water leak", "HIGH", self.location, "Maintenance", 60
        )
        self.assertEqual(legacy.category, "WATER_LEAK")
        self.assertEqual(legacy.decision.category, "WATER_LEAK")

        unknown = confirm_triage(
            self.make_report(2), self.operator, "Sơn lại hành lang", "LOW", self.location, "Maintenance", 60
        )
        self.assertEqual(unknown.category, "OTHER")

    def test_grouping_rejects_report_already_in_an_active_case(self):
        first, second, third = self.make_report(1), self.make_report(2), self.make_report(3)
        case = confirm_triage(first, self.operator, "Elevator", "HIGH", self.location, "Maintenance", 240)
        other_case = confirm_triage(third, self.operator, "Elevator", "HIGH", self.location, "Maintenance", 240)

        with self.assertRaisesMessage(ValidationError, "active case"):
            group_report(case, third, self.operator)

        self.assertEqual(other_case.reports.get(), third)
        self.assertEqual(MaintenanceCase.objects.count(), 2)

    def test_triage_rejects_unaffiliated_or_cross_building_operator_and_location(self):
        report = self.make_report(1)
        other_building = Building.objects.create(name="Other Residence")
        other_location = BuildingLocation.objects.create(building=other_building, name="Lift 1")
        other_operator = get_user_model().objects.create_user(
            email="other-operator@example.test", password="secret", display_name="Other Operator"
        )
        ManagementMembership.objects.create(user=other_operator, building=other_building)

        with self.assertRaises(PermissionDenied):
            confirm_triage(report, other_operator, "Elevator", "HIGH", self.location, "Maintenance", 60)
        with self.assertRaises(PermissionDenied):
            confirm_triage(
                report,
                get_user_model().objects.create_user(
                    email="unaffiliated@example.test", password="secret", display_name="Unaffiliated"
                ),
                "Elevator",
                "HIGH",
                self.location,
                "Maintenance",
                60,
            )
        with self.assertRaisesMessage(ValidationError, "belong to the report building"):
            confirm_triage(report, self.operator, "Elevator", "HIGH", other_location, "Maintenance", 60)

    def test_grouping_rejects_cross_building_report(self):
        case = confirm_triage(
            self.make_report(1), self.operator, "Elevator", "HIGH", self.location, "Maintenance", 60
        )
        other_building = Building.objects.create(name="Other Residence")
        other_report = self.make_report(
            2,
            other_building,
            BuildingLocation.objects.create(building=other_building, name="Lift 1"),
        )

        with self.assertRaisesMessage(ValidationError, "case building"):
            group_report(case, other_report, self.operator)


class CaseDatabaseConstraintTests(CaseFixture, TransactionTestCase):
    available_apps = [
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "lamto.accounts",
        "lamto.audit",
        "lamto.maintenance",
    ]

    def _fixture_teardown(self):
        # Immutable audit/document triggers correctly reject Django's TRUNCATE flush.
        pass

    def test_database_rejects_second_active_case_link_for_orm_raw_and_queryset_writes(self):
        first, second = self.make_report(1), self.make_report(2)
        first_case = confirm_triage(first, self.operator, "Elevator", "HIGH", self.location, "Maintenance", 60)
        second_case = confirm_triage(second, self.operator, "Elevator", "HIGH", self.location, "Maintenance", 60)

        with self.assertRaises(IntegrityError), transaction.atomic():
            CaseReport.objects.create(case=second_case, report=first, grouped_by=self.operator)
        with self.assertRaises(IntegrityError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO maintenance_casereport (case_id, report_id, grouped_by_id, created_at) "
                    "VALUES (%s, %s, %s, NOW())",
                    [second_case.pk, first.pk, self.operator.pk],
                )
        with self.assertRaises(IntegrityError), transaction.atomic():
            CaseReport.objects.filter(case=second_case, report=second).update(report=first)

    def test_database_rejects_reactivating_case_that_conflicts_with_an_active_link(self):
        report = self.make_report(1)
        inactive_case = confirm_triage(
            report, self.operator, "Elevator", "HIGH", self.location, "Maintenance", 60
        )
        inactive_case.active = False
        inactive_case.save(update_fields=["active"])
        other_case = confirm_triage(
            self.make_report(2), self.operator, "Elevator", "HIGH", self.location, "Maintenance", 60
        )
        CaseReport.objects.create(case=other_case, report=report, grouped_by=self.operator)

        with self.assertRaises(IntegrityError), transaction.atomic():
            MaintenanceCase.objects.filter(pk=inactive_case.pk).update(active=True)

    def test_concurrent_grouping_allows_only_one_active_case(self):
        first_case = confirm_triage(
            self.make_report(1), self.operator, "Elevator", "HIGH", self.location, "Maintenance", 60
        )
        second_case = confirm_triage(
            self.make_report(2), self.operator, "Elevator", "HIGH", self.location, "Maintenance", 60
        )
        target = self.make_report(3)
        barrier = threading.Barrier(2)
        outcomes = []

        def group(case_id):
            close_old_connections()
            try:
                barrier.wait()
                group_report(
                    MaintenanceCase.objects.get(pk=case_id),
                    IssueReport.objects.get(pk=target.pk),
                    get_user_model().objects.get(pk=self.operator.pk),
                )
            except ValidationError:
                outcomes.append("rejected")
            else:
                outcomes.append("linked")
            finally:
                close_old_connections()

        threads = [threading.Thread(target=group, args=(case.pk,)) for case in (first_case, second_case)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(sorted(outcomes), ["linked", "rejected"])
        self.assertEqual(CaseReport.objects.filter(report=target).count(), 1)
