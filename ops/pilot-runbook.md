# Pilot runbook — normal accountability path

## Purpose

Prove one complete **real** normal maintenance/spend case end-to-end on the pilot
building: report → triage → proposal → work → acceptance → payment →
publication → resident ledger → integrity verification.

## Preconditions

- Non-production or controlled pilot environment only.
- `PILOT_ALLOW_FIXTURES=1` only when loading seed data; production must keep it false.
- PostgreSQL migrated; private object storage reachable; manager MFA enrolled.
- Gate face threshold and sharpness are explicitly set from a committed reader-capture calibration report. If FMR=0 and FNMR<=5% cannot both be met, run plate recognition only. See `docs/ops/gate-threshold-calibration.md`.
- Optional: Besu/outbox worker for live chain confirmation. If chain is paused or
  unavailable, a local signature still permits work start with
  **Pending blockchain anchoring**; publication waits for confirmed evidence.
- Seed (non-prod):

  ```bash
  export PILOT_ALLOW_FIXTURES=1
  .venv/bin/python manage.py seed_pilot --fixture
  ```

  Prints login emails only. Wallet private keys are never printed; optional
  `--wallet-env .env.pilot-wallets.local` writes keys to an ignored local file.

## Safety and ethics

- **No incident is manufactured.** Do not stage false hazards or delay real safety work.
- If a genuine emergency arises during the pilot window, follow the building's
  emergency procedures outside LamTo. Safety action is never delayed for pilot
  paperwork.

## Participants

| Participant | Responsibility |
|-------------|----------------|
| Resident | Report, inspect published ledger |
| Management user | Triage, create the work order and proposal, start and complete work, record transfer evidence and payee acknowledgement, publish the ledger, and verify hashes and balances |

One Management user performs the whole staff path. Managers meet, review, and
sign off offline before data entry; the application records the agreed result
rather than re-running the review. A building may have several Management
users, but no step requires a second person.

## Procedure (normal path)

1. Resident submits issue report with photo and location.
2. A manager confirms triage and creates a **paid** work order.
3. A manager submits a signed proposal (amount + quotation document).
4. A manager starts work (may show **Pending blockchain anchoring** until
   prerequisite outbox events confirm) and completes with cause/result photos.
5. A manager accepts work and records transfer evidence.
6. The same manager records the payee acknowledgement, settling the proposal.
7. Confirm chain/outbox events (`confirm_all_chain_events` in tests; worker in live).
8. A manager signs the publication snapshot; finalize after confirmation.
9. Resident opens latest ledger entry: actual cost, **Record verified**, and the
   original supporting documents.
10. A manager runs verification: document hashes match, chain events match (or local
    confirmed when registry unavailable), recomputed fund balance agrees.

## Automated proof

```bash
source /tmp/grok-goal-717590634826/implementer/env.sh  # or project env
.venv/bin/python manage.py test lamto.finance.tests.test_settlements -v 2
# optional browser suite (domain fallback if Chromium missing):
.venv/bin/python -m pytest tests/e2e -v
```

## Acceptance artifacts

Collect sign-off in `ops/acceptance-report-template.md` from the participating
Management users and resident.

## Tenant integrity (nightly)

```bash
.venv/bin/python manage.py tenant_integrity
```

Runs the cross-building consistency checks (spec 2.3). Non-zero exit means a
scoping bug wrote cross-tenant references; treat as a security incident.

## Anchoring mode switch

`EVIDENCE_ANCHORING_BACKEND` (environment) selects the evidence anchoring
transport: `besu` (default, chain round-trip) or `disabled` (local settlement,
`LOCAL_SIGNED`).

- Switching is an audited ops action, never a UI toggle: record who/why/when in
  the ops log, then change the environment value and restart web + worker.
- Events keep the status they settled with. A `LOCAL` event is never
  retro-anchored; a `CONFIRMED` event keeps its chain record.
- Events still `PENDING` at switch time settle with whichever backend is active
  when the worker next claims them.
- Verify after switching: `/s/ops/health/?format=json` reports
  `anchoring_backend`; new publications must show `LOCAL_SIGNED` (disabled) or
  `CHAIN_CONFIRMED` (besu) — never each other's wording, badges, or export values.
- Disabling never disables: wallet signatures on decisions, the outbox,
  canonical hashing, publication gates, idempotent fund posting, corrections,
  or document-hash integrity checks. Only the chain round-trip is skipped, and
  chain-dependent verification observations are skipped, not faked.

## Onboard a new building

```bash
.venv/bin/python manage.py onboard_building \
  --name "Toà nhà Example" \
  --locations "Sảnh, Thang máy 1, Hầm xe" \
  --units "A-101,A-102,A-103" \
  --managers "manager1@example.vn"
```

The command creates missing manager users with unusable passwords and gives
existing or new users a Management membership for the building. Then, per the
printed next steps: set manager passwords and TOTP, register signer wallets,
add resident occupancies (with phone numbers), and record and confirm the fund
opening balance. Run `manage.py tenant_integrity` afterwards.
