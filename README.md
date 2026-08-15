# LamTo

**From a resident's photo to a verifiable Maintenance Fund expense.**

![Django 5.2](https://img.shields.io/badge/Django-5.2-2f3a8f?style=flat-square)
![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-2f3a8f?style=flat-square)
![Flutter](https://img.shields.io/badge/Flutter-iOS%20%2B%20Android-2f3a8f?style=flat-square)
![Solidity 0.8.27](https://img.shields.io/badge/Solidity-0.8.27-2f3a8f?style=flat-square)

LamTo is a Vietnamese-first accountability layer for apartment maintenance.
Residents report problems; management records the decision, work, and payment
evidence; and the building publishes an append-only ledger that anyone can
verify. LamTo complements existing property-management and accounting systems.
It does not move or hold money.

## Why it matters

A maintenance complaint and the expense that eventually appears in a building's
fund are usually disconnected. LamTo creates one traceable chain:

```text
report -> human triage decision -> work -> proposal -> settlement -> public ledger
```

AI may suggest a category, urgency, deadline, or duplicate report, but a named
manager always makes the recorded decision. Published evidence is never edited
in place; corrections are appended.

## Hackathon demo

1. A resident reports a problem with a photo and location in the Flutter app.
2. LamTo proposes a triage result, and a manager accepts or overrides it in the
   web workspace.
3. The manager records the work, quotation, and transfer evidence, then
   publishes the fund entry.
4. The resident follows the expense back to the original report and verifies its
   evidence.
5. If published data is changed, LamTo reports `MISMATCH`; the anchored hash held
   by independent Besu nodes remains unchanged.

The key principle is **explain before proving**: people see a plain-language
status first, with hashes and signatures available as technical proof.

## What we built

- A Flutter resident app for reports, updates, ratings, and the published ledger.
- A server-rendered Django workspace for triage, cases, proposals, settlements,
  publication, and verification.
- Human-accountable AI triage with manual fallback.
- Private, virus-scanned evidence storage with hash-checked downloads.
- EIP-712 signed evidence anchored to a Solidity `EvidenceRegistry` on a
  four-validator Hyperledger Besu QBFT network.
- An idempotent outbox so a chain outage delays anchoring without losing or
  duplicating records.

```text
Flutter app ----> DRF API ----> Django + PostgreSQL
                                    |       |
Management web ---------------------+       +----> MinIO + ClamAV
                                    |
                                    +----> signed outbox
                                               |
                                               v
                                      EvidenceRegistry
                                      Besu QBFT network
```

## Quick start

Prerequisites: Docker, Python 3.12+, and
[`uv`](https://docs.astral.sh/uv/). Flutter stable is only required for the
resident app.

```bash
# Infrastructure and Python dependencies
docker compose up -d
uv sync

# Local demo environment: load defaults, generate a secret, and use local signing
set -a
source .env.example
set +a
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(64))')"
export DEBUG=1
export EVIDENCE_ANCHORING_BACKEND=disabled

# Database and synthetic demo data
POSTGRES_USER=lamto_owner POSTGRES_PASSWORD=lamto-owner \
  .venv/bin/python manage.py migrate
PILOT_ALLOW_FIXTURES=1 .venv/bin/python manage.py seed_pilot --fixture

# Management workspace: http://127.0.0.1:8000/s/
.venv/bin/python manage.py runserver 0.0.0.0:8000
```

Demo management login:

```text
pilot-management-1@pilot.lamto.test
pilot-test-secret
```

Run the resident app in another terminal:

```bash
cd app
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

Use `127.0.0.1` instead of `10.0.2.2` for an iOS simulator or Linux desktop.
The resident login is `pilot-resident@pilot.lamto.test` with the same demo
password. See [`app/README.md`](app/README.md) for other targets.

Local mode settles evidence as `LOCAL_SIGNED`. For the full on-chain pitch, use
the [four-laptop Besu demo guide](ops/hackathon-demo-4-laptops.md).

## Tests

```bash
POSTGRES_USER=lamto_owner POSTGRES_PASSWORD=lamto-owner \
  .venv/bin/python manage.py test lamto
.venv/bin/python -m pytest tests -v
(cd chain && forge test)
(cd app && flutter analyze && flutter test)
```

## Repository map

| Path | Purpose |
|---|---|
| `src/lamto/` | Django domain, API, Management workspace, and workers |
| `app/` | Flutter resident app |
| `chain/` | Solidity contract, Foundry tests, and Besu devnet |
| `docs/api/openapi-v1.yaml` | Resident API contract |
| `tests/` | Cross-cutting and end-to-end tests |

More detail: [product model](PRODUCT.md), [design system](DESIGN.md),
[pilot runbook](ops/pilot-runbook.md), and
[OpenAPI contract](docs/api/openapi-v1.yaml).

## Status

LamTo is a pre-pilot hackathon prototype. All included buildings, residents,
documents, and amounts are synthetic. Do not use the demo fixtures or credentials
in production.

No license has been published yet.
