# GTM System — End-to-End Flow

Everything you have today, in the order it runs. Phases on top, the underlying skill/tool used in brackets.

## Map at a glance

```mermaid
flowchart TD
    %% ============= PHASE 0 — INGEST =============
    subgraph P0["PHASE 0 — INGEST CALLS INTO THE CORPUS"]
        direction TB
        A1[Fireflies meeting URLs] -->|tools/fireflies.py| A2[Markdown transcripts on disk]
        A2 -->|sheet/fetch_all.py| A3[transcripts/*.md + index.json]
        A3 -->|sheet/build_final.py| A4[rec_enriched.csv<br/>+ category, angle,<br/>pain_point, sub_categories]
        A4 -->|sheet/upload_supabase.py| A5[(client_calls table)]
        A5 -->|tools/chunk_calls.py| A6[(call_chunks table<br/>~10–15 chunks per call)]
        A6 -->|tools/embed_chunks.py| A7[6 Gemini embeddings per chunk:<br/>text, summary, label_text,<br/>pain_point, angle, sub_categories]
    end

    %% ============= PHASE 0.5 — BRAINSTORM =============
    subgraph PHALF["PHASE 0.5 — CLIENT BRAINSTORM (one-stop KG view)"]
        direction TB
        BS1[clients/&lt;name&gt;/<br/>onboarding sheet, excel, prior emails<br/>+ all prior clients' output/ files<br/>+ memory] -->|skills/00_client_brainstorm.md<br/>≥6 cross-client corpus searches| BS2[clients/&lt;name&gt;/output/00_brainstorm.md<br/>= client snapshot + cross-client matches<br/>+ recurring patterns + hypotheses<br/>+ gaps for downstream]
    end

    %% ============= PHASE 1 — PRE-RESEARCH =============
    subgraph P1["PHASE 1 — PRE-RESEARCH (extract client truth)"]
        direction TB
        B1[Brainstorm<br/>+ client sheet<br/>+ raw transcripts] -->|skills/ICP-skills/Pre-Research & Case Study Extraction.md| B2[Verified USP<br/>+ proven case-study patterns<br/>+ verbatim VoC phrases]
    end

    %% ============= PHASE 2 — DEEP RESEARCH PIPELINE (DRP) =============
    subgraph P2["PHASE 2 — DEEP RESEARCH PIPELINE (5 chained skills)"]
        direction TB
        C1[Skill 1: Context & VoC Data Sources<br/>01_context_and_data_source.md] --> C2[Skill 2: Pain Points + Consequences<br/>02_pain_points_and_consequences.md]
        C2 --> C3[Skill 3: Dream Outcomes + 5-Whys<br/>03_outcomes_and_whys.md]
        C3 --> C4[Skill 4: Current Solutions + Failed Attempts<br/>04_current_solutions.md]
        C4 --> C5[Skill 5: Objections + Triggers<br/>05_objections_and_triggers.md]
    end

    %% ============= PHASE 3 — STRATEGY =============
    subgraph P3["PHASE 3 — STRATEGY"]
        direction TB
        D1[Market Deep-Dive & Variable Balancing<br/>skills/ICP-skills/Market Deep-Dive...md] --> D2[GTM Hypothesis Generation & Trigger Mapping<br/>skills/ICP-skills/GTM Hypothesis...md]
    end

    %% ============= PHASE 4 — COMPILATION =============
    subgraph P4["PHASE 4 — COMPILATION"]
        direction TB
        E1[GTM Sheet Compiler<br/>ICP-skills-deepsearch-engine/gtm-sheet-compiler.md]
        E2[GTM Data Sheet<br/>skills/ICP-skills/GTM-sheet.md]
        E1 --> E2
    end

    %% ============= PHASE 5 — COPY =============
    subgraph P5["PHASE 5 — COPY"]
        direction TB
        F1[SMS skill<br/>skills/copies/sms-skills.md]
        F2[Email / Cold-DM<br/>FUTURE skills]
    end

    %% ============= LATERAL SKILLS / TOOLS =============
    subgraph LATERAL["LATERAL — fires anywhere in phases 1–5"]
        direction TB
        L1[".claude/skills/call-corpus-search<br/>fires on any GTM question.<br/>Calls the 5 search tools below."]
        L2[search_chunks_by_text]
        L3[search_chunks_by_summary]
        L4[search_chunks_by_label<br/>(label_text bag-of-words)]
        L5[search_chunks_by_pain_point<br/>(KG hop)]
        L6[search_chunks_by_angle<br/>(KG hop)]
        L1 --> L2 & L3 & L4 & L5 & L6
        L7[Sandler 49 rules<br/>skills/sandler-sales-rules.md]
    end

    %% Phase wiring
    A7 -.feeds.-> L2 & L3 & L4 & L5 & L6
    A7 -.feeds.-> BS1

    BS2 --> B1
    BS2 -.passed as input to.-> C1 & C2 & C3 & C4 & C5
    BS2 -.passed as input to.-> D1 & D2
    BS2 -.passed as input to.-> E1
    BS2 -.passed as input to.-> F1 & F2

    B2 --> C1
    C5 --> D1
    D2 --> E1
    E2 --> F1 & F2

    L1 -.consulted in.-> P1
    L1 -.consulted in.-> P2
    L1 -.consulted in.-> P3
    L1 -.consulted in.-> P4
    L1 -.consulted in.-> P5
    L7 -.consulted before drafting.-> F1 & F2
```

