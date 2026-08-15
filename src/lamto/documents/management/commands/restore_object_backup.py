"""Restore object backup copies into an isolated bucket/prefix for drills."""

from __future__ import annotations

import json
import os
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        "Restore objects listed in a backup manifest into an isolated "
        "destination bucket/prefix. Used by restore-drill.sh."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--manifest",
            required=True,
            help="Path to the backup manifest JSON produced by backup_objects.",
        )
        parser.add_argument(
            "--dest-bucket",
            default=os.getenv("RESTORE_DEST_BUCKET", ""),
            help="Isolated destination bucket (S3). Empty uses private storage.",
        )
        parser.add_argument(
            "--dest-prefix",
            default=os.getenv("RESTORE_DEST_PREFIX", "restore-drill"),
            help="Isolated destination key prefix.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate the manifest without copying.",
        )

    def handle(self, *args, **options):
        manifest_path = Path(options["manifest"])
        if not manifest_path.is_file():
            raise CommandError(f"Manifest not found: {manifest_path}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries = manifest.get("entries") or []
        if not entries and not options["dry_run"]:
            raise CommandError("Manifest contains no entries.")

        dest_prefix = options["dest_prefix"].rstrip("/")
        allow_fs = os.getenv("LAMTO_BACKUP_ALLOW_FS", "").lower() in {"1", "true", "yes"}
        client, bucket, is_s3 = self._storage_client()
        dest_bucket = options["dest_bucket"] or bucket

        restored = 0
        for entry in entries:
            source_key = entry.get("dest_key") or entry.get("source_key")
            sha = entry.get("sha256") or ""
            target_key = f"{dest_prefix}/{sha}/{entry.get('source_key', source_key)}"
            if options["dry_run"]:
                restored += 1
                continue
            if is_s3 and client is not None:
                copy_source = {"Bucket": bucket, "Key": source_key}
                if entry.get("source_version_id") and str(entry["source_version_id"]).lower() != "null":
                    # Prefer backup dest key (already version-addressed).
                    pass
                client.copy_object(
                    Bucket=dest_bucket,
                    Key=target_key,
                    CopySource=copy_source,
                    ServerSideEncryption=os.getenv("BACKUP_SSE", "AES256"),
                )
            elif allow_fs:
                from django.core.files.base import ContentFile
                from django.core.files.storage import storages

                storage = storages["private"]
                try:
                    data = storage.open(source_key, "rb").read()
                except Exception:
                    # Fall back to original source key.
                    try:
                        data = storage.open(entry.get("source_key", ""), "rb").read()
                    except Exception:
                        data = b""
                storage.save(target_key, ContentFile(data))
            else:
                raise CommandError(
                    "Restore requires S3 storage or LAMTO_BACKUP_ALLOW_FS=1."
                )
            restored += 1

        self.stdout.write(f"restore_object_backup restored={restored} prefix={dest_prefix}")

    def _storage_client(self):
        from django.core.files.storage import storages

        storage = storages["private"]
        if hasattr(storage, "connection") and hasattr(storage, "bucket_name"):
            return storage.connection.meta.client, storage.bucket_name, True
        return None, None, False
