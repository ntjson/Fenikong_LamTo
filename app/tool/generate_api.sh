#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(cd .. && pwd)"
SCHEMA_REL="docs/api/openapi-v1.yaml"
OUT="packages/lamto_api"
rm -rf "$OUT"

generate_with_docker() {
  docker run --rm -u "$(id -u):$(id -g)" \
    -v "$ROOT:/local" \
    openapitools/openapi-generator-cli:v7.14.0 generate \
    -i "/local/$SCHEMA_REL" -g dart-dio -o "/local/app/$OUT" \
    --additional-properties=pubName=lamto_api,dateLibrary=core \
    --type-mappings=date=DateTime
}

generate_with_java() {
  npx --yes @openapitools/openapi-generator-cli@2.23.1 generate \
    -i "../$SCHEMA_REL" -g dart-dio -o "$OUT" \
    --additional-properties=pubName=lamto_api,dateLibrary=core \
    --type-mappings=date=DateTime
}

if command -v java >/dev/null 2>&1; then
  generate_with_java
elif command -v docker >/dev/null 2>&1; then
  generate_with_docker
else
  echo "ERROR: need java or docker to run openapi-generator" >&2
  exit 1
fi

( cd "$OUT" && dart pub get && dart run build_runner build --delete-conflicting-outputs )
shopt -s globstar nullglob
# built_value prints every property by default. Keep one-time credentials out of
# logs and crash reports while preserving their wire serialization.
perl -0pi -e "s/\n\s*\.\.add\('(password|statusToken)', \1\)//g" \
  "$OUT"/lib/src/model/registration_{create_request,submission}.g.dart
perl -0pi -e 's/[ \t]+$//mg; s/\n+\z/\n/' "$OUT"/**/*.dart "$OUT"/**/*.md