---

## Phase-by-phase: what to do, what runs, what's produced

### PHASE 0 — Ingest calls into the corpus

When you have a new client (or new calls for an existing client), bring the transcripts into Supabase **once**. Everything downstream re-uses this corpus.

| Step | Command | Produces |
|---|---|---|
| Fetch one transcript | `python3 tools/fireflies.py "<url>"` | Markdown to stdout |
| Bulk fetch from sheet | `python3 sheet/fetch_all.py` | `sheet/transcripts/*.md` + index |
| Categorize + build CSV | `python3 sheet/build_final.py` | `sheet/rec_enriched.csv` |
| Upload to Supabase | `python3 sheet/upload_supabase.py` | rows in `client_calls` |
| Chunk into topic blocks | `python3 tools/chunk_calls.py --client <name>` | rows in `call_chunks` |
| Embed (6 vectors/chunk) | `python3 tools/embed_chunks.py --client <name>` | populated embedding cols |

**Pipeline is idempotent** — `chunked` and `embedded` flags on `client_calls` mean re-running picks up only new work.

### PHASE 0.5 — Client Brainstorm (NEW, runs once per new client)

Run `skills/00_client_brainstorm.md`. This is the **only** skill that hits the corpus heavily — it consolidates everything we know into one file:

- Reads the entire `clients/<client>/` folder (onboarding sheet, excel, spec docs, prior emails).
- Reads any prior research outputs for this client.
- Runs ≥6 cross-client corpus searches to find every prior call that overlaps on pain, angle, vertical, or specialty.
- Pulls the matching prior client's downstream outputs (Pre-Research USP, lead pain in DRP02, final SMS/email angles) so you can see "what worked before for similar pains."
- Writes a single doc to `clients/<client>/output/00_brainstorm.md` with: client snapshot → cross-client matches → recurring patterns → initial hypotheses → gaps for downstream skills.

**Every downstream skill (Phases 1–5) takes the brainstorm as primary input.** They don't re-query the DB unless they discover a brand-new probe mid-task. This is the "build the KG view once, reference it everywhere" pattern.

### PHASE 1 — Pre-research

Run `skills/ICP-skills/Pre-Research & Case Study Extraction.md`. Inputs: brainstorm + client sheet + raw transcripts. Output: verified USP + proven case-study patterns + verbatim VoC.

### PHASE 2 — Deep Research Pipeline (5 chained skills)

Run them **in order** — each consumes the previous one's MDX output:

1. `01_context_and_data_source.md` → ICP, TAM, watering holes, VoC sources.
2. `02_pain_points_and_consequences.md` → ranked verbatim pains.
3. `03_outcomes_and_whys.md` → desired outcomes, 5-Whys.
4. `04_current_solutions.md` → tools, failed attempts, blockers.
5. `05_objections_and_triggers.md` → objections + macro triggers.

