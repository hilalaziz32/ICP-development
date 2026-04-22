# GTM Playground — How This Repo Works

This is the operating system for our outbound/GTM work. Every client (Kynship, UNITZERO, etc.) runs through the same pipeline: **research the market → build the GTM sheet → write the copy**. The repo is split so that *each step in the process has its own file*, and the same step can be reused across clients.

If you are new: read this top-to-bottom once. After that you should be able to pick any client and know exactly which file to open next.

---

## The folders in plain English

| Folder | What lives here | Who reads it |
|---|---|---|
| [skills/](skills/) | **Prompts**. The actual "brain" that runs at each step. You load one of these into Claude and it does the work. | The AI, at runtime |
| [sops/](sops/) | **Standard Operating Procedures**. How-to guides for the human operator — step-by-step checklists. | Humans + the AI reads them as reference |
| [frameworks/](frameworks/) | **Templates and proven formulas** (SMS structures, email swipe files, value-prop formulas). | Skills pull from these when writing copy |
| [rules/](rules/) | **Guardrails**. Things we always do / never do. Style, tone, anti-patterns. | Every skill reads these before producing output |
| [clients/](clients/) | **Per-client workspaces**. Each client has an `output/` folder where the pipeline writes its results. | Read by downstream steps; final deliverable |
| [tools/](tools/) | Small Python helpers (Slack, Fathom). | Ops only |
| [winning-sms/](winning-sms/) | Library of SMS messages that actually got replies. Copy skills cross-reference this. | SMS writing skill |

---

## The full pipeline — one picture

