# Pilot acceptance report

**Building / pilot name:** _______________________  
**Date window:** _______________________  
**Environment:** (non-prod / pilot) _______________________  
**Build / commit SHA:** _______________________  

## Scope completed

| Scenario | Pass? | Evidence (test log / ticket / screenshot) |
|----------|-------|-------------------------------------------|
| Normal path (report → published ledger → integrity verification) | ☐ | |
| Chain paused: work pending anchor; publish blocked then retry same IDs | ☐ | |
| Transfer evidence and payee acknowledgement recorded by the manager | ☐ | |
| Proposal revision after signature requires a new publication | ☐ | |
| AI/email outage: report + action inbox authoritative | ☐ | |
| Cross-building object/file access denials | ☐ | |
| Tamper mismatch blocks publication and preserves the original evidence | ☐ | |
| Backup/outbox replay idempotent (no duplicate rows) | ☐ | |

## Automated results

```
# paste: manage.py test lamto.finance.tests.test_settlements -v 2
# paste: pytest tests/e2e (or e2e-env-fail.log if browser blocked)
# paste: verify_integrity / restore-drill notes if run
```

## Fund / integrity snapshot

- Opening / pre-pilot balance: ________ VND  
- Post normal-path balance: ________ VND  
- Duplicate financial/chain rows found: ________ (must be 0)  
- Unresolved high-severity findings: ________ (must be 0)  

## Sign-off

| Participant | Name | Signature | Date |
|-------------|------|-----------|------|
| Management participant | | | |
| Participating resident, or a person chosen by participating residents | | | |

## Attestations

- [ ] No safety incident was manufactured for the pilot.
- [ ] Safety action was never delayed for pilot or chain availability.
- [ ] Wallet private keys were not exported to shared channels.

**Overall decision:** ☐ Accept  ☐ Accept with observations  ☐ Reject  

**Notes:**  
_________________________________________________________________
_________________________________________________________________
