---
status: accepted
---

# Publish the price comparison to residents without anchoring it

Residents can now see how a published proposal's amount compared to the
Predicted price band. The comparison is stored against the ProposalVersion and
deliberately kept **outside** `_submission_snapshot()`, so it is not hashed into
`proposal_snapshot_hash` and never reaches the chain. A generated, non-repeatable
advisory number does not belong in an integrity chain whose entire claim is that
a hash proves a specific document.

## Consequences

**Old anchors keep verifying.** Adding a field inside the signed snapshot would
change `payloadHash` and strand every existing anchored event — the same break
`fund_code` caused, recorded in `MISSION.md`, which cost a full reseed. Nothing
needs reseeding for this change.

**The frozen reading is the one the manager acted on.** Comparing writes a
`PricePrediction` row and the create form carries only its id; publication
resolves that id server-side. Raw numbers in a hidden field would let a
resident-facing figure be edited by whoever submits the form. If the submitted
amount no longer matches the amount the prediction was made against, the stale
prediction is discarded and the proposal publishes with no comparison at all.

**No comparison, no display.** A manager who never presses compare publishes a
proposal without one, and both the workspace and the app show nothing rather than
computing something after the fact. Recomputing at read time was rejected: the
same proposal would show different percentages to different residents.

**Residents get a caveat the workspace does not.** The staff line is bare, as
staff can open the prediction record; the app carries `Ước tính bằng AI, chỉ để
tham khảo.` because a resident cannot check it.
