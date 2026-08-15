# Product

<!-- impeccable:product-schema 1 -->

## Register

product

## Platform

adaptive

## Users

**Primary:** Vietnamese-speaking residents, on the mobile app only. They report apartment maintenance issues, answer requests for missing information, follow the case and the work, rate a completed job, and open the published Maintenance Fund ledger to see how spending connects back to the original reports and the supporting documents. They also read building announcements, pay resident bills, and enrol a face and vehicle plates for gate access. Design trade-offs favor mobile-native clarity, plain Vietnamese, and low cognitive load. Residents have no web surface; the app is the whole resident product.

**Secondary:** The building's Management user, on the web workspace only. One account carries the entire staff path: reviewing an AI triage suggestion and recording the decision, requesting missing information, declining with a recorded reason, opening a case and running the work with published progress, creating and publishing an immutable spending proposal, settling it against transfer evidence, publishing the ledger, verifying hashes and balances, approving resident registrations and gate enrolments, and issuing resident bills. The application does not enforce separation of duties. Where a building wants more than one person involved, managers meet and sign off offline, and the workspace records the agreed result rather than re-running the review. The workspace is denser and desktop-first because that is where the evidence is inspected.

Management access is password-only in every deployment (ADR 0001): no MFA enrollment or re-authentication step exists, and a successful password login opens the workspace directly. The authenticated Management session is persistent with a rolling 400-day lifetime and no inactivity timeout; each authenticated `/s/` request renews it. Logout is the normal termination path, while password changes, account disablement, browser cookie loss, server-side session deletion, and platform-level invalidation may still end it.

The resident app and the Management workspace share one accountability model and one evidence chain. Neither replaces the building's full maintenance, accounting, or property-management systems.

## Product Purpose

LamTo coordinates resident-reported maintenance cases and makes every published Maintenance Fund expenditure traceable from the original reports through triage, work, acceptance, payment evidence, and an independently verifiable resident-facing outcome.

Triage is assisted rather than automated. A suggestion proposes a category, urgency, interpreted location, responsible department, deadline, likely duplicates, and any missing information; a manager confirms or overrides it, and the recorded decision keeps both the suggestion and the differences from it. A report can also end without a case: declined with a stated reason, or held while missing information is requested. Those outcomes are part of the accountability record, not exceptions to it.

Published evidence is the real document. Residents download the original supporting files, gated by an explicit allowlist of document kinds. There is no redacted variant, so nothing a resident sees is a scrubbed stand-in for something they cannot see.

The MVP focuses on maintenance accountability and financial transparency. It does not initiate payments, hold funds, introduce resident crypto wallets, or replace the building's existing operational systems.

Success means both happy paths complete end to end: a normal maintenance case and a standalone spending proposal, each with independently verifiable proposal and settlement anchors. Residents can independently verify the evidence, tampering is detected, corrections remain append-only, and recovery creates neither lost nor duplicate records.

## Positioning

LamTo is the accountability layer for apartment maintenance, linking resident reports to traceable and independently verifiable Maintenance Fund spending without replacing existing property-management or accounting systems.

## Operating Context

**The maintenance path.** A resident submits an issue report with photos against a building location. The report moves through a fixed set of states — submitted, in review, needs information, declined, in progress, proposed, completed, closed — and an AI triage job produces a suggestion that a manager accepts or overrides as a recorded decision. Accepting opens a maintenance case, which may absorb more than one report. Work is published as append-only work updates carrying before and after evidence. The resident rates the completed job.

**The money path.** A spending proposal is created against a case, or standalone, with a quotation document attached; publishing it freezes it and anchors a proposal event. Settlement records the transfer evidence and anchors a settlement event; the recipient is the contractor frozen on the proposal (ADR 0002). The Maintenance Fund page carries the balance with opening, inflow, and outflow context, and offers per-record verification of hashes and balances. Residents read the same ledger from the app.

**The evidence chain.** Published records are canonicalized, hashed, signed locally, and queued to a blockchain outbox that anchors them to an `EvidenceRegistry` contract. Every record carries an explicit evidence level — pending, locally signed, chain confirmed, or mismatch — rather than a boolean "verified". Corrections are append-only; nothing published is edited in place.

**The building's day-to-day.** The workspace also carries the routine surrounding work: approving resident registration requests against units, publishing announcements, issuing resident bills against a bill document with a QR reference, and reviewing gate enrolments. The Action Inbox is the workspace's entry point: it groups what the Management user must act on next.

**The gate.** Reader devices at entrances recognize an enrolled resident face or vehicle plate and record a short-lived sighting. Retention is the defining constraint: gate events are deleted whole within roughly 24 hours, no capture image is ever stored, and the enrolment review photo lives only until a manager decides or its own TTL expires. The gate app writes no permanent audit rows, deliberately.

**Environments.** Postgres, MinIO/S3 for private document storage, ClamAV for upload scanning, and a Besu chain for anchoring, all runnable locally through `compose.yaml`. The Management user works at a desktop; residents work on a phone in a corridor or a lobby, often on a poor connection.

## Capabilities and Constraints

**Confirmed capabilities:** issue reporting with photos; AI-assisted triage with a recorded human decision; information requests and recorded declines; maintenance cases spanning multiple reports; append-only work updates recording cause and result; completion ratings; spending proposals (case-linked and standalone) with immutable publication; single-sided settlement evidenced by transfer proof (ADR 0002); Maintenance Fund balance, series, and per-record verification; a resident-facing published ledger; document upload with virus scanning, insert-only versions, and hash-checked download; announcements; resident bills with QR reference and issue/pay/void lifecycle; push notifications; resident registration requests; gate face and plate enrolment, manager review, reader devices, and a retention purge; an audit log and audit export; password-only Management access with persistent rolling 400-day sessions and no inactivity timeout (ADR 0001).

