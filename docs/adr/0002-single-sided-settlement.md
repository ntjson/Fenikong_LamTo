---
status: accepted
---

# Settle a proposal on transfer evidence alone

Settlement used to require two documents: the transfer proof, then a "payee
acknowledgement" that a Management account uploaded on the payee's behalf. Both
sides were filed by the same party, so the second document evidenced nothing the
first did not; the `PAYEE_LINK` acknowledgement kind that would have made it
independent evidence was never built. Settlement is now single-sided — filing
the transfer proof settles the proposal — and the payee is no longer recorded at
all, since the proposal already carries a frozen, anchor-hashed contractor name.

## Consequences

The anchored payload becomes `settlement.v2`, dropping `payee_name`,
`bank_reference`, `ack_sha256` and `ack_recorded_at`, and renaming the remaining
timestamp to `settled_at`. Anchored `settlement.v1` events are not re-verifiable
by this code and no compatibility path is kept: all existing chain data is
demo data and is reseeded. The check constraint requiring both evidence sides is
dropped, as is the separate `transfer_recorded_at` timestamp that only existed
to distinguish the two steps.

The REST API breaks in place rather than versioning, because its only consumer
is the resident app built from this same repository.
