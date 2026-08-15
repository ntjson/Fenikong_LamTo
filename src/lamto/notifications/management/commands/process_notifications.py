from django.core.management.base import BaseCommand

from lamto.notifications.services import process_due_notifications


class Command(BaseCommand):
    help = "Process due in-app, email, and push notification deliveries."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=50,
            help="Maximum deliveries to process in one run.",
        )

    def handle(self, *args, **options):
        results = process_due_notifications(limit=options["limit"])
        self.stdout.write(f"processed {len(results)} notification delivery(ies)")
        for row in results:
            self.stdout.write(
                f"  pk={row.pk} channel={row.channel} status={row.status}"
            )
