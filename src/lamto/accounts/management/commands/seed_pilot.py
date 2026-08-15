"""Seed a deterministic non-production pilot fixture.

Usage:
  PILOT_ALLOW_FIXTURES=1 python manage.py seed_pilot --fixture

"""

from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from lamto.accounts.models import Building
from lamto.testing.factories import (
    PILOT_BUILDING_NAME,
    PILOT_EMAIL_DOMAIN,
    PILOT_PASSWORD,
    seed_pilot_world,
)


class Command(BaseCommand):
    help = "Seed deterministic pilot users and records for non-production scenarios."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture",
            action="store_true",
            help="Create (or reuse) the labeled pilot fixture world.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Create a new building even if a pilot building already exists.",
        )
        parser.add_argument(
            "--building-name",
            default=PILOT_BUILDING_NAME,
            help="Building display name for the fixture.",
        )

    def handle(self, *args, **options):
        if not options["fixture"]:
            raise CommandError("Pass --fixture to seed the pilot world.")
        if not getattr(settings, "PILOT_ALLOW_FIXTURES", False):
            raise CommandError(
                "Refusing to seed: PILOT_ALLOW_FIXTURES is false. "
                "Set PILOT_ALLOW_FIXTURES=1 only in non-production environments."
            )

        building_name = options["building_name"]
        existing = Building.objects.filter(name=building_name).first()
        if existing is not None and not options["force"]:
            self.stdout.write(
                self.style.WARNING(
                    f"Pilot building already exists (id={existing.pk}, name={building_name}). "
                    "Use --force to create another. Login emails use "
                    f"*@{PILOT_EMAIL_DOMAIN} with password from seed (not echoed here if reused)."
                )
            )
            self.stdout.write(
                "Idempotent reuse: no new rows created. Documented logins use prefix pilot-:\n"
                f"  pilot-management-1@{PILOT_EMAIL_DOMAIN}\n"
                f"  pilot-resident@{PILOT_EMAIL_DOMAIN}\n"
            )
            return

        seed = seed_pilot_world(building_name=building_name, password=PILOT_PASSWORD, email_prefix="pilot")

        self.stdout.write(self.style.SUCCESS("Pilot fixture created."))
        self.stdout.write(f"Building: {seed.building.name} (id={seed.building.pk})")
        self.stdout.write(f"Unit: {seed.unit.label}")
        if seed.report is not None:
            self.stdout.write(f"Sample report id: {seed.report.pk} (labeled TEST in text)")
        self.stdout.write("")
        self.stdout.write("Login identifiers (password not printed in production runbooks):")
        for number, user in enumerate(seed.management_users, 1):
            self.stdout.write(f"  management-{number:18} {user.email}")
        for number, user in enumerate(seed.residents, 1):
            self.stdout.write(f"  resident-{number:20} {user.email}")
