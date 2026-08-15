# Backup and restore drill

## Purpose

- **PostgreSQL**: base backups and continuous WAL via [WAL-G](https://github.com/wal-g/wal-g) into a private S3 prefix (`WALG_S3_PREFIX`), encrypted with `WALG_LIBSODIUM_KEY`.
- **Objects**: `manage.py backup_objects` copies every `DocumentVersion` / quarantined object under an immutable version-addressed key, writes a signed hash/version manifest, and records a `BackupMarker` for the ops health panel.
- **Drill**: `restore-drill.sh` restores into an isolated database name and isolated object prefix, runs integrity verification, exports a report, then destroys isolated resources.

Stakeholder wallet private keys are **never** on the server, in backups, or in support workflows.

## Required environment

| Variable | Role |
|----------|------|
| `WALG_S3_PREFIX` | Private S3 URI for WAL-G |
| `WALG_LIBSODIUM_KEY` | WAL-G encryption key |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | Private ops credentials |
| `PGDATA` | PostgreSQL data directory for `backup-push` / `backup-fetch` |
| `PGHOST` `PGPORT` `PGUSER` `PGDATABASE` | Connection defaults |
| `BACKUP_SSE` | Destination SSE algorithm (default `AES256`) |
| `BACKUP_OBJECTS_PREFIX` | Immutable object backup prefix |
| `MANIFEST_PATH` | (restore) path to `backup_objects` manifest |
| `RESTORE_DB_NAME` | Isolated database (default `lamto_restore_drill`) |
| `RESTORE_DEST_PREFIX` | Isolated object prefix |
| `LAMTO_BACKUP_ALLOW_FS` | `1` allows filesystem storage in local tests only |

Commands **fail closed** unless source bucket versioning is enabled and destination SSE is configured (or `LAMTO_BACKUP_ALLOW_FS=1` for local filesystem drills).

## Daily backup

```bash
export WALG_S3_PREFIX=s3://lamto-ops/walg/
export WALG_LIBSODIUM_KEY=...
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export PGDATA=/var/lib/postgresql/data
bash ops/backup/backup.sh
```

## Restore drill

```bash
export MANIFEST_PATH=/tmp/lamto-backup-manifests/objects-….json
# plus WAL-G / AWS / PG vars as above
bash ops/backup/restore-drill.sh
```

### Dry-run (CI / no live WAL-G)

Exercises the isolated verification loop structure with stubs. Does **not** claim live S3/WAL-G success. Live mode still **fail-closed** without `WALG_*`.

```bash
bash ops/backup/restore-drill.sh --dry-run
# or: RESTORE_DRILL_DRY_RUN=1 bash ops/backup/restore-drill.sh
```

Steps asserted: isolated DB name, WAL-G fetch (stubbed), `migrate --check` against Django `restored` alias (`DJANGO_RESTORE_DB_NAME`), object restore (stubbed), `verify_integrity --database restored`, manifest hash/count/balance comparison, outbox deferral note, report export, destroy.

Schedule live restore drills on a fixed cadence (see `ops/deployment-checklist.md`).

## Django commands

```bash
.venv/bin/python manage.py backup_objects --manifest-path /tmp/manifest.json
.venv/bin/python manage.py restore_object_backup --manifest /tmp/manifest.json --dest-prefix restore-drill
.venv/bin/python manage.py verify_integrity --all --database default --report /tmp/drill.json
```