```
                        ┌──────────────────────────────────┐
                        │   CLIENT ONBOARDING INPUTS       │
                        │   • onboarding form              │
                        │   • sales-call transcripts       │
                        │   • case studies                 │
                        │   • website URL                  │
                        └──────────────┬───────────────────┘
                                       │
                                       ▼
  ╔════════════════════════════════════════════════════════════════════╗
  ║                  PHASE 1 — DEEP RESEARCH PIPELINE                  ║
  ║               (folder: skills/ICP-skills-deepsearch-engine/)       ║
  ╚════════════════════════════════════════════════════════════════════╝

  ┌──────────────────────────────────────────────────────────────────────┐
  │ STEP 1 ─► skills/ICP-skills-deepsearch-engine/01_context_and_data_source.md
  │          ← map TAM, ICP, VoC sources
  │          ALSO READS:
  │            • rules/core_principles.md          (ICP principles)
  │            • rules/anti_patterns_and_mistakes.md
  │          INPUT:  client website, ICP, persona, onboarding form
  │          OUTPUT: clients/<client>/output/01_context_and_data_source.md
  └────────────────────────────────────┬─────────────────────────────────┘
                                       ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │ STEP 2 ─► skills/ICP-skills-deepsearch-engine/02_pain_points_and_consequences.md
  │          ← mine real pains from VoC, rank 1–10, cascade consequences
  │          ALSO READS:
  │            • rules/core_principles.md
  │            • rules/anti_patterns_and_mistakes.md
  │          INPUT:  Step 1 output
  │          OUTPUT: clients/<client>/output/02_pain_points_and_consequences.md
  └────────────────────────────────────┬─────────────────────────────────┘
                                       ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │ STEP 3 ─► skills/ICP-skills-deepsearch-engine/03_outcomes_and_whys.md
  │          ← dream outcomes + 5 whys (emotional driver)
  │          ALSO READS:
  │            • rules/core_principles.md
  │            • sops/unique_mechanism_sop.md      (outcome language feeds mechanism)
  │          INPUT:  Step 2 output
  │          OUTPUT: clients/<client>/output/03_outcomes_and_whys.md
  └────────────────────────────────────┬─────────────────────────────────┘
                                       ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │ STEP 4 ─► skills/ICP-skills-deepsearch-engine/04_current_solutions.md
  │          ← what they've tried, what's blocking, what's pressuring them
  │          ALSO READS:
  │            • rules/core_principles.md
  │          INPUT:  Steps 1–3
  │          OUTPUT: clients/<client>/output/04_current_solutions.md
  └────────────────────────────────────┬─────────────────────────────────┘
                                       ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │ STEP 5 ─► skills/ICP-skills-deepsearch-engine/05_objections_and_triggers.md
  │          ← predicted objections + "why now" trigger events
  │          ALSO READS:
  │            • rules/core_principles.md
  │            • skills/sandler-sales-rules.md     (objection patterns)
  │          INPUT:  Steps 1–4
  │          OUTPUT: clients/<client>/output/05_objections_and_triggers.md
  └────────────────────────────────────┬─────────────────────────────────┘
                                       ▼
  ╔════════════════════════════════════════════════════════════════════╗
  ║                  PHASE 2 — COMPILE THE GTM SHEET                   ║
  ╚════════════════════════════════════════════════════════════════════╝

  ┌──────────────────────────────────────────────────────────────────────┐
  │ STEP 6 ─► skills/ICP-skills-deepsearch-engine/gtm-sheet-compiler.md
  │          ← synthesise into 3–5 scalable segments (NO new research)
  │          ALSO READS (mandatory):
  │            • sops/gtm_data_sheet_sop.md        (human SOP for same process)
  │            • sops/unique_mechanism_sop.md      (each segment needs a mechanism)
  │            • frameworks/value_prop_frameworks.md (offer angle formulas)
  │            • rules/core_principles.md
  │            • rules/anti_patterns_and_mistakes.md
  │          INPUT:  Steps 1–5 outputs + onboarding form + case studies CSV
  │          OUTPUT: clients/<client>/output/01_gtm_strategy.md
  └────────────────────────────────────┬─────────────────────────────────┘
                                       ▼
              ➜ 3–5 segments, each with persona, triggers, offer angle
                                       │
                                       ▼
  ╔════════════════════════════════════════════════════════════════════╗
  ║                  PHASE 3 — COPYWRITING                             ║
  ╚════════════════════════════════════════════════════════════════════╝

  ┌──────────────────────────────────────────────────────────────────────┐
  │ STEP 7 ─► skills/copies/sms-skills.md
  │          ← write SMS copy (Pain + Mechanism + Outcome)
  │          ALSO READS (all of these, every time):
  │            • sops/sms_guidelines.md            (operational rules)
  │            • sops/unique_mechanism_sop.md      (mechanism required)
  │            • frameworks/sms_frameworks.md      (12 proven frameworks)
  │            • winning-sms/                      (tone/length reference)
  │            • rules/copy_and_prompt_guidelines.md (voice)
  │            • rules/anti_patterns_and_mistakes.md (no dashes, no corp-speak)
  │            • skills/sandler-sales-rules.md    (Priority-10 + Child/Adult/Parent)
  │            • skills/sandler-49-rules-quickref.md
  │          INPUT:  Step 6 GTM sheet + Steps 1–5 research
  │          OUTPUT: clients/<client>/output/06_sms_copy_drafts.md
  └────────────────────────────────────┬─────────────────────────────────┘
                                       ▼
              ➜ SMS drafts per segment
                                       │
                                       ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │ STEP 8 ─► QA PASS (no skill, just checklists)
  │          READS:
  │            • rules/copy-iterator.md            (1-to-1 voice check)
  │            • rules/copy_and_prompt_guidelines.md
  │            • rules/anti_patterns_and_mistakes.md
  │            • sops/qa_checklists.md             (pre-ship checklist)
  │          OUTPUT: clients/<client>/output/07_sms_copy_improved.md  (FINAL)
  └──────────────────────────────────────────────────────────────────────┘

  FOR COLD EMAIL (parallel path to SMS in Step 7):
    • frameworks/email_templates.md                (swipe file)
    • frameworks/value_prop_frameworks.md          (value-prop formulas)
    • + same rules/ + sops/qa_checklists.md as above
```

Everything the AI reads at a given step is listed inside the skill file's `<rules>` block. The graph above is the short version.

---

## Step-by-step — what each step actually does

### Phase 1 — Deep Research (the 5 skills)

Each of these is a self-contained prompt. You run them **in order**. Each one takes the previous step's output as input.

