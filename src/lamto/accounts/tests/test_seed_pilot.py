from io import StringIO

from django.core.management import call_command
from django.test import TestCase, override_settings

from lamto.accounts.models import Building, User
from lamto.testing.factories import (
    PILOT_BUILDING_NAME,
    PILOT_EMAIL_DOMAIN,
    seed_pilot_world,
)


class SeedPilotTests(TestCase):
    def test_seed_pilot_world_creates_fenikong_manager(self):
        seed = seed_pilot_world(
            building_name="Seed Test Building",
            create_sample_report=False,
        )
        self.assertEqual(len(seed.management_users), 1)
        self.assertEqual(seed.management_users[0].display_name, "Fenikong")
        self.assertEqual(len(seed.residents), 1)
        self.assertEqual(seed.residents[0].display_name, "Pilot Resident")
        self.assertEqual(seed.building.name, "Seed Test Building")

    @override_settings(PILOT_ALLOW_FIXTURES=True)
    def test_seed_pilot_command_fixture(self):
        out = StringIO()
        call_command("seed_pilot", "--fixture", stdout=out)
        manager = User.objects.get(email=f"pilot-management-1@{PILOT_EMAIL_DOMAIN}")
        self.assertEqual(manager.display_name, "Fenikong")
        resident = User.objects.get(email=f"pilot-resident@{PILOT_EMAIL_DOMAIN}")
        self.assertEqual(resident.display_name, "Pilot Resident")
        building = Building.objects.get(name=PILOT_BUILDING_NAME)
        self.assertIsNotNone(building)
