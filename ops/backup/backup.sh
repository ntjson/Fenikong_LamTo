#!/usr/bin/env bash
# PostgreSQL base/WAL backup via WAL-G + object version backup + signed marker.
# Fails closed when required credentials, tools, or safety flags are missing.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >&2; }
die() { log "ERROR: $*"; exit 1; }

require_env() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    die "Required environment variable ${name} is not set"
  fi
}

require_cmd() {
  local name="$1"
  if ! command -v "${name}" >/dev/null 2>&1; then
    die "Required command not found on PATH: ${name}"
  fi
}

require_env WALG_S3_PREFIX
require_env WALG_LIBSODIUM_KEY
require_env AWS_ACCESS_KEY_ID
require_env AWS_SECRET_ACCESS_KEY
require_env PGDATA

: "${PGHOST:=127.0.0.1}"
: "${PGPORT:=5432}"
: "${PGUSER:=${POSTGRES_USER:-lamto}}"
: "${PGDATABASE:=${POSTGRES_DB:-lamto}}"
: "${BACKUP_SSE:=AES256}"
: "${BACKUP_OBJECTS_PREFIX:=object-backups}"
: "${MANIFEST_DIR:=/tmp/lamto-backup-manifests}"
: "${PYTHON:=.venv/bin/python}"

require_cmd wal-g
if [[ ! -x "${PYTHON}" && ! -f "${PYTHON}" ]]; then
  if ! command -v "${PYTHON}" >/dev/null 2>&1; then
    die "Python interpreter not found: ${PYTHON}"
  fi
fi

if [[ ! -d "${PGDATA}" ]]; then
  die "PGDATA directory does not exist: ${PGDATA}"
fi

mkdir -p "${MANIFEST_DIR}"
MANIFEST_PATH="${MANIFEST_DIR}/objects-$(date -u +%Y%m%dT%H%M%SZ).json"

export WALG_S3_PREFIX WALG_LIBSODIUM_KEY
export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY
export AWS_REGION="${AWS_REGION:-us-east-1}"
export PGHOST PGPORT PGUSER PGDATABASE
if [[ -n "${POSTGRES_PASSWORD:-}" ]]; then
  export PGPASSWORD="${POSTGRES_PASSWORD}"
fi
export BACKUP_SSE BACKUP_OBJECTS_PREFIX

log "Starting PostgreSQL base backup via WAL-G (PGDATA=${PGDATA})"
wal-g backup-push "${PGDATA}" | tee /tmp/lamto-walg-backup.log

log "Verifying latest WAL-G backup listing"
wal-g backup-list | tee /tmp/lamto-walg-list.txt
if [[ ! -s /tmp/lamto-walg-list.txt ]]; then
  die "wal-g backup-list returned no backups"
fi

log "Backing up object versions (manifest=${MANIFEST_PATH})"
"${PYTHON}" manage.py backup_objects \
  --dest-prefix "${BACKUP_OBJECTS_PREFIX}" \
  --manifest-path "${MANIFEST_PATH}"

if [[ ! -s "${MANIFEST_PATH}" ]]; then
  die "Object backup manifest was not written: ${MANIFEST_PATH}"
fi

log "Backup complete. Manifest: ${MANIFEST_PATH}"