**Step 1 — Context & Data Sources**
- File: [skills/ICP-skills-deepsearch-engine/01_context_and_data_source.md](skills/ICP-skills-deepsearch-engine/01_context_and_data_source.md)
- Does: maps the client's business, TAM, ICP, persona, and — most importantly — the exact Reddit subs / LinkedIn groups / G2 sections / Slack communities where the persona actually talks.
- Needs from you: client website, ICP, persona, onboarding form.
- Output goes to: `clients/<client>/output/01_context_and_data_source.md`

**Step 2 — Pain Points & Consequences**
- File: [skills/ICP-skills-deepsearch-engine/02_pain_points_and_consequences.md](skills/ICP-skills-deepsearch-engine/02_pain_points_and_consequences.md)
- Does: pulls verbatim pain-point quotes from the sources Step 1 found, ranks them 1–10, and cascades consequences at 30/90/365 days.
- Reads: Step 1 output.
- Output: `clients/<client>/output/02_pain_points_and_consequences.md`

**Step 3 — Dream Outcomes & Whys**
- File: [skills/ICP-skills-deepsearch-engine/03_outcomes_and_whys.md](skills/ICP-skills-deepsearch-engine/03_outcomes_and_whys.md)
- Does: for each ranked pain, finds the outcome the persona actually wants (in their words), then runs 5 Whys to get the emotional driver.
- Reads: Step 2 output.

**Step 4 — Current Solutions & Blockers**
- File: [skills/ICP-skills-deepsearch-engine/04_current_solutions.md](skills/ICP-skills-deepsearch-engine/04_current_solutions.md)
- Does: what the ICP is *currently* doing (tools, agencies, DIY), what they've tried and failed, what's blocking them, what's pressuring them to fix it now.
- Reads: Steps 1–3.

**Step 5 — Objections & Triggers**
- File: [skills/ICP-skills-deepsearch-engine/05_objections_and_triggers.md](skills/ICP-skills-deepsearch-engine/05_objections_and_triggers.md)
- Does: predicts objections to the cold pitch + surfaces trigger events (funding, hiring, tech changes) that make *this quarter* the right moment.
- Reads: Steps 1–4.

---

### Phase 2 — GTM Sheet Compiler

**Step 6 — Compile the final GTM sheet**
- File: [skills/ICP-skills-deepsearch-engine/gtm-sheet-compiler.md](skills/ICP-skills-deepsearch-engine/gtm-sheet-compiler.md)
- Does: **no new research** — it synthesises Steps 1–5 plus the onboarding form and case studies into 3–5 clean, like-for-like segments the data team can run in Apollo/Clay.
- Reads:
  - All 5 deep-research outputs
  - Client onboarding form
  - Case studies CSV
  - [sops/gtm_data_sheet_sop.md](sops/gtm_data_sheet_sop.md) — the human SOP for the same process
  - [sops/unique_mechanism_sop.md](sops/unique_mechanism_sop.md) — so each segment has a defensible mechanism, not a generic claim

> **Alternative shorter path** — [skills/ICP-skills/](skills/ICP-skills/) contains an older 4-step version of the same pipeline (`Pre-Research & Case Study Extraction` → `Market Deep-Dive & Variable Balancing` → `GTM Hypothesis Generation & Trigger Mapping` → `GTM-sheet`). Use this when the client is simple or research budget is tight. The 5-skill deepsearch engine is the default.

---

### Phase 3 — Copywriting

**Step 7 — Write the SMS**
- File: [skills/copies/sms-skills.md](skills/copies/sms-skills.md)
- Does: writes SMS copy that sounds like one business owner texting another. Pain + Mechanism + Outcome.
- Reads (all of these, every time):
  - [sops/sms_guidelines.md](sops/sms_guidelines.md) — operational rules
  - [sops/unique_mechanism_sop.md](sops/unique_mechanism_sop.md) — every SMS needs a unique mechanism
  - [frameworks/sms_frameworks.md](frameworks/sms_frameworks.md) — the 12 proven SMS frameworks
  - [winning-sms/](winning-sms/) — cross-reference tone/length against real winners
  - [rules/copy_and_prompt_guidelines.md](rules/copy_and_prompt_guidelines.md) — voice
  - [rules/anti_patterns_and_mistakes.md](rules/anti_patterns_and_mistakes.md) — what to avoid (no dashes, no corporate speak, etc.)
  - [skills/sandler-sales-rules.md](skills/sandler-sales-rules.md) + [skills/sandler-49-rules-quickref.md](skills/sandler-49-rules-quickref.md) — behavioural-sales pressure test

