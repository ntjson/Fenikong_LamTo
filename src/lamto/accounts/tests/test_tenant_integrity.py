from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.test import TestCase

from lamto.accounts.models import Building, ResidentOccupancy, Unit
from lamto.maintenance.models import BuildingLocation, TriageDecision
from lamto.maintenance.reporting import submit_report


class TenantIntegrityCommandTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.building_a = Building.objects.create(name="Integrity A")
        cls.building_b = Building.objects.create(name="Integrity B")
        cls.unit_a = Unit.objects.create(building=cls.building_a, label="IA-1")
        cls.loc_a = BuildingLocation.objects.create(building=cls.building_a, name="IA Lobby")
        cls.loc_b = BuildingLocation.objects.create(building=cls.building_b, name="IB Lobby")
        cls.resident = get_user_model().objects.create_user(
            email="integrity@example.test", password="x", display_name="I"
        )
        ResidentOccupancy.objects.create(user=cls.resident, unit=cls.unit_a)
        cls.report = submit_report(cls.resident, cls.unit_a, "TEST integrity", cls.loc_a, [])

    def test_consistent_data_passes(self):
        out = StringIO()
        call_command("tenant_integrity", stdout=out)
        assert "all checks passed" in out.getvalue()

    def test_cross_building_decision_location_fails(self):
        TriageDecision.objects.create(
            report=self.report,
            operator=self.resident,
            category="c",
            urgency="LOW",
            location=self.loc_a,
            department="d",
            deadline_minutes=60,
        )
        # Bypass form scoping the way a bug would: plain FK, no composite key.
        TriageDecision.objects.filter(report=self.report).update(location=self.loc_b)
        with self.assertRaises(CommandError) as ctx:
            call_command("tenant_integrity")
        assert "triage_decision_location" in str(ctx.exception)
