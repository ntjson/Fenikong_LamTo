"""Onboard a new building tenant: building, fund, locations, units, and
optional Management users. The fund opening balance stays in the
runbook — they need real humans and signed evidence.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from lamto.accounts.models import Building, ManagementMembership, Unit, User
from lamto.finance.models import MaintenanceFund
from lamto.maintenance.models import BuildingLocation

def _split(raw):
    return [part.strip() for part in raw.split(",") if part.strip()]


class Command(BaseCommand):
    help = "Create a building tenant with its fund, locations, units, and managers."

    def add_arguments(self, parser):
        parser.add_argument("--name", required=True, help="Building display name.")
        parser.add_argument("--timezone", default="Asia/Ho_Chi_Minh")
        parser.add_argument("--locations", default="", help="Comma-separated root location names.")
        parser.add_argument("--units", default="", help="Comma-separated unit labels.")
        parser.add_argument(
            "--managers",
            default="",
            help="Comma-separated emails; existing users get a ManagementMembership, "
            "missing users are created inactive-password.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        name = options["name"].strip()
        if not name:
            raise CommandError("--name is required.")
        if Building.objects.filter(name=name).exists():
            raise CommandError(f"Building {name!r} already exists.")
        building = Building.objects.create(name=name, timezone=options["timezone"])
        MaintenanceFund.objects.create(building=building)
        for location_name in _split(options["locations"]):
            BuildingLocation.objects.create(building=building, name=location_name)
        for unit_label in _split(options["units"]):
            Unit.objects.create(building=building, label=unit_label)
        for email in _split(options["managers"]):
            user = User.objects.filter(email=email).first()
            if user is None:
                user = User.objects.create_user(email=email, password=None, display_name=email)
            ManagementMembership.objects.create(user=user, building=building)

        self.stdout.write(self.style.SUCCESS(f"Building onboarded: {name} (id={building.pk})"))
        self.stdout.write(
            "Next steps (runbook): set manager passwords + TOTP, "
            "add resident occupancies (set phone numbers for phone "
            "login), then record and verify the fund opening balance."
        )
