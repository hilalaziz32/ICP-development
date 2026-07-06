# SMS Playbook — 1-Minute Tour

**What it is:** research → develop → draft, as 4 skills that hand off to each other. Every claim traced, nothing invented, everything QA'd against our Voice Profile before it ships.

## The pipeline

```
        RESEARCH                DEVELOP                    DRAFT
  ┌─────────────────┐   ┌──────────────────────┐   ┌──────────────────┐
  │   /sms-brief    │   │ /case-study-developer│   │    /sms-draft    │
  │                 │──▶│                      │──▶│                  │
  │ calls + master  │   │ proof-framing menu + │   │ pick 2-3 levers  │
  │ sheet + web →   │   │ mechanism menu from  │   │ → ~3 variants ea │
  │ Layer A brief   │   │ a real case study    │   │ → cut → QA       │
  └─────────────────┘   └──────────────────────┘   └──────────────────┘
          ▲                        ▲                        ▲
          │                        │                        │
  /call-corpus-search      mechanism-wordsmith       Voice Profile +
  (mine real prospect      (make the tactic          QA checklist +
   language on demand)      sticky, plain)           scoring rubric
```

**You stay the strategist at every arrow:** you pick the case study, you pick the mechanism line, you pick the levers, you pick the winner. The skills generate menus and enforce rules — they never decide.

## The 4 skills

| Skill | You give it | It gives back |
|---|---|---|
| **/sms-brief** | client + segment + persona | Layer A brief — real pains, buyer language, objections; every claim sourced (calls → master sheet → web, in that order) |
| **/case-study-developer** | a case study + the brief | 2 menus: ways to frame the numbers + ways to say the mechanism |
| **/mechanism-wordsmith** | the literal tactic | 5–7 SMS-ready reframings — plain words, no jargon |
| **/sms-draft** | developed case study + brief | T1/T2 variants per lever, cut to length, QA'd to voice |

## The rules layer (this folder)

- **Voice Profile** — how we sound; every draft is checked against it
- **levers.md** — the psychological angles a text can lead with
- **winners.md / pattern-library.md** — what's actually worked; new copy is cross-checked against it
- **QA** — checklist + scoring rubric inside sms-draft; nothing ships un-scored

## Hard rules baked in

1. **No invented numbers, clients, or mechanisms** — ever
2. **Real buyer language beats assumptions** — calls are Tier-1 evidence
3. **Mechanism is mined from real sources, then sharpened** — never lifted, never made up
4. **Skills are client-agnostic** — all client knowledge arrives via the brief, so the same pipeline runs on any offer

## Try it (one line each)

```
draft the brief for [client], targeting [persona]
develop the case study for [client]
draft the SMS
```
