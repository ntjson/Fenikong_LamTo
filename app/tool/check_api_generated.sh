#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
./tool/generate_api.sh
# Fail on any uncommitted change (including untracked) under packages/lamto_api.
if [ -n "$(git status --porcelain -- packages/lamto_api)" ]; then
  echo "ERROR: packages/lamto_api is stale. Run app/tool/generate_api.sh and commit." >&2
  git --no-pager status --short -- packages/lamto_api >&2
  git --no-pager diff --stat -- packages/lamto_api >&2 || true
  exit 1
fi
echo "OK: generated API client matches the committed schema."
