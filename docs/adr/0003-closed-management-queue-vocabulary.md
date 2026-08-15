---
status: accepted
---

# Make the Management queue a closed vocabulary

The queue that handles a case was free text, deliberately: the triage assistant
proposed a team name and the operator could type anything. That made the value
untranslatable, so a Vietnamese workspace showed English queue names, and it let
prompt drift split one team across several spellings. The Management queue is now
a closed set of codes with translated labels, chosen the same way `CaseCategory`
already was, and the assistant returns a code rather than prose.

## Consequences

Existing free-text values are migrated lossily — recognised names map to codes,
everything else becomes `GENERAL` — which is acceptable only because the database
is reseeded for the demo. The underlying column is renamed from `department` to
`management_queue` so the model matches the label the workspace has always shown.
Operators lose the ability to invent a queue on the spot; adding one is now a code
change and a migration.
