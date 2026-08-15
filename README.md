# LamTo

**The accountability layer for apartment maintenance.** LamTo links resident-reported
issues to traceable, independently verifiable Maintenance Fund spending — without
replacing the building's existing property-management or accounting systems.

![Django 5.2](https://img.shields.io/badge/Django-5.2-2f3a8f?style=flat-square)
![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-2f3a8f?style=flat-square)
![Flutter](https://img.shields.io/badge/Flutter-iOS%20%2B%20Android-2f3a8f?style=flat-square)
![Solidity 0.8.27](https://img.shields.io/badge/Solidity-0.8.27-2f3a8f?style=flat-square)
![Vietnamese-first](https://img.shields.io/badge/Locale-Vietnamese--first-2f3a8f?style=flat-square)
![WCAG 2.2 AA baseline](https://img.shields.io/badge/WCAG-2.2%20AA%20baseline-0f7a45?style=flat-square)

A resident photographs a leak in a stairwell. Months later, a line item appears in the
building's Maintenance Fund. In most buildings those two facts are unconnected, and no
resident can walk the distance between them. LamTo makes that distance walkable: every
published expenditure traces back through settlement, payment evidence, acceptance,
work, the triage decision, and the original reports — with the supporting documents
attached and the hashes verifiable by anyone holding the app.

Two principles shape the whole system:

**Explain before proving.** Plain-language status leads; hashes, event IDs, and
signatures live behind a disclosure labelled *Technical proof*. Nobody should need to
read a hash to understand what happened to their report.

**Attribute every judgement to a person.** AI triage produces a *suggestion* — a
category, urgency, deadline, likely duplicates, and any missing information. A manager
accepts or overrides it, and the record keeps both the suggestion and the differences
from it. Automation may propose. It never appears to have concluded.

---

## The accountability chain

```
 resident                management                        evidence
─────────────────────────────────────────────────────────────────────────────
 report        ──▶   triage suggestion
  photos,               │
  location              ├── needs info    ──▶  question returned to resident
                        ├── declined     ──▶  reason recorded
                        └── case opened
                              │
                        work updates      ──▶  before / after evidence
                              │                (append-only)
                        proposal          ──▶  frozen on publish, anchored   ①
                              │                quotation attached
                        settlement        ──▶  transfer evidence + payee     ⑩
                              │                acknowledgement, anchored
 ledger       ◀──       fund published    ──▶  balance, hashes, anchor state
  verify, rate                                 residents read the same ledger
```

A decline or an unanswered information request is part of that chain, not a dead end.
Published records are immutable; corrections append. Nothing published is ever edited
in place, and no screen offers an edit affordance over published evidence.

---

## Two surfaces, one evidence chain

|  | **Resident app** | **Management workspace** |
|---|---|---|
| **Platform** | Flutter — iOS + Android | Server-rendered Django, desktop-first |
| **Location** | `app/` | every route under `/s/` |
| **Language** | Vietnamese, keyed from machine codes | Vietnamese (`LANGUAGE_CODE = "vi"`) |
| **Does** | report issues, answer info requests, follow the work, rate a completed job, read the published ledger and announcements, pay bills, enrol face + plates | triage, cases, work updates, proposals, settlements, fund publication, hash and balance verification, registrations, gate review, bills, announcements, audit export |
| **Talks to** | `/api/v1/` — DRF + Knox tokens, contract at [`docs/api/openapi-v1.yaml`](docs/api/openapi-v1.yaml) | the database directly; full page navigation on every mutation |

Residents have no web surface. The app is the whole resident product, and no web screen
is designed as though a resident might arrive at it.

The application **does not enforce separation of duties** — one Management account can
perform every staff step. Where a building wants more than one person involved, managers
sign off offline and the workspace records the agreed result rather than re-running
the review. This is a deliberate choice, documented so nobody mistakes the workspace
for a four-eyes control.

---

## How evidence works

Published records are canonicalized, hashed, signed locally, then queued to a blockchain
outbox that anchors them to an `EvidenceRegistry` contract via an EIP-712 typed
signature. Every record carries an explicit **evidence level** rather than a boolean
"verified":

| Level | Meaning |
|---|---|
| `PENDING` | Queued; no signature settled yet. |
| `LOCAL_SIGNED` | Signed by the platform key and settled locally. Honest and complete when anchoring is switched off — never presented as chain-confirmed. |
| `CHAIN_CONFIRMED` | Anchored and confirmed on chain. |
| `MISMATCH` | The recomputed hash disagrees with what was anchored. Surfaced, never swallowed. |

Anchoring can be disabled entirely (`EVIDENCE_ANCHORING_BACKEND=disabled`), so every
evidence surface must render truthfully for a record that is locally signed and will
never be confirmed. The outbox is idempotent and lease-based: a chain outage delays
confirmation, it does not lose or duplicate records.

`chain/src/EvidenceRegistry.sol` is deliberately small — an owner-managed signer
allowlist, one `recordEvidence` entry point that rejects duplicates and bad signatures,
and an immutable mapping from event ID to `(payloadHash, previousHash, eventType,
signer, recordedAt)`. Event type `1` is a published proposal; `10` is a settlement.

---

## Quick start

**Prerequisites:** Docker, Python 3.12+, and — for the resident app — Flutter (stable).
Foundry is only needed if you want a live chain.

```bash
# 1 — infrastructure: Postgres 17, MinIO (private document storage), ClamAV
docker compose up -d

# 2 — environment
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(64))"   # paste as SECRET_KEY
```

`SECRET_KEY` is the only value that must be set — the rest of `.env.example` already
matches the compose services. For local work without a chain, also set
`EVIDENCE_ANCHORING_BACKEND=disabled`; evidence then settles as `LOCAL_SIGNED` and the
UI says so plainly.

```bash
# 3 — Python environment
uv sync                    # or: python -m venv .venv && .venv/bin/pip install -e ".[dev]"

# 4 — database and a synthetic pilot building
.venv/bin/python manage.py migrate
PILOT_ALLOW_FIXTURES=1 .venv/bin/python manage.py seed_pilot --fixture

# 5 — the Management workspace, at http://127.0.0.1:8000/s/
.venv/bin/python manage.py runserver 0.0.0.0:8000
```

`seed_pilot` prints login emails only; wallet private keys are never printed. Its
fixture data is obviously synthetic and must never be used outside a non-production
seed — `PILOT_ALLOW_FIXTURES` must stay false in production.

**The resident app:**

```bash
cd app
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

Android emulators reach the host at `10.0.2.2`; iOS simulators and Linux desktop use
`127.0.0.1`. The base URL is also editable at runtime from the login screen, so a
tunnel URL can be swapped without rebuilding. See [`app/README.md`](app/README.md) for
push setup and the integration-test harness.

**A live chain (optional):**

```bash
cd chain/besu && ./generate-network.sh      # writes Node-1..4 keys + .env.network
docker compose up -d                        # four-validator QBFT devnet, RPC on :8545

cd ../ && forge build && forge test
OWNER_ADDRESS=… PRIVATE_KEY=… forge script script/DeployEvidenceRegistry.s.sol \
  --rpc-url http://127.0.0.1:8545 --broadcast
# then set EVIDENCE_CONTRACT_ADDRESS in .env and allowlist the platform key:
.venv/bin/python manage.py authorize_platform_signer
```

The four validators stand for the parties with a stake in the record — management
board, property-management operator, resident representative, and auditor. Generated
keys, `.env.network`, and `Node-*` data directories are never committed.

---

## Repository layout

```
src/lamto/
├── accounts/        buildings, units, memberships, occupancy, MFA, tenancy guards
├── maintenance/     reports, AI triage + recorded decisions, cases, work, ratings
├── finance/         proposals, settlements, fund balance, integrity checks
├── evidence/        canonicalization, local signing, outbox, chain adapter
├── documents/       private object storage, virus scanning, insert-only versions
├── gate/            face + plate enrolment, readers, matching, retention purge
├── billing/         resident bills, QR references, issue / pay / void
├── notifications/   push delivery, announcements
├── audit/           audit log and export
├── api/             resident REST API v1 (36 endpoints, Knox tokens)
├── web/             Management workspace — views, forms, templates, static
├── testing/         factories and the deterministic pilot seed world
└── config/          settings, URL roots, unified worker

app/            Flutter resident app — Riverpod, Dio, generated `lamto_api` client
chain/          Foundry project — EvidenceRegistry, tests, Besu QBFT devnet
docs/api/       OpenAPI v1 contract (drf-spectacular)
docs/ops/       gate threshold calibration, push smoke checklist
ops/            pilot runbook, deployment checklist, Postgres role bootstrap
locale/vi/      Django Vietnamese message catalogue
tests/          cross-cutting end-to-end and tenant-isolation suites
```

Roughly 39k lines of Python, 23k of Dart, 105 migrations, and 108 test modules.

---

## Testing

```bash
# Django suites — per app, colocated under src/lamto/*/tests/
.venv/bin/python manage.py test lamto

# Cross-cutting end-to-end: normal flow, tamper + correction, blockchain outage,
# anchoring-disabled mode, role access, gate recognition, cross-building isolation
.venv/bin/python -m pytest tests -v

# Optional live browser run (otherwise the same paths run through a domain driver)
LAMTO_E2E_BROWSER=1 .venv/bin/python -m pytest tests/e2e -v

# Contract
cd chain && forge test

# Resident app
cd app && flutter analyze && flutter test
```

The end-to-end suite is written so that a missing Chromium degrades to a domain driver
exercising the same entry points, rather than silently skipping.

CI runs the Flutter app on every touch of `app/` or the OpenAPI contract — analyze,
test, and an **API client drift gate** that fails if the generated client no longer
matches the contract. A nightly workflow brings up compose, seeds the pilot world, and
runs the full resident happy path against a live backend on Linux desktop under `xvfb`.

---

## Configuration

Full reference in [`.env.example`](.env.example). The values that change behaviour most:

| Variable | Effect |
|---|---|
| `SECRET_KEY` | Required. Also the fallback for `EVIDENCE_WRITE_SECRET` and `GATE_EMBEDDING_KEY`. |
| `EVIDENCE_ANCHORING_BACKEND` | `besu` (default) or `disabled`. Disabled settles evidence locally and says so. |
| `BLOCKCHAIN_RPC_URL`, `EVIDENCE_CONTRACT_ADDRESS`, `PLATFORM_SIGNER_PRIVATE_KEY` | Chain round-trip. |
| `AI_TRIAGE_URL`, `AI_TRIAGE_TOKEN`, `AI_TRIAGE_MODEL` | OpenAI-compatible endpoint that must support `response_format={"type":"json_object"}`. Unset, or on any provider failure, reports route to manual triage — a first-class path, not a degraded one. |
| `PRIVATE_STORAGE_*`, `CLAMAV_*` | Private document storage and upload scanning. |
| `FIREBASE_CREDENTIALS`, `PUSH_ENABLED` | Leave empty and push degrades to a no-op. |
| `GATE_FACE_MATCH_THRESHOLD`, `GATE_MIN_FACE_SHARPNESS` | The shipped `0.38` is an **unvalidated starting point**. Calibrate against real reader captures before any pilot — see [`docs/ops/gate-threshold-calibration.md`](docs/ops/gate-threshold-calibration.md). |
| `GATE_EVENT_RETENTION_HOURS`, `GATE_ENROLLMENT_PHOTO_TTL_HOURS` | Hard retention ceilings, below. |
| `PILOT_ALLOW_FIXTURES` | Gates synthetic seed data. Must be false in production. |

Postgres uses four separated roles — `lamto_owner`, `lamto_app`, `lamto_writer`,
`lamto_service` — bootstrapped by [`ops/postgres-init.sql`](ops/postgres-init.sql).
Signed service transitions run on a dedicated executor role, and a few maintenance
commands deliberately refuse to run without owner credentials.

---

## Operations

One unified worker drains every queue, with each processor independently callable so a
failed adapter cannot stall the others:

```bash
.venv/bin/python manage.py run_worker    # triage, outbox, publication, integrity, notifications
```

| Command | Purpose |
|---|---|
| `process_triage` | Pending AI triage jobs. |
| `process_blockchain_outbox` | Idempotent anchoring of due evidence events. |
| `process_notifications` | Due in-app, email, and push deliveries. |
| `verify_integrity` | Append verification observations for published ledger entries; runs against a restored database for recovery drills. |
| `tenant_integrity` | Fails when any cross-building reference is inconsistent. |
| `purge_gate_data` | Deletes expired gate events and enrolment photos. |
| `close_completed_cases` | Closes completed cases past the 14-day rating window. |
| `onboard_building` | Creates a building with its fund, locations, units, and managers. |
| `authorize_platform_signer` | Allowlists the platform signer on the registry (owner key). |
| `calibrate_gate_threshold` | Scores labelled reader captures and prints a threshold sweep. |
| `backup_objects` / `restore_object_backup` | Version-addressed object backup with a signed marker; restore into an isolated bucket. |
| `cleanup_stale_prepared_ops` | Purges prepared-but-unsigned documents and draft proposals. |
| `deactivate_stale_devices` | Retires push devices unseen for N days. |

Runbooks: [`ops/pilot-runbook.md`](ops/pilot-runbook.md) walks one complete real case
end to end; [`ops/deployment-checklist.md`](ops/deployment-checklist.md) covers
bring-up.

---

## Privacy commitments

These are constraints on the design, not settings to be tuned upward:

- **Gate events are deleted whole** within roughly 24 hours. **No capture image is ever
  stored.** The enrolment review photo lives only until a manager decides or its TTL
  expires. The gate app writes no permanent audit rows — deliberately. No screen may
  imply a durable movement history exists, because none does.
- **Face embeddings are encrypted at rest** and dropped the moment an enrolment is
  rejected or expires.
- **Resident document downloads are fail-closed against an allowlist**: report photo,
  before photo, after photo, quotation, payment proof, resident bill. Invoices,
  contracts, and completion reports are staff-only. Links are signed and expire within
  five minutes. Residents download the *original* file — there is no redacted variant,
  so nothing a resident sees is a scrubbed stand-in for something they cannot see.

---

## Design and product documentation

- **[PRODUCT.md](PRODUCT.md)** — users, operating context, capabilities, constraints,
  product principles, and accessibility commitments.
- **[DESIGN.md](DESIGN.md)** — the design system. Creative north star (*"The Open
  Maintenance Desk"*), tokens, and the named rules the interface is held to: the
  Ten-Percent Rule, the Human Before Hash Rule, the Separate States Rule, the
  State-Only Motion Rule, and the rest.

The palette is restrained cool neutrals with sparse **Accountability Indigo**
(`#2F3A8F`) — institutional emphasis without crypto-purple spectacle — plus four
semantic roles that mean one thing each: verified green, attention amber, mismatch red,
open blue. The workspace is flat: no shadow vocabulary at all, structure carried by
spacing, a 1px border, and a tonal step. That is deliberate rather than unfinished.

The system explicitly rejects the crypto-trading dashboard, the interchangeable-card
admin template, the glossy property-management sales app, the surveillance command
center, and the playful hackathon prototype.

---

## Scope

**In scope:** issue reporting with photos; AI-assisted triage with a recorded human
decision; information requests and recorded declines; cases spanning multiple reports;
append-only work updates; completion ratings; case-linked and standalone spending
proposals with immutable publication; settlement with transfer evidence and payee
acknowledgement; fund balance, series, and per-record verification; a resident-facing
published ledger; virus-scanned insert-only documents with hash-checked download;
announcements; resident bills; push notifications; registration requests; gate face and
plate enrolment with manager review and retention purge; audit log and export;
management MFA and re-authentication.

**Not in scope, by design:** payment initiation, custody of funds, resident crypto
wallets, general property management, accounting, and building operations. LamTo owns
the maintenance-accountability workflow and supports the building's other systems
rather than absorbing them.

**State of the project:** pre-pilot. There are no customers, no pilot buildings, no
testimonials, no usage metrics, and no pricing — and none of those should be
manufactured. Every screen needing a building name, a resident, an amount, or a
document uses obviously synthetic sample data and says so. The gate face threshold is
uncalibrated. Success is defined as both happy paths completing end to end — a normal
maintenance case and a standalone spending proposal, each with independently verifiable
proposal and settlement anchors — with tampering detected, corrections append-only, and
recovery producing neither lost nor duplicate records.

---

## License

No license file has been added to this repository yet, so default exclusive copyright
applies. Add one before distributing.
