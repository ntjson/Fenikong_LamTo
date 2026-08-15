---
name: LamTo
description: Accountability layer for apartment maintenance across a resident mobile app and a Management web workspace.
colors:
  primary: "#2f3a8f"
  primary-hover: "#273178"
  primary-active: "#202864"
  on-primary: "#ffffff"
  focus: "#0b57d0"
  focus-on-dark: "#ffffff"
  neutral-bg: "#e9edf6"
  surface: "#ffffff"
  surface-muted: "#eef1f8"
  ink: "#1c2434"
  muted: "#5b6577"
  border: "#a3aec6"
  success: "#0f7a45"
  success-bg: "#e7f6ee"
  warning: "#8a5c00"
  warning-bg: "#fff6dd"
  error: "#b42318"
  error-bg: "#fef3f2"
  info: "#175cd3"
  info-bg: "#eff8ff"
  staff-nav: "#1c2434"
  dark-primary: "#8a97e8"
  dark-on-primary: "#12141c"
  dark-bg: "#12141c"
  dark-surface: "#1c2030"
  dark-ink: "#e8eaf2"
  dark-muted: "#a0a8b8"
  dark-border: "#3a4158"
  dark-success: "#66d19e"
  dark-success-bg: "#163425"
  dark-warning: "#e2b44c"
  dark-warning-bg: "#362c10"
  dark-error: "#f2938c"
  dark-error-bg: "#3b1b18"
  dark-info: "#7cb5f5"
  dark-info-bg: "#14273d"
typography:
  body:
    fontFamily: "system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
  headline:
    fontFamily: "system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1.25
  title:
    fontFamily: "system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1.15rem"
    fontWeight: 700
    lineHeight: 1.25
  label:
    fontFamily: "system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "0.85rem"
    fontWeight: 600
    lineHeight: 1.3
  amount:
    fontFamily: "system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 700
    lineHeight: 1.2
    fontFeature: "tabular-nums"
  hash:
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "0.85rem"
    fontWeight: 400
    lineHeight: 1.4
rounded:
  sm: "8px"
  md: "10px"
  lg: "12px"
  pill: "999px"
spacing:
  1: "0.25rem"
  2: "0.5rem"
  3: "0.75rem"
  4: "1rem"
  5: "1.5rem"
  6: "2rem"
  touch-web: "44px"
  touch-ios: "44pt"
  touch-android: "48dp"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.md}"
    padding: "0.65rem 1rem"
    height: "{spacing.touch-web}"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
    textColor: "{colors.on-primary}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.primary}"
    rounded: "{rounded.md}"
    padding: "0.65rem 1rem"
    height: "{spacing.touch-web}"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "0.65rem 0.75rem"
    height: "{spacing.touch-web}"
  panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "{spacing.4}"
  status-pill:
    rounded: "{rounded.pill}"
    padding: "0.2rem 0.65rem"
    typography: "{typography.label}"
  status-pill-verified:
    backgroundColor: "{colors.success-bg}"
    textColor: "{colors.success}"
  status-pill-pending:
    backgroundColor: "{colors.warning-bg}"
    textColor: "{colors.warning}"
  status-pill-mismatch:
    backgroundColor: "{colors.error-bg}"
    textColor: "{colors.error}"
  status-pill-open:
    backgroundColor: "{colors.info-bg}"
    textColor: "{colors.info}"
  task-row:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    padding: "{spacing.3}"
    height: "{spacing.touch-web}"
  staff-nav-link:
    backgroundColor: "{colors.staff-nav}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.sm}"
    padding: "0.5rem 0.75rem"
    height: "{spacing.touch-web}"
  staff-nav-link-active:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
---

# Design System: LamTo

## 1. Overview

**Creative North Star: "The Open Maintenance Desk"**

LamTo feels like a well-lit resident service desk where reports, decisions, money, and proof are arranged in one readable sequence. A resident should understand what happened and what comes next while checking a phone in a building corridor; the building's Management user should inspect the same evidence efficiently at a desktop.

These are two distinct systems joined by one evidence chain, and the split is now absolute: **the resident product is the Flutter app, and the web platform is the Management workspace.** Every web route lives under `/s/`. There is no resident web surface, and nothing in the web system should be designed as though a resident might arrive at it. The app follows iOS Human Interface Guidelines and Android Material 3 conventions on their respective hardware, not one look painted over both. The web surface is denser and task-oriented. Both explain human outcomes before exposing technical proof.

The system rejects the crypto dashboard, the interchangeable-card admin template, the glossy property-management sales app, the command-center, and the hackathon prototype. It also rejects the newest temptation: presenting an AI triage suggestion as a conclusion. A suggestion is always rendered as something a named person accepted or overrode.

