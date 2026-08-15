---
status: accepted
---

# Publish the evidence chain as a public explorer page

The inline technical-proof disclosures (raw hashes plus evidence-level badges)
are replaced, wherever an anchored proposal has a public token, by a badge and
a link to a new public, unauthenticated page — the Evidence explorer — that
visualizes the proposal's whole anchored chain: published versions through
Settlement as an accountability timeline, each step's anchor event with its
evidence level, payload hash and transaction hash, and the latest independent
integrity observation, read live from the chain at page load. Anchored
evidence only means something if a third party can check it without asking
permission, so the page is public under an opaque, unguessable token rather
than behind resident authentication.

## Considered options

Linking out to the dev-only Blockscout was rejected: it shows raw Besu
transactions, knows nothing about proposals or hash chains, and is unreachable
from residents' phones. A resident-authenticated explorer was rejected: the
login wall breaks "verify it yourself". A WebView inside the resident app was
rejected in favour of the external browser (new `url_launcher` dependency):
the resident sees the real URL and can share or open it on a PC, which is
itself part of the proof.

## Consequences

A Proposal mints a random `public_token` at first publish. Only post-feature
publications get one: pre-feature proposals keep the old raw-hash disclosure
permanently and every replaced screen branches on token presence. There is no
backfill — old bank-transfer proofs must not become public automatically —
while full parity (amount, contractor, approvers, step texts and the transfer
proof itself) is the chosen policy for whatever the explorer does show.

Transfer-proof documents are served content-addressed at
`/e/<token>/doc/<sha256>/`, the bytes re-verified against the anchored hash on
download, so the document URL is itself part of the proof.

The page is fully honest about failure states (PENDING, LOCAL_SIGNED,
MISMATCH, integrity MISMATCH/UNAVAILABLE) using the resident app's vocabulary,
degrades to stored state with an honest note when the chain is unreachable,
and is Vietnamese-only. Transaction hashes link out to a chain explorer only
when an optional setting provides one.

The case-detail "Technical proof" disclosure (triage-assistant confidence) and
the exception review stay untouched: they are not anchoring evidence.