**Stack:** Django 5.2 on Python 3.12+ with Postgres, a server-rendered staff web workspace under `/s/`, and a Django REST Framework API (`docs/api/openapi-v1.yaml`, drf-spectacular, Knox tokens) consumed by a Flutter app targeting iOS and Android. Riverpod, Dio, and a generated `lamto_api` package on the client. Solidity `EvidenceRegistry` under `chain/`. InsightFace/ONNX for face embeddings, ML Kit text recognition for plates on device.

**Constraints that shape design:**

- Every web mutation is a full page navigation. There is no client-side rendering layer on the staff workspace, so there is no partial-update or optimistic-UI vocabulary available to it.
- Published records are immutable; corrections append. No screen may offer an edit affordance over published evidence.
- The application does not enforce separation of duties. One Management account can perform every staff step.
- Face embeddings are encrypted at rest and dropped the moment an enrolment is rejected or expires; gate events and review photos have hard TTLs. No design may imply a durable movement history exists.
- Resident document downloads are fail-closed against an allowlist: report photo, before photo, after photo, quotation, payment proof, resident bill. Invoices, contracts, and completion reports are staff-only. Download links are signed and expire within five minutes.
- Anchoring can be disabled (`EVIDENCE_ANCHORING_BACKEND=disabled`), so every evidence surface must render honestly when a record is locally signed and never confirmed.
- AI triage requires a configured model and gateway; when the provider fails or returns something malformed, the report routes to manual triage. Manual triage is a first-class path, not a degraded one.

**Terminology:** report, case, triage suggestion, triage decision, info request, work update, completion rating, proposal, settlement, Maintenance Fund, evidence level, anchor, occupancy, membership, building, unit, bill, announcement, gate enrolment, gate event.

**Explicitly out of scope:** payment initiation, custody of funds, resident crypto wallets, general property management, accounting, and building operations.

## Brand Commitments

- **Name:** LamTo.
- **Voice:** trustworthy, clear, rigorous. Neutral, evidence-led, and restrained. Explain status and evidence in plain language before exposing technical detail. Blockchain and AI appear only when they clarify verification or automation, never as identity or spectacle. An AI suggestion is always shown as a suggestion a person accepted or changed, never as a verdict the system reached.
- **Vietnamese-first:** resident-facing copy is Vietnamese, keyed from machine codes rather than server-supplied display strings. `app/lib/l10n/app_vi.arb` and `locale/vi/LC_MESSAGES/` are the sources.
- **Money is VND**, stored as integer đồng.

The visual world, palette, typography, and the aesthetic anti-references live in DESIGN.md.

## Evidence on Hand

**Real and usable:** the Vietnamese and English ARB catalogues (`app/lib/l10n/`) and the Django `.po` catalogue (`locale/vi/`); the OpenAPI contract at `docs/api/openapi-v1.yaml`; the triage system prompt and taxonomy in `src/lamto/maintenance/triage_prompt.py`; seed and demo fixtures in `src/lamto/testing/factories.py`; the `EvidenceRegistry` contract and its ABI under `chain/`; operational runbooks at `docs/ops/gate-threshold-calibration.md` and `docs/ops/push-smoke-checklist.md`; a Playwright end-to-end suite and Flutter integration tests covering both happy paths.

**Absent — must not be fabricated:** there are no customers, no pilot buildings, no testimonials, no case studies, no press, no usage or savings metrics, no pricing, no logo or brand mark, and no photography. There is no marketing surface at all. Any screen needing a building name, a resident name, an amount, or a document uses obviously synthetic sample data and says so.

## Product Principles

1. **Make accountability continuous.** Connect each published expenditure to the resident reports, work, decisions, documents, and verification that justify it. A decline or an unanswered information request is part of that chain, not a dead end.
2. **Explain before proving.** Lead with plain-language status and outcomes; reveal hashes, event IDs, signatures, and other technical proof only as supporting detail.
3. **Attribute every judgement to a person.** Show what was suggested, what was decided, and who decided it. Automation may propose; it never appears to have concluded.
4. **Support the building's systems.** Own the maintenance-accountability workflow without expanding into general property management, accounting, payment initiation, or building operations.
5. **Make responsibility legible.** Show who must act, what evidence they are reviewing, and what happens next without creating a surveillance atmosphere.
6. **Preserve trust under failure.** State whether data was saved, retain drafts where possible, expose pending or failed verification honestly, and give the next safe action.

## Accessibility & Inclusion

WCAG 2.2 AA is the baseline for the resident app and the Management workspace.

- Controls have clear labels, visible focus or platform equivalents, and never rely on color alone.
- Web supports keyboard and screen-reader use; native surfaces use platform accessibility APIs.
- Reduced-motion settings are respected, and essential meaning never depends on animation.
- Resident-facing copy is Vietnamese-first, keyed from machine codes rather than server-supplied display strings.
- Type and layout accommodate Vietnamese diacritics and system text scaling without clipping.
- Resident screens use generous touch targets, one primary action per screen, and no gesture-only affordances.
- Errors explain what happened, whether data was saved, and the next safe action.
