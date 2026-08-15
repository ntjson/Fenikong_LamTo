"""Ops entry point for expiring prepared-but-never-signed staff drafts.

Requires a DB role that owns the document tables (e.g. lamto_owner from
``.env.example``), because cleanup briefly disables append-only triggers.
Do not run under the restricted web writer role.
"""

from django.core.management.base import BaseCommand, CommandError

from lamto.web.staff_documents import cleanup_stale_prepared_ops


class Command(BaseCommand):
    help = (
        "Delete prepared-but-never-signed staff documents and draft "
        "proposals older than N hours, and purge their private-storage blobs. "
        "Requires table-owner DB credentials (lamto_owner) — not lamto_writer."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--older-than-hours",
            type=int,
            default=24,
            help="Age threshold in hours (default 24).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report candidates without deleting.",
        )

    def handle(self, *args, **options):
        hours = options["older_than_hours"]
        if hours < 1:
            raise CommandError("--older-than-hours must be >= 1")
        dry_run = bool(options["dry_run"])
        try:
            result = cleanup_stale_prepared_ops(
                older_than_hours=hours, dry_run=dry_run
            )
        except Exception as error:
            # Common when run as non-owner: insufficient privilege for ALTER TABLE.
            raise CommandError(
                f"cleanup failed (need table-owner DB role such as lamto_owner): {error}"
            ) from error

        if dry_run:
            self.stdout.write(
                "dry_run documents_candidate={documents_candidate} "
                "proposals_candidate={proposals_candidate}".format(**result)
            )
        else:
            self.stdout.write(
                "documents_deleted={documents_deleted} "
                "proposals_deleted={proposals_deleted} "
                "storage_purged={storage_purged}".format(**result)
            )
        return str(result)