**Key Characteristics:**

- Restrained cool neutrals with sparse Accountability Indigo.
- Platform-native resident navigation and controls; genuine per-OS adaptation.
- Desktop-first operational web workflows for one Management user.
- One shared vocabulary of semantic integrity states and plain-language status.
- State-only motion and a WCAG 2.2 AA baseline.

## 2. Colors

Neutral surfaces dominate. Accountability Indigo is reserved for primary actions, current selection, links, and focus; semantic colors communicate evidence state and nothing else.

### Primary

- **Accountability Indigo** (`primary`): Institutional emphasis without crypto-purple spectacle. Primary buttons, active navigation, links, the current filter, and the row-lead action. Deepens on hover (`primary-hover`) and press (`primary-active`).
- **Focus Blue** (`focus`): Keyboard focus on web, as a 3px ring offset 2px. On the dark staff navigation the ring switches to white (`focus-on-dark`), because indigo-on-ink is not visible. Native surfaces use the platform focus treatment.

### Neutral

- **Clear Ground** (`neutral-bg`): Default light page and scaffold background.
- **Working Surface** (`surface`): Panels, forms, sheets, and grouped content.
- **Quiet Surface** (`surface-muted`): Toolbars, the membership bar, and secondary regions.
- **Record Ink** (`ink`): Primary copy, financial amounts, and the staff navigation surface. Money is Record Ink, never muted.
- **Quiet Ink** (`muted`): Secondary labels and metadata. Meets AA on both Clear Ground and Working Surface.
- **Border Mist** (`border`): Dividers, input strokes, and flat container boundaries.
- **Night Ground / Surface / Ink / Quiet Ink / Border** (`dark-*`): The first-class dark appearance for the Flutter app only. The Management web workspace does not ship a `prefers-color-scheme` theme; these tokens are not applied on web.

### Semantic

Four roles, one meaning each, on both platforms.

- **Verified Green** (`success`): Confirmed, resolved, chain-confirmed, independently verified.
- **Attention Amber** (`warning`): Pending, awaiting confirmation, deadline approaching.
- **Mismatch Red** (`error`): Failure, mismatch, overdue, blocked progress.
- **Open Blue** (`info`): Open, informational, in progress — and the locally-signed evidence level. Under disabled anchoring, "Đã ký — chưa bật neo blockchain" is a permanent informational state, not a warning awaiting resolution, so LOCAL_SIGNED renders Open Blue rather than Attention Amber.

Night has its own semantic set (`dark-success` through `dark-info-bg`): deep tinted fills with light ink. The light pastels glare on Night Ground and fail contrast, so they are never reused there. Night also carries its own primary pair: fills lighten to `dark-primary` (`#8A97E8`) so they read on Night Ground, and filled-button labels flip to `dark-on-primary` (`#12141C`, the Night Ground ink, ≈6.9:1) — white on the light indigo is 2.74:1 and fails AA.

### Named Rules

**The Ten-Percent Rule.** Accountability Indigo occupies no more than ten percent of a screen.

**The Separate States Rule.** Success, warning, error, and information use independent semantic roles plus text or an icon; color never carries meaning alone.

