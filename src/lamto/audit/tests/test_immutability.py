from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, connection, transaction
from django.test import TestCase

from lamto.accounts.models import (
    Building,
    ManagementMembership,
    ResidentOccupancy,
    Unit,
)
from lamto.audit.models import AuditEvent
from lamto.audit.services import record_audit


class AuditImmutabilityTests(TestCase):
    def make_board_membership(self):
        user = get_user_model().objects.create_user(
            email="board@example.test", password="secret", display_name="Board Member"
        )
        building = Building.objects.create(name="Minh An Residence")
        return ManagementMembership.objects.create(user=user, building=building)

    def test_audit_is_append_only(self):
        membership = self.make_board_membership()
        event = record_audit(
            actor=membership.user,
            membership=membership,
            action="proposal.create",
            target_type="ProposalVersion",
            target_id="42",
            result="allowed",
        )

        event.result = "changed"
        with self.assertRaises(ValueError):
            event.save()
        with self.assertRaises(ValueError):
            event.delete()

    def test_database_trigger_rejects_bulk_and_raw_mutation(self):
        membership = self.make_board_membership()
        event = record_audit(
            actor=membership.user,
            membership=membership,
            action="proposal.create",
            target_type="ProposalVersion",
            target_id="42",
            result="allowed",
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            AuditEvent.objects.filter(pk=event.pk).update(result="changed")
        with self.assertRaises(IntegrityError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM audit_auditevent WHERE id = %s", [event.pk])

    def test_database_trigger_rejects_raw_truncate(self):
        with self.assertRaises(IntegrityError) as context, transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE audit_auditevent")
        self.assertIn("audit events are append-only", str(context.exception))

    def test_record_audit_rejects_inactive_membership(self):
        membership = self.make_board_membership()
        membership.active = False
        membership.save(update_fields=["active"])

        with self.assertRaises(PermissionDenied):
            record_audit(
                actor=membership.user,
                membership=membership,
                action="proposal.create",
                target_type="ProposalVersion",
                target_id="42",
                result="allowed",
            )
        self.assertEqual(AuditEvent.objects.count(), 0)

    def test_record_audit_rejects_membership_owned_by_another_actor(self):
        membership = self.make_board_membership()
        other_actor = get_user_model().objects.create_user(
            email="other@example.test", password="secret", display_name="Other Actor"
        )

        with self.assertRaises(PermissionDenied):
            record_audit(
                actor=other_actor,
                membership=membership,
                action="proposal.create",
                target_type="ProposalVersion",
                target_id="42",
                result="allowed",
            )
        self.assertEqual(AuditEvent.objects.count(), 0)

    def test_staff_cannot_record_document_download_without_membership(self):
        membership = self.make_board_membership()

        with self.assertRaises(PermissionDenied):
            record_audit(
                actor=membership.user,
                membership=None,
                action="document.download",
                target_type="DocumentVersion",
                target_id="42",
                result="allowed",
                metadata={"occupancy_id": 1},
            )
        self.assertEqual(AuditEvent.objects.count(), 0)

    def test_unaffiliated_resident_can_record_document_download_with_active_occupancy(self):
        resident = get_user_model().objects.create_user(
            email="resident@example.test", password="secret", display_name="Resident"
        )
        building = Building.objects.create(name="Resident Building")
        occupancy = ResidentOccupancy.objects.create(
            user=resident, unit=Unit.objects.create(building=building, label="A-1")
        )

        event = record_audit(
            actor=resident,
            membership=None,
            action="document.download",
            target_type="DocumentVersion",
            target_id="42",
            result="denied",
            metadata={"occupancy_id": occupancy.id},
        )

        self.assertIsNone(event.membership_id)
