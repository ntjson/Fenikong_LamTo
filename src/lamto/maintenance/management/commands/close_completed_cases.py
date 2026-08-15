from django.core.management.base import BaseCommand

from lamto.maintenance.cases import close_expired_completed_cases


class Command(BaseCommand):
    help = "Close completed cases whose 14-day rating window has passed."

    def handle(self, *args, **options):
        closed = close_expired_completed_cases()
        self.stdout.write(self.style.SUCCESS(f"Closed {closed} case(s)."))
