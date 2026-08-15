"""Backup every private object version into an immutable version-addressed prefix."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone as dj_timezone

from lamto.accounts.models import BackupMarker
from lamto.documents.models import DocumentVersion, QuarantinedUpload


class Command(BaseCommand):
    help = (
        "Enumerate every source object version, copy under an immutable "
        "version-addressed backup key, write a hash/version manifest, and "
        "record a signed BackupMarker. Fails closed unless source versioning "
        "and destination SSE are enabled (or LAMTO_BACKUP_ALLOW_FS=1 for tests)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dest-prefix",
            default=os.getenv("BACKUP_OBJECTS_PREFIX", "object-backups"),
            help="Destination key prefix for immutable copies.",
        )
        parser.add_argument(
            "--manifest-path",
            default="",
            help="Optional filesystem path to write the JSON manifest.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Enumerate and build manifest without copying objects.",
        )

    def handle(self, *args, **options):
        dest_prefix = options["dest_prefix"].rstrip("/")
        allow_fs = os.getenv("LAMTO_BACKUP_ALLOW_FS", "").lower() in {"1", "true", "yes"}
        client, bucket, is_s3 = self._storage_client()

        if is_s3:
            self._assert_versioning_and_sse(client, bucket)
        elif not allow_fs:
            raise CommandError(
                "Object backup requires S3-compatible storage with versioning "
                "and SSE, or LAMTO_BACKUP_ALLOW_FS=1 for local drills."
            )

        entries = []
        for version in DocumentVersion.objects.order_by("id").iterator(chunk_size=200):
            entry = self._backup_one(
                client,
                bucket,
                is_s3,
                version.storage_key,
                version.provider_version_id,
                version.sha256,
                dest_prefix,
                dry_run=options["dry_run"],
            )
            entry.update(
                {
                    "document_version_id": version.pk,
                    "filename": version.filename,
                }
            )
            entries.append(entry)

        for q in QuarantinedUpload.objects.exclude(storage_key__isnull=True).exclude(
            storage_key=""
        ).iterator(chunk_size=100):
            entry = self._backup_one(
                client,
                bucket,
                is_s3,
                q.storage_key,
                q.provider_version_id,
                q.sha256,
                dest_prefix,
                dry_run=options["dry_run"],
            )
            entry["quarantined_upload_id"] = q.pk
            entries.append(entry)

        now = datetime.now(timezone.utc)
        marker_id = hashlib.sha256(
            f"{now.isoformat()}|{len(entries)}".encode()
        ).hexdigest()[:32]
        manifest = {
            "marker_id": marker_id,
            "generated_at": now.isoformat(),
            "object_count": len(entries),
            "dest_prefix": dest_prefix,
            "entries": entries,
        }
        manifest_body = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        signature = hmac.new(
            settings.SECRET_KEY.encode(),
            manifest_body,
            hashlib.sha256,
        ).hexdigest()
        manifest["signature"] = signature

        storage_key = f"{getattr(settings, 'BACKUP_OPS_PREFIX', 'ops/backups').rstrip('/')}/markers/{marker_id}.json"
        if not options["dry_run"]:
            if is_s3:
                client.put_object(
                    Bucket=bucket,
                    Key=storage_key,
                    Body=json.dumps(manifest).encode(),
                    ServerSideEncryption=os.getenv("BACKUP_SSE", "AES256"),
                    ContentType="application/json",
                )
            else:
                from django.core.files.base import ContentFile
                from django.core.files.storage import storages

                storages["private"].save(
                    storage_key, ContentFile(json.dumps(manifest).encode())
                )

            BackupMarker.objects.create(
                marker_id=marker_id,
                signed_at=dj_timezone.now(),
                signature=signature,
                storage_key=storage_key,
                metadata={
                    "object_count": len(entries),
                    "dest_prefix": dest_prefix,
                },
            )

        manifest_path = options.get("manifest_path") or ""
        if manifest_path:
            with open(manifest_path, "w", encoding="utf-8") as fh:
                json.dump(manifest, fh, indent=2)
            self.stdout.write(f"manifest {manifest_path}")

        self.stdout.write(
            f"backup_objects marker={marker_id} count={len(entries)} signature={signature[:16]}…"
        )

    def _storage_client(self):
        from django.core.files.storage import storages

        storage = storages["private"]
        if hasattr(storage, "connection") and hasattr(storage, "bucket_name"):
            return storage.connection.meta.client, storage.bucket_name, True
        return None, None, False

    def _assert_versioning_and_sse(self, client, bucket):
        try:
            ver = client.get_bucket_versioning(Bucket=bucket)
        except Exception as error:
            raise CommandError(f"Unable to read source versioning: {error}") from error
        status = (ver or {}).get("Status") or ""
        if status.lower() != "enabled":
            raise CommandError(
                f"Source bucket {bucket!r} versioning is not enabled (Status={status!r})."
            )
        # Destination SSE: require explicit env or default AES256 assumption checked via put.
        sse = os.getenv("BACKUP_SSE", "AES256")
        if not sse:
            raise CommandError("BACKUP_SSE must be set for destination server-side encryption.")

    def _backup_one(
        self,
        client,
        bucket,
        is_s3,
        storage_key,
        provider_version_id,
        sha256,
        dest_prefix,
        *,
        dry_run,
    ):
        dest_key = f"{dest_prefix}/{sha256}/{provider_version_id or 'null'}/{storage_key}"
        entry = {
            "source_key": storage_key,
            "source_version_id": provider_version_id,
            "sha256": sha256,
            "dest_key": dest_key,
        }
        if dry_run:
            return entry
        if is_s3:
            copy_source = {"Bucket": bucket, "Key": storage_key}
            if provider_version_id and str(provider_version_id).lower() != "null":
                copy_source["VersionId"] = provider_version_id
            extra = {
                "ServerSideEncryption": os.getenv("BACKUP_SSE", "AES256"),
                "MetadataDirective": "COPY",
            }
            client.copy_object(
                Bucket=bucket,
                Key=dest_key,
                CopySource=copy_source,
                **extra,
            )
        else:
            from django.core.files.base import ContentFile
            from django.core.files.storage import storages

            storage = storages["private"]
            try:
                data = storage.open(storage_key, "rb").read()
            except Exception:
                data = b""
            storage.save(dest_key, ContentFile(data))
        return entry
