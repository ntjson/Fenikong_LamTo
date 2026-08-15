#!/usr/bin/env bash
# Real-entry smoke: flutter run -d web-server of lib/main.dart (no emulator required).
# Usage: from app/  ./tool/smoke_web_run.sh [port]
set -euo pipefail
cd "$(dirname "$0")/.."
PORT="${1:-8765}"
LOG="${SMOKE_LOG:-/tmp/lamto-smoke-web.log}"

echo "Launching lib/main.dart on web-server :$PORT (log: $LOG)"
# timeout keeps CI/agent runs from hanging; local interactive use: drop timeout.
timeout 120s flutter run -d web-server \
  --web-hostname=127.0.0.1 \
  --web-port="$PORT" 2>&1 | tee "$LOG" &
PID=$!

ok=0
for _ in $(seq 1 60); do
  if curl -fsS "http://127.0.0.1:$PORT/" -o /tmp/lamto-smoke-index.html 2>/dev/null; then
    if grep -qE 'flutter_bootstrap|flutter\.js|main\.dart\.js' /tmp/lamto-smoke-index.html; then
      ok=1
      break
    fi
  fi
  sleep 2
done

if [ "$ok" -eq 1 ]; then
  code=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/main.dart.js" || echo 000)
  echo "SMOKE_OK=1 main.dart.js HTTP $code"
else
  echo "SMOKE_OK=0 (server did not serve Flutter bootstrap in time)" >&2
fi

kill -TERM "$PID" 2>/dev/null || true
wait "$PID" 2>/dev/null || true
exit $((1 - ok))
