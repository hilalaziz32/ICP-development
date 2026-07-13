---
name: mechanism-wordsmith
description: Turn a chosen case study's literal agency mechanism into a spread of cold-SMS-ready mechanism lines — sticky, jargon-free, connector-led, in the buyer's own words. Reads the shared SMS playbook (Voice Profile, winners.csv, pattern-library). Use when a strategist has the brief + a chosen case study with a known literal mechanism and needs the {{unique_mechanism}} line(s) for cold SMS. Triggers on "wordsmith this mechanism", "make this mechanism sticky", "mechanism variants for [case study]", "unique mechanism for [client]", "give me SMS-able mechanisms", "reframe [tactic] for SMS". Do NOT invent a mechanism that isn't in the case study. Do NOT write the full SMS — that's sms-draft.
---

# mechanism-wordsmith — the {{unique_mechanism}} engine

Turn **"what the agency literally did"** into a small spread of cold-SMS-ready mechanism lines a
strategist can remix to ship in minutes. The mechanism is a **core pillar** of the text — this skill
exists to make it land. It is **not** an auto-writer; it surfaces strong, on-voice options.

## The shared playbook this skill reads (always load these first)
- **`sms-playbook/Cold-SMS-Voice-Profile-Scaletopia.md`** — the tonal source of truth (closer-test,
  native-unit, picture>label, the banlist, casing/CTA). Every line obeys it.
- **`sms-playbook/winners.csv`** — the 17 tagged winners. **This is the routing source**: match the
  case study to the closest winner(s) by offer/niche and read their lever · pattern · what-carries ·
  whether the mechanism was used or omitted.
- **`sms-playbook/pattern-library.md`** — the two-tier model + the mechanism patterns + connectors.
- **`sms-playbook/FUNDAMENTALS.md`** — the spine. (`levers.md` = light support.)

## Inputs
**Required:** chosen case study (client + result/outcome) · the **literal mechanism** (what the agency
actually did) · the Layer A brief (pains + the buyer's own words) · offer + niche · persona.
**Helpful:** sophistication, already-tried lines to avoid.

## Output
A ranked spread of mechanism lines (strategist controls how many). Each carries:
`line (connector-led) · pattern (or "omitted — lead on result+specificity") · what-carries · lever it
serves · why it works · score`. Plus a note flagging anything that doesn't trace to a winner/brief.
**This skill outputs only the mechanism line(s) — never the full SMS.**

---

## Workflow

### Step 0 — Confirm inputs
If the literal mechanism is vague, missing, or pure jargon with no substance → **stop and kick back.**
Never invent a mechanism. ("Worked closely on their marketing" is not a mechanism.)

### Step 1 — Route via the winners
Find the closest tagged winner(s) in `winners.csv` (same offer archetype / niche). Read their **lever,
pattern, what-carries, and mechanism-used-or-omitted.** That's your routing — not a separate matrix.

### Step 2 — Tier-1 decision: what carries?
Decide what does the heavy lifting (per `pattern-library.md`): case study/result · specificity/relevance
· authority · guarantee · **or the mechanism itself**.
- **The mechanism is usually present and usually matters — keep it central.**
- **Omit it ONLY in the narrow case:** (a) commoditized/SEO offer where the mechanism just restates the
  result ("we ranked them #1" — the Big Leap case), or (b) a case study so strong + specific it carries
  alone. If omitting → return "lead on result + specificity" + optional *"without X"* wrapper lines, and
  say so explicitly. Don't manufacture a fake mechanism to fill the slot.

### Step 3 — Generate the spread (when the mechanism carries or supports)
Write **connector-led** lines across the live patterns (Plain-English · High-level abstraction ·
Contrarian · Trigger), each:
- **Connector included** ("mostly by…", "using…", "by…") — never the bare fragment. Pick the connector
  per `pattern-library.md` (soften with "mostly by" when full attribution would overclaim).
- **Picture, not label** (Voice Profile): "gifting free product to 100 creators and running ads off their
  posts" beats "viral micro creator seeding strategy". A sticky *label* is licensed only by strong proof.
- **Payable on the call** — if the closer couldn't defend it on a call, cut it.
- In the **buyer's own words** from the brief; **native unit** for the persona (retainers / shows / jobs).

### Step 4 — Wrapper pass
Where it genuinely fits, add a *"without X"* wrapper = the buyer's assumed-required thing or core pain,
compressed. **Imply, don't over-assert** ("unpaid creators" > "without ever paying a single creator").
Flag absolutes (ever/single/entire) to defend-or-cut. Only when you truly didn't do X.

### Step 5 — Voice pass
Run every line through the Voice Profile: the **banlist** (no %/decimals, no "it's not just X—it's Y",
no empty verbs/jargon, no "+"-notation), **closer-would-say-it test**, **phone-paste glance test**,
casing, and the lexical preferences (creator>influencer, ads>creatives, etc.).

### Step 6 — Score + rank
Score each line on: **believability · relevance · differentiation · curiosity · length · traceability.**
Rank. (Curiosity can win even without dissolving a named pain.)

### Step 7 — Output the spread
Strategist-controlled quantity. Label each line as in **Output** above. Flag any that don't trace to a
winner/brief. Hand off to sms-draft for assembly.

---

## Hard rules
- **Never invent a mechanism** that isn't in the case study. Kick back on vague.
- **Never force a mechanism onto an omit-case** (commoditized/SEO) — return result+specificity instead.
- **Mechanism is a core pillar** — omission is the rare exception, never the default.
- **Connector-led, picture-over-label, native-unit, in the buyer's words.**
- **Jargon is judged against the brief**, not a static banlist — a term the buyer uses themselves stays.
- **Never write the full SMS** — only the mechanism line(s).
- **Every line obeys the Voice Profile.** If the closer wouldn't say it on a call, it's dead.

## When NOT to use
- No case study chosen yet (Layer B selection first) · literal mechanism unknown (research first) ·
  the strategist wants the full SMS (use sms-draft).

## Success bar
A run wins if the spread gives the strategist enough strong, on-voice building blocks to land a final
mechanism line by remixing in a few minutes — not that any single line ships verbatim.
