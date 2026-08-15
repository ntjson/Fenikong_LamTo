from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from lamto.accounts.models import (
    Building,
    ResidentOccupancy,
    Unit,
)
from lamto.audit.models import AuditEvent
from lamto.documents.models import Document, DocumentVersion
from lamto.maintenance.models import BuildingLocation, IssueReport, TriageJob
from lamto.maintenance.reporting import submit_report


class ReportSubmissionTests(TestCase):
    def make_resident_unit_and_location(self):
        building = Building.objects.create(name="Minh An Residence")
        resident = get_user_model().objects.create_user(
            email="resident@example.test", password="secret", display_name="Resident"
        )
        unit = Unit.objects.create(building=building, label="A-1")
        ResidentOccupancy.objects.create(user=resident, unit=unit)
        location = BuildingLocation.objects.create(building=building, name="Lift 2")
        return resident, unit, location

    def test_submission_commits_report_and_pending_triage_job(self):
        resident, unit, location = self.make_resident_unit_and_location()

        report = submit_report(resident, unit, "Elevator shakes", location, [])

        self.assertEqual(IssueReport.objects.get(id=report.id).text, "Elevator shakes")
        self.assertEqual(TriageJob.objects.get(report=report).status, TriageJob.Status.PENDING)

    def test_location_direct_save_rejects_cross_building_parent(self):
        first = Building.objects.create(name="First Building")
        second = Building.objects.create(name="Second Building")
        parent = BuildingLocation.objects.create(building=first, name="Basement")

        with self.assertRaises(IntegrityError), transaction.atomic():
            BuildingLocation.objects.create(building=second, parent=parent, name="Lift 2")

    def test_location_direct_save_rejects_self_parent(self):
        building = Building.objects.create(name="First Building")
        location = BuildingLocation.objects.create(building=building, name="Basement")
        location.parent = location

        with self.assertRaises(IntegrityError), transaction.atomic():
            location.save(update_fields=["parent"])

        location.refresh_from_db()
        self.assertIsNone(location.parent_id)

    def test_location_update_rejects_ancestor_cycle(self):
        building = Building.objects.create(name="First Building")
        root = BuildingLocation.objects.create(building=building, name="Basement")
        child = BuildingLocation.objects.create(building=building, parent=root, name="Lift 2")

        with self.assertRaises(IntegrityError), transaction.atomic():
            BuildingLocation.objects.filter(pk=root.pk).update(parent=child)

        root.refresh_from_db()
        self.assertIsNone(root.parent_id)

    def test_location_building_update_rejects_existing_children(self):
        building = Building.objects.create(name="First Building")
        other_building = Building.objects.create(name="Second Building")
        root = BuildingLocation.objects.create(building=building, name="Basement")
        BuildingLocation.objects.create(building=building, parent=root, name="Lift 2")

        with self.assertRaises(IntegrityError), transaction.atomic():
            BuildingLocation.objects.filter(pk=root.pk).update(building=other_building)

        root.refresh_from_db()
        self.assertEqual(root.building_id, building.id)

    def test_location_path_label_is_deterministic(self):
        building = Building.objects.create(name="First Building")
        basement = BuildingLocation.objects.create(building=building, name="Basement")
        lift = BuildingLocation.objects.create(building=building, parent=basement, name="Lift 2")

        self.assertEqual(lift.path_label, "First Building / Basement / Lift 2")

    def test_submission_rejects_inactive_location_ancestor(self):
        resident, unit, location = self.make_resident_unit_and_location()
        parent = BuildingLocation.objects.create(building=unit.building, name="Basement")
        location.parent = parent
        location.save(update_fields=["parent"])
        parent.active = False
        parent.save(update_fields=["active"])

        with self.assertRaisesMessage(ValidationError, "active"):
            submit_report(resident, unit, "Elevator shakes", location, [])

    def test_submission_snapshots_current_location_hierarchy(self):
        resident, unit, location = self.make_resident_unit_and_location()
        stale_location = BuildingLocation.objects.get(pk=location.pk)
        parent = BuildingLocation.objects.create(building=unit.building, name="Basement")
        BuildingLocation.objects.filter(pk=location.pk).update(parent=parent)

        report = submit_report(resident, unit, "Elevator shakes", stale_location, [])

        self.assertEqual(
            report.location_path_snapshot,
            "Minh An Residence / Basement / Lift 2",
        )

    def test_submission_rejects_inactive_occupancy(self):
        resident, unit, location = self.make_resident_unit_and_location()
        ResidentOccupancy.objects.filter(user=resident, unit=unit).update(active=False)

        with self.assertRaisesMessage(PermissionDenied, "Active occupancy"):
            submit_report(resident, unit, "Elevator shakes", location, [])

    def test_submission_rejects_photo_from_another_building(self):
        resident, unit, location = self.make_resident_unit_and_location()
        other_building = Building.objects.create(name="Other Building")
        photo = DocumentVersion.objects.create(
            document=Document.objects.create(
                building=other_building, kind=Document.Kind.REPORT_PHOTO
            ),
            version=1,
            storage_key="report-photo-other-building",
            provider_version_id="version-1",
            filename="photo.jpg",
            content_type="image/jpeg",
            byte_size=1,
            sha256="0" * 64,
            uploader=resident,
        )

        with self.assertRaises(ValidationError):
            submit_report(resident, unit, "Elevator shakes", location, [photo])

    def test_submission_rejects_another_residents_same_building_photo(self):
        resident, unit, location = self.make_resident_unit_and_location()
        other_resident = get_user_model().objects.create_user(
            email="other-resident@example.test", password="secret", display_name="Other Resident"
        )
        ResidentOccupancy.objects.create(
            user=other_resident,
            unit=Unit.objects.create(building=unit.building, label="A-2"),
        )
        photo = DocumentVersion.objects.create(
            document=Document.objects.create(
                building=unit.building, kind=Document.Kind.REPORT_PHOTO
            ),
            version=1,
            storage_key="report-photo-other-resident",
            provider_version_id="version-1",
            filename="photo.jpg",
            content_type="image/jpeg",
            byte_size=1,
            sha256="1" * 64,
            uploader=other_resident,
        )

        with self.assertRaises(ValidationError):
            submit_report(resident, unit, "Elevator shakes", location, [photo])

        self.assertEqual(IssueReport.objects.count(), 0)

    def test_submission_accepts_owned_current_report_photo(self):
        resident, unit, location = self.make_resident_unit_and_location()
        photo = DocumentVersion.objects.create(
            document=Document.objects.create(
                building=unit.building, kind=Document.Kind.REPORT_PHOTO
            ),
            version=1,
            storage_key="report-photo-owned",
            provider_version_id="version-1",
            filename="photo.jpg",
            content_type="image/jpeg",
            byte_size=1,
            sha256="2" * 64,
            uploader=resident,
        )

        report = submit_report(resident, unit, "Elevator shakes", location, [photo])

        self.assertEqual(list(report.photos.values_list("version_id", flat=True)), [photo.id])

    def test_submission_attributes_audit_to_resident_without_membership(self):
        resident, unit, location = self.make_resident_unit_and_location()

        report = submit_report(resident, unit, "Elevator shakes", location, [])

        self.assertTrue(IssueReport.objects.filter(pk=report.pk).exists())
        self.assertTrue(TriageJob.objects.filter(report=report).exists())
        audit = AuditEvent.objects.get(action="report.submit", target_id=str(report.pk))
        self.assertEqual(audit.actor_id, resident.id)
        self.assertIsNone(audit.membership_id)