**The One Warning Rule.** There is exactly one warning value, `#8A5C00` (5.39:1 on Attention Amber's background), and both platforms use it. The lighter `#9A6700` cleared AA by 0.02 and is prohibited. Where web and app disagree on a token, the accessible value wins and both move.

**The Native Role Rule.** Flutter maps the palette through iOS semantic colors and Material color roles so dark mode and increased contrast keep working. The app's accepted Material mapping lightens two neutrals — neutral-bg maps to `#F6F7FB` and border to `#D7DCE8` — while the web workspace ships the canonical `neutral-bg`/`border` values.

## 3. Typography

**Display Font:** Platform system sans
**Body Font:** Platform system sans
**Label/Mono Font:** Platform mono, only inside expanded technical proof

**Character:** Approachable, neutral, and precise. One system family carries each surface; hierarchy comes from role, weight, and placement rather than decorative type pairing. There is no display face and no second family to pair against.

### Hierarchy

- **Headline** (700, 1.5rem, 1.25): Screen-level titles. Never promotional display sizes; the ceiling is 1.5rem, not a clamp.
- **Title** (700, 1.15rem, 1.25): Section headings, workflow sections, and evidence groups.
- **Body** (400, 1rem, 1.5): Primary copy, capped at 70ch for prose. Data-dense rows may run wider.
- **Label** (600, 0.85rem, 1.3): Field labels, metadata, status text, and deadlines, in sentence case.
- **Amount** (700, 1.75rem, tabular figures): Fund balances and headline financial figures. Row-level amounts use body size with the same tabular figures.
- **Hash** (mono, 0.85rem): Hashes, event IDs, and signed snapshots, inside disclosure only.
- **Native roles:** Dynamic Type on iOS and the Material type scale on Android. Hard-coded native point sizes are prohibited.

### Named Rules

**The Human Before Hash Rule.** Explain evidence in human language before showing hashes, event IDs, or signatures. Technical proof lives behind a `<details>` disclosure labelled "Technical proof", never in the summary.

**The Vietnamese-First Rule.** Resident type scales with the system and preserves enough leading for Vietnamese diacritics at every supported size. Resident copy is keyed from machine codes, never from server-supplied display strings.

**The Management Locale Rule.** The Management workspace ships in Vietnamese (`LANGUAGE_CODE = "vi"`). Staff templates, flash messages, nav labels, and TextChoices displays are translated through `locale/vi/LC_MESSAGES/`. The brand badge reads "LamTo Management" / "LamTo Quản lý", not HR. Money uses locale thousand separators (`USE_THOUSAND_SEPARATOR` + `NUMBER_GROUPING = 3`); negatives keep an ASCII minus with grouping (e.g. `-1.000.000`).

**The Tabular Column Rule.** Tabular figures only pay off when the column is end-aligned. Any amount in a scannable column is end-aligned once the row becomes a grid; stacked mobile rows stay start-aligned. Money chart series use brand/info colours for flow volume — never success/error, which are reserved for evidence state.

## 4. Elevation

LamTo is flat by default. Structure comes from spacing, dividers, tonal surfaces, and platform materials. Panels are a 1px Border Mist stroke on Working Surface with no shadow. Native surfaces use system materials on iOS and Material tonal elevation on Android. The web workspace has no shadow vocabulary at all, and that is deliberate rather than unfinished.

Depth on web is carried by three devices only: the tonal step from Clear Ground to Working Surface, the 1px border, and the horizontal rule at the top of a workflow section. A workflow section that is the primary action on the screen raises its top border to 2px in Accountability Indigo. That is the single strongest visual emphasis the workspace owns.

### Named Rules

**The One Boundary Rule.** A container may use a solid border or a soft elevation shadow, never both as decoration.

**The Flat Record Rule.** Evidence at rest has no decorative lift. If a record needs a large shadow to look organized, its hierarchy is wrong.

**The State-Only Motion Rule.** Motion explains state or spatial relationship and honors Reduce Motion or Remove animations. Page-load choreography is prohibited. Web transitions are 180ms on an ease-out curve and are limited to border, background, color, and a 1px press translate.

## 5. Components

Components are familiar, restrained, and consistent. Every interactive control accounts for default, hover, focus, active, disabled, loading, and error where applicable.

### Buttons

- **Shape:** Gently rounded (10px), minimum 44px target on web.
- **Primary:** Accountability Indigo on white, deepening on hover, pressed by a 1px downward translate.
- **Secondary:** Working Surface with a Border Mist stroke and indigo label; hover shifts the border to indigo.
- **Disabled:** 55% opacity and `not-allowed`. The `aria-disabled` treatment (62%) is distinct from the native disabled state, so a blocked-but-focusable control can still explain itself.
- **iOS / Android:** Native button roles at 44pt / 48dp minimums; Material filled, tonal, outlined and text roles.
- **Focus:** Focus Blue ring on web, platform-native treatment elsewhere.

### Status pills

- **One shape:** Fully rounded (999px), label typography, semantic background and ink, optional leading dot or icon.
- **One vocabulary:** Evidence level, workflow status, and deadline tone all use this pill. A deadline with no tone is Quiet Surface on Record Ink; soon is Attention Amber; overdue is Mismatch Red.
- **Prohibited:** A second chip shape for the same job. The square 8px "status chip" and the separate filter pill were removed for exactly this reason.

### Filters and search

- **Staff web:** A single search-and-filter form (`queue-toolbar`) with visible labels, native selects, an Apply button, and a Clear filters link that appears only when a filter is active. Web filtering is a form, not a chip row.
- **Resident app:** `SegmentedButton` and `ChoiceChip` for ledger and rating segments, themed through Material and Cupertino.
- **Separation:** Filter state never borrows verified, warning, or error colors.

### Panels and containers

- **Resident app:** Prefer platform lists and grouped content over card stacks.
- **Staff web:** Flat Working Surface panels (12px radius, 1.5rem padding) with a clear heading and one boundary treatment.
- **Nesting:** Nested cards are prohibited.

### Task lists

The workspace's primary data view, and deliberately not a table. A bordered list of full-row links; each row is a four-column grid above 720px and a stack below it. Column order is fixed: **next action, subject, amount, deadline.** The next action leads because responsibility outranks identity; the record ID never leads.

- **Hover:** The row fills with Clear Ground. The whole row is the hit target, minimum 44px.
- **Missing values:** An em dash for sighted users paired with a screen-reader-only explanation ("No amount recorded"), never a bare blank.
- **Empty:** Every list ships an empty state that names why it is empty and what to do, distinguishing "no records" from "no records match your filter" and offering Clear filters in the second case.

### Inputs and fields

- **Web:** Full-width Working Surface fields, visible labels, 10px radius, 44px minimum height, hover shifts the border to indigo, and an explicit error block in Mismatch Red on its tint.
- **Placeholders:** Quiet Ink at full opacity; they are hints, never a substitute for a label.
- **Native:** System text fields, switches, pickers, sheets, and dialogs.
- **Failure:** Preserve entered data where safe and state whether it was saved.

### Loading

- **Submitting:** A form marked `data-busy-on-submit` takes `aria-busy="true"` on submit, which dims its buttons to 62% and makes them inert. The second submit is swallowed. This is the whole loading vocabulary on web, because every mutation is a full page navigation.
- **Prohibited:** A spinner in the middle of content, and a `data-` behavior attribute with no script behind it. A control that looks interactive and does nothing is worse than no control.

### Navigation

- **iOS resident app:** `CupertinoTabScaffold` with a tab bar for top-level destinations and Cupertino routes for hierarchy. Report creation is a task, so it is the platform primary action rather than a destination.
- **Android resident app:** Material `NavigationBar` on compact widths and `NavigationRail` on expanded widths; system Back always works.
- **Staff web:** Record Ink navigation bar with indigo active and hover states, a white focus ring, a membership switcher that collapses to a plain label when there is only one building, and a secondary finance sub-nav in pill form.

### Signature patterns

- **Fund balance:** A prominent tabular amount followed by opening, inflow, and outflow context, with a compact balance chart that is itself a link to the fund.
- **Accountability chain:** An ordered `<ol>` of plain-language stages, each an outlined pill carrying a label and a state word, semantically tinted by state, with `aria-current="step"` on the live one. The state word does the work; the color agrees with it.
- **Technical proof:** A closed `<details>` labelled "Technical proof" holding hashes, verification status, and the signed snapshot. Each hash pairs a monospace value with a Copy button that reports "Copied" in place.
- **Action inbox:** A grouped task list showing who must act next, not a surveillance dashboard.

## 6. Do's and Don'ts

### Do:

- **Do** connect each expenditure to the reports, work, decisions, documents, and verification that justify it.
- **Do** explain status and outcomes before technical proof, and keep proof inside a disclosure.
- **Do** render an AI triage suggestion as a suggestion, alongside what the operator decided and how it differed.
- **Do** use platform-native resident controls while sharing brand and semantic roles across platforms.
- **Do** pair semantic color with text or an icon, and verify WCAG 2.2 AA contrast before committing a token.
- **Do** use tabular numerals for money, end-align amount columns, and keep amounts in Record Ink.
- **Do** lead every task row with the next action, and give every list a real empty state.
- **Do** expose the next safe action after failure, and say whether data was saved.

### Don't:

- **Don't** resemble a crypto-trading or Web3 dashboard with neon visuals, token language, or hashes and transaction IDs dominating the interface.
- **Don't** become a generic admin template composed of interchangeable cards, charts, and tables without an accountability narrative.
- **Don't** resemble a glossy property-management sales app built around luxury imagery, promotional gradients, or marketing-first interactions.
- **Don't** create a surveillance or command-center interface that makes residents feel monitored or controlled.
- **Don't** expose an overly legalistic, accounting-heavy, or technically dense system instead of plain status and evidence.
- **Don't** look like a playful hackathon prototype that weakens the seriousness of financial records.
- **Don't** present a model's output as an authoritative decision instead of a suggestion a named person accepted or overrode.
- **Don't** design a web screen for a resident. The web platform is the Management workspace; residents are app-only.
- **Don't** introduce a second shape for a job the status pill already does, or a second button vocabulary on one screen.
- **Don't** ship a `data-` behavior hook, an `aria-busy` rule, or a copy button without the script that makes it real.
- **Don't** use gradient text, glassmorphism, colored side-stripe borders, nested cards, oversized radii, decorative grids, or repeated eyebrow scaffolding.
- **Don't** pair a one-pixel border with a wide soft shadow on the same container.
- **Don't** port web navigation chrome into the native resident app, or leave dead resident-web chrome in the web stylesheet.
