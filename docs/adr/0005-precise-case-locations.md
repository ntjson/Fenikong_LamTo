---
status: accepted
---

# Record precise Case locations at triage

When confirming triage on an issue report, the Management account previously had
their location choice replaced with its root ancestor in the two-level location
tree (the area / floor), discarding the specific place (e.g. stairwell or lift)
the resident reported. Triage now preserves and records the exact Location
selected — whether an area or a place within one — and groups places under their
area in the triage picker.

## Consequences

The Case location `location_id` feeds the signed, anchored `case_snapshot_hash`
included in proposal evidence payloads. Old cases anchored the root ancestor,
while new cases anchor the exact chosen Location (a place or an area). Precision
was chosen over continuity: existing cases and previously anchored evidence
snapshots are untouched and are never recomputed or retro-anchored.