For cold email, the parallel template library is [frameworks/email_templates.md](frameworks/email_templates.md) and the value-prop formulas are [frameworks/value_prop_frameworks.md](frameworks/value_prop_frameworks.md).

**Step 8 — QA / iterate**
- File: [rules/copy-iterator.md](rules/copy-iterator.md) — the quick "does this sound human?" pass
- File: [sops/qa_checklists.md](sops/qa_checklists.md) — the pre-ship checklist (relevance, lingo, flow, CTA, unique mechanism visible, pattern interrupt present)
- Enforced by: [rules/anti_patterns_and_mistakes.md](rules/anti_patterns_and_mistakes.md)

---

## The rules files — read these first, always

Every skill above reads the `rules/` folder before producing anything. If you are tweaking a skill or writing new copy by hand, start here:

- [rules/core_principles.md](rules/core_principles.md) — the 5 ICP principles + market research principles. The *why* behind the whole pipeline.
- [rules/copy_and_prompt_guidelines.md](rules/copy_and_prompt_guidelines.md) — the 80/20 prompting template + pyramid of persuasion.
- [rules/anti_patterns_and_mistakes.md](rules/anti_patterns_and_mistakes.md) — the "never do this" list.
- [rules/copy-iterator.md](rules/copy-iterator.md) — the human-voice QA checklist.

---

## How a new client moves through the repo

Using Kynship as the worked example:

```
clients/kynship/
  ├── onbaordingform.txt             ← raw input
  ├── transcripts/                   ← raw input (sales calls)
  ├── excel/                         ← raw input (case studies)
  ├── slack/                         ← raw input (slack data)
  └── output/
      ├── 01_context_and_data_source.md   ← written by Step 1
      ├── 02_pain_points_and_consequences.md ← written by Step 2
      ├── 03_outcomes_and_whys.md         ← written by Step 3   (when done)
      ├── 04_current_solutions.md         ← written by Step 4   (when done)
      ├── 05_objections_and_triggers.md   ← written by Step 5   (when done)
      ├── 01_gtm_strategy.md              ← written by Step 6
      └── 06_sms_copy_drafts.md           ← written by Step 7
```

UNITZERO has the same layout at [clients/UNITZERO/](clients/UNITZERO/).

When a new client lands:
1. Create `clients/<new-client>/` with `onboardingform.txt`, `transcripts/`, `case-studies` (any format).
2. Create an empty `clients/<new-client>/output/` folder.
3. Run Steps 1 → 7 in order, each writing into that `output/` folder.
4. Ship copy from Step 7 after passing the Step 8 QA.

---

## One-liner cheat sheet

| I want to… | Open this file |
|---|---|
| Understand the whole philosophy | [rules/core_principles.md](rules/core_principles.md) |
| Kick off deep research for a new client | [skills/ICP-skills-deepsearch-engine/01_context_and_data_source.md](skills/ICP-skills-deepsearch-engine/01_context_and_data_source.md) |
| Compile a finished GTM segment sheet | [skills/ICP-skills-deepsearch-engine/gtm-sheet-compiler.md](skills/ICP-skills-deepsearch-engine/gtm-sheet-compiler.md) |
| Write SMS | [skills/copies/sms-skills.md](skills/copies/sms-skills.md) |
| Write cold email | [frameworks/email_templates.md](frameworks/email_templates.md) + [frameworks/value_prop_frameworks.md](frameworks/value_prop_frameworks.md) |
| QA copy before shipping | [sops/qa_checklists.md](sops/qa_checklists.md) + [rules/copy-iterator.md](rules/copy-iterator.md) |
| Build a unique mechanism | [sops/unique_mechanism_sop.md](sops/unique_mechanism_sop.md) |
| See the human SOP for the GTM sheet | [sops/gtm_data_sheet_sop.md](sops/gtm_data_sheet_sop.md) |
| Pressure-test copy against Sandler | [skills/sandler-sales-rules.md](skills/sandler-sales-rules.md) |