Each step has mandatory live web search; **the corpus search skill plugs in here as a *second* source of truth** (real prospect language from your own calls, not just public web).

### PHASE 3 — Strategy

1. `Market Deep-Dive & Variable Balancing.md` — pressure-test the research against market reality.
2. `GTM Hypothesis Generation & Trigger Mapping.md` — produce 3+ campaign hypotheses (MDX).

### PHASE 4 — Compilation

`gtm-sheet-compiler.md` (Skill 7) → `GTM-sheet.md` produces the final, execution-ready GTM Data Sheet (3–5 segments, persona/sizing/intent triggers/offer angles per segment). This is what your data team runs in Apollo/Clay.

### PHASE 5 — Copy

- `skills/copies/sms-skills.md` for SMS.
- **SMS playbook chain** (`.claude/skills/`): `sms-brief` → `case-study-developer` → `sms-draft` — the deep, strategist-led path; reads local files + the Supabase call corpus.
- **`.claude/skills/evergreen-copywriter`** — the *evergreen-grounded* copy path, running **parallel** to the chain. Pulls pains/lingo/proof/winners from the Evergreen API (the live runtime face of `sms-playbook/evergreen-db-spec.md`), writes, saves, and links the copy back. Use for fast, data-grounded copy; the chain stays for deep hand-crafted runs. Both bind to the same `sms-playbook/` voice bar.
- (Future) email + cold DM skills slot in here. They consume the GTM Sheet + DRP outputs.

---

## Corpus integration tiers (READ THIS)

The Supabase call corpus is wired into the pipeline at **two levels of mandate**:

| Tier | Skills | Behaviour |
|---|---|---|
| **MANDATORY corpus pass before web search** | Pre-Research, DRP Skill 01 (Context) | Must run ≥3 cross-client corpus queries before any web call. Web is a supplement. Every claim tagged `[CORPUS …]` / `[TRANSCRIPT]` / `[WEB …]`. |
| **Optional corpus supplement** | DRP 02–05, Market Deep-Dive, GTM Hypothesis, GTM Sheet, SMS, GTM Sheet Compiler | Corpus is available; query it when web feels thin or claims need a verbatim anchor. Skip when prior-skill MDX already has enough VoC. |

The full protocol — which CLI to pick for which question, how to cite, when to scope to one client — lives in [`skills/_corpus_first_protocol.md`](skills/_corpus_first_protocol.md).

## Lateral skill — call-corpus-search

`.claude/skills/call-corpus-search/SKILL.md` fires automatically when **any** of these phases needs to ground a claim in actual prospect language. Triggers on requests like:

- "Pull every chunk where prospects describe high CAC pain."
- "What objections did kynship prospects raise about pricing?"
- "Find chunks from calls pitched on the 'cut CAC by 50%' angle."

It picks one of 5 search modes and returns ranked chunks with verbatim text + parent call's strategic context. **Cross-client by default** — patterns travel across verticals.

---

## When you (Hilal) start a new GTM project

1. **Phase 0 first.** Ingest the client's calls into Supabase (one-time per client). Skip if already done.
2. **Phase 1.** Pre-research using the call corpus + onboarding sheet. The corpus-search skill will fire repeatedly here.
3. **Phase 2.** Run the 5 DRP skills sequentially. Each step references the corpus.
4. **Phase 3.** Strategy + hypotheses.
5. **Phase 4.** Compile into GTM Sheet.
6. **Phase 5.** Copy. Reference Sandler rules + corpus before drafting any line.

Total: 0 → 5 is one full GTM run. The corpus and the 5 search tools are the connective tissue that keep every phase honest — no marketing-speak, no hallucinated pains.

---

## What's missing / future hooks

- **Email + cold-DM copy skills** (Phase 5 has only SMS today).
- **Critique tool** that takes a draft and (a) roleplays a prospect, (b) flags outsider language, (c) suggests verbatim swaps from the corpus. Reuses the same `call_chunks` embeddings.
- **Pattern map** — cluster the pain-point embeddings to surface the top 5 cross-client themes for a vertical without a query.
- **More clients in the corpus** — current corpus is 31 kynship calls / 303 chunks. Pattern depth scales with breadth.
