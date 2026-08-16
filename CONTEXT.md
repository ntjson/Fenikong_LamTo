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

**Case location**:
The place a case is filed against, exactly what was selected at triage, an area
or a place within one.
_Avoid_: Incident location, issue location


**Management queue**:
The team responsible for handling a case, chosen from a fixed set. The triage
assistant proposes one and a Management account confirms or overrides it.
_Avoid_: Department, assigned team

**Started work**:
The moment a Management account picks a case up, recorded on the case itself.
Progress and completion are accounts of work, so neither is accepted before it.
It is also the last moment a spending proposal can be created: starting work
moves the reports on, and a case whose reports have moved on is no longer a
candidate for one.
_Avoid_: Work status, in-progress flag, work state

**Maintenance Fund**:
The single pool of money a building spends from. A building has exactly one,
so spending is never attributed to a chosen fund — there is nothing to choose.
_Avoid_: Fund code, funding source, general fund

**Expected schedule**:
The frozen resident-facing label derived from an expected start date and an
expected end date.
_Avoid_: Timeline, schedule range, planned dates

**Reference price set**:
The synthetic collection of past job prices a quotation can be compared
against. It describes jobs outside this building, commits no one, and covers
Elevator work only.
_Avoid_: Benchmark data, market data, price database, historical prices

**Reference price**:
One category's figure within the Reference price set — an average, the observed
range around it, and how many sample jobs it rests on. It is not the building's
own estimate and never becomes one, so nothing about it is "expected" in the
sense Expected schedule uses that word.
_Avoid_: Expected price, benchmark price, market rate, market average, fair
price

**Price comparison**:
The advisory reading a Management account asks for while entering a quotation:
whether the amount falls within the range of comparable jobs, and how far it
sits from the Reference price. Nothing is recorded, published, or anchored, so
it informs the spend without entering the evidence chain.
_Avoid_: Price check, price validation, price verdict, price approval

**Settlement**:
The record that a published proposal was paid, evidenced by the transfer proof
the Management account files. Filing that proof is the whole of settling; there
is no second confirming party.
_Avoid_: Payee acknowledgement, acknowledgement, two-sided settlement

**Transfer proof**:
The document a Management account files to evidence that a published proposal
was paid; filing it is what settles the proposal. Resident-facing Vietnamese:
Chứng từ thanh toán.
_Avoid_: Transfer evidence, payment voucher, Bằng chứng chuyển khoản,
Chứng từ chuyển khoản

**Evidence explorer**:
The public, unauthenticated page, reached by an opaque token, that shows one
proposal's anchored chain end to end — its published versions, its Settlement,
the signed anchor event of each, and the latest independent integrity
observation. The Resident app opens it in an external browser.
_Avoid_: Explorer, chain explorer, Blockscout
