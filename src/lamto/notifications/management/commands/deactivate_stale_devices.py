from django.core.management.base import BaseCommand

from lamto.notifications.devices import deactivate_stale_devices


class Command(BaseCommand):
    help = "Deactivate push devices unseen for N days (default 180; spec 7.2)."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=180)

    def handle(self, *args, **options):
        n = deactivate_stale_devices(days=options["days"])
        self.stdout.write(self.style.SUCCESS(f"deactivated={n}"))
