import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.utils import timezone

from lamto.finance.integrity import verify_published_entry
from lamto.finance.models import PublishedLedgerEntry, VerificationObservation


class Command(BaseCommand):
    help = (
        "Append verification observations for published ledger entries. "
        "Accepts Django's --database ALIAS; when run against a restored database "
        "it reads that alias and writes the drill report outside the restored DB."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Verify every published ledger entry.",
        )
        parser.add_argument(
            "--entry-id",
            type=int,
            action="append",
            dest="entry_ids",
            default=[],
            help="Verify a specific published entry id (repeatable).",
        )
        parser.add_argument(
            "--database",
            default="default",
            help="Database alias to read published entries from.",
        )
        parser.add_argument(
            "--report",
            type=str,
            default="",
            help="Optional filesystem path for a JSON drill report (outside DB).",
        )

    def handle(self, *args, **options):
        using = options.get("database") or "default"
        if using not in connections:
            raise CommandError(f"Unknown database alias {using!r}.")

        entry_ids = list(options.get("entry_ids") or [])
        if options.get("all"):
            entry_ids = list(
                PublishedLedgerEntry.objects.using(using)
                .order_by("pk")
                .values_list("pk", flat=True)
            )
        if not entry_ids and not options.get("all"):
            raise CommandError("Provide --all or at least one --entry-id.")

        results = []
        for entry_id in entry_ids:
            # Domain service reads/writes the selected alias; assert presence first.
            if not PublishedLedgerEntry.objects.using(using).filter(pk=entry_id).exists():
                raise CommandError(
                    f"Published entry {entry_id} not found on database {using!r}."
                )
            observation = verify_published_entry(entry_id, using=using)
            results.append(
                {
                    "entry_id": entry_id,
                    "observation_id": observation.pk,
                    "result": observation.result,
                    "observed_at": observation.observed_at.isoformat(),
                }
            )
            self.stdout.write(f"{entry_id}\t{observation.result}\t{observation.pk}")

        report_path = options.get("report") or ""
        if report_path:
            path = Path(report_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "generated_at": timezone.now().isoformat(),
                "database": using,
                "results": results,
                "mismatch_count": sum(
                    1
                    for row in results
                    if row["result"] == VerificationObservation.Result.MISMATCH
                ),
            }
            # Report always lands on the filesystem, never inside the restored DB.
            path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
            self.stdout.write(f"report={path}")
