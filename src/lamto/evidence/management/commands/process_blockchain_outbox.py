from django.core.management.base import BaseCommand

from lamto.evidence.worker import process_due_outbox_events, process_outbox_event


class Command(BaseCommand):
    help = "Process due blockchain outbox events idempotently."

    def add_arguments(self, parser):
        parser.add_argument(
            "--event-id",
            type=int,
            default=None,
            help="Process a single outbox primary key instead of claiming due rows.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="Maximum number of due events to process in one run.",
        )

    def handle(self, *args, **options):
        event_id = options["event_id"]
        if event_id is not None:
            result = process_outbox_event(event_id)
            self.stdout.write(
                f"processed event pk={result.pk} status={result.status} "
                f"tx={result.transaction_hash or '-'}"
            )
            return
        results = process_due_outbox_events(limit=options["limit"])
        self.stdout.write(f"processed {len(results)} outbox event(s)")
        for result in results:
            self.stdout.write(
                f"  pk={result.pk} status={result.status} tx={result.transaction_hash or '-'}"
            )
