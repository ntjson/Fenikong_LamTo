# LamTo

LamTo connects resident-facing service activity with the management work needed to resolve, account for, and publish that activity.

## Language

**Management workspace**:
The staff-facing web product whose routes live under `/s/`.
_Avoid_: Admin web page, admin portal

**Management account**:
A staff identity authorized to use the Management workspace.
_Avoid_: Management user, admin user

**Management session**:
An authenticated browser session through which a Management account uses the Management workspace.
_Avoid_: Admin session

**Resident app**:
The resident-facing mobile product for iOS and Android.
_Avoid_: Resident web page, resident portal

**Location**:
A named place inside a building that a report can be filed against, arranged as
a two-level tree — an area and the places within it. Names are unique only among
siblings, so the same lift or corridor name recurs on every floor.
_Avoid_: Area, zone, place

**Management queue**:
The team responsible for handling a case, chosen from a fixed set. The triage
assistant proposes one and a Management account confirms or overrides it.
_Avoid_: Department, assigned team

**Maintenance Fund**:
The single pool of money a building spends from. A building has exactly one,
so spending is never attributed to a chosen fund — there is nothing to choose.
_Avoid_: Fund code, funding source, general fund

**Settlement**:
The record that a published proposal was paid, evidenced by the transfer proof
the Management account files. Filing that proof is the whole of settling; there
is no second confirming party.
_Avoid_: Payee acknowledgement, acknowledgement, two-sided settlement

**Evidence explorer**:
The public, unauthenticated page, reached by an opaque token, that shows one
proposal's anchored chain end to end — its published versions, its Settlement,
the signed anchor event of each, and the latest independent integrity
observation. The Resident app opens it in an external browser.
_Avoid_: Explorer, chain explorer, Blockscout
