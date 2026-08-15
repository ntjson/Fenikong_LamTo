from django.core.management.base import BaseCommand

from lamto.config.worker import run_worker_cycle, run_worker_loop


class Command(BaseCommand):
    help = (
        "Run the unified database-backed worker (triage, outbox, "
        "publication finalization, integrity, notifications)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--once",
            action="store_true",
            help="Run a single cycle and exit.",
        )
        parser.add_argument(
            "--sleep",
            type=float,
            default=2.0,
            help="Base sleep seconds between cycles.",
        )
        parser.add_argument(
            "--jitter",
            type=float,
            default=1.0,
            help="Random jitter seconds added to sleep.",
        )
        parser.add_argument(
            "--max-cycles",
            type=int,
            default=None,
            help="Optional cycle cap (useful in tests).",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=50,
            help="Default batch limit for processors that accept limit.",
        )

    def handle(self, *args, **options):
        if options["once"]:
            result = run_worker_cycle(limit=options["limit"])
            for proc in result.processors:
                status = "ok" if proc.ok else "FAIL"
                self.stdout.write(
                    f"[{status}] {proc.name}: {proc.detail} (count={proc.count})"
                )
            return
        self.stdout.write("Starting unified worker loop…")
        run_worker_loop(
            sleep_seconds=options["sleep"],
            jitter_seconds=options["jitter"],
            max_cycles=options["max_cycles"],
        )
