# Cold-SMS System — Beta → Launch Readiness Audit

> **What this is.** An honest read of whether the SMS system is ready to hand to a GTM strategist, *how* to judge
> it going forward, and the specific things only Aaman currently supplies that have to be systematized first.
> **Status: STRAWMAN — Aaman to redline, especially Part 3 (it's your judgment, I only extracted my read).**
> Date: 2026-06-08 · Owner: Aaman · re-run this audit every time we change a skill or finish a real campaign.

---

## The launch bar (the one definition of "done")

> A **new strategist** runs a full campaign **A → B → C unaided** and hits **~8/10 copy** (per `scoring-rubric.md`)
> in **materially less time than manual** (target ≈ **under 2 hours** end to end).

Everything below is measured against that line. We are **not there yet** — the gap is *reliability, speed, and
hand-off-ability*, not raw quality (the system can already produce 8/10; it just can't do it *consistently* or
*without Aaman*).

---

## Part 1 — How to judge a system like this

The trap we've already paid for twice: **judging it by reading it.** "Builds cleanly, no buzzwords, references
resolve" told us nothing — case-study-developer still shipped at 5.5/10. **You can only judge this by running it
on real campaigns and grading the output.** That's the whole method.

### The three axes (score every real run)

| Axis | Question | How to measure | Why it matters |
|---|---|---|---|
| **Quality** | Is the output 8–9/10? | Score the final variants against `scoring-rubric.md` (Relevance 30 / Human 25 / Proof-fit 20 / USP 15 / CTA 10) | the output bar |
| **Speed** | Is it a *fraction* of manual time? | **Rounds of back-and-forth** + **wall-clock**, vs the manual baseline | the whole point of the system |
| **Consistency** | Does it behave the same every run? | Count **off-script incidents** (invented structure, ignored its own rules, under-flooded, cringe lines) | reliability = hand-off-ability |

> ⚠️ **Open gap — we have no manual baseline number.** We can't honestly claim "a fraction of the time" until we
> write down what a campaign took *manually* before (rough hours for A, B, C). Capture this next run.

### The two extra lenses

- **Per-component health** — rate each skill / playbook / data layer / doc (the scorecard in Part 2).
- **Hand-off readiness** — the real test: *could a zero-context strategist run it and clear the launch bar?*
  Today: no — see Part 3.

### Reusable per-run scorecard (copy this for every campaign)

```
CAMPAIGN: __________  OFFER SHAPE: __________  DATE: ______
QUALITY    (rubric /100): ____   →  ≥80 = pass
SPEED      rounds: ____  wall-clock: ____  vs manual baseline: ____  →  materially faster = pass
CONSISTENCY off-script incidents: ____  (list them)            →  0–1 = pass
NOTES / what Aaman had to supply that the strategist wouldn't: __________
VERDICT vs launch bar:  PASS / NOT YET
```

Run this on **different offer shapes** (easy-mechanism, thin/commodity-mechanism, tool/product). A pass on one
shape ≠ ready — the GoFish "easy mechanism" pass hid the reliability problems Redo exposed.

---

## Part 2 — Readiness scorecard (what's at level / what isn't)

✅ Ready · ⚠️ Shaky · ❌ Missing · 🔧 Designed-not-built

| Component | Rating | Evidence / gap to the bar |
|---|---|---|
| **sms-brief** (Layer A) | ✅ | Reliable across all 4 runs. Soft spot: goes web-led when there are no transcripts (GoFish). |
| **case-study-developer** (Layer B) | ⚠️ | GoFish 5.5→fixed; **Redo regressed**: invented an "Angles A–F" taxonomy it's explicitly told *not* to make, under-flooded then padded with cringe, and didn't mine the call corpus for the proven language until told. Capability is fine; **reliability is not.** |
| **sms-draft** (Layer C) | ⚠️ | Can beat a human (~8/10). But the **QA gate misfires**: "mechanism welded to case in T1 = auto-fail" would have killed Redo's *actual winning* split shape; banlist over-applied (killed colloquial "%"). |
| **playbook** | ✅ mostly | Strong tone bible + 17 winners. But **agency-offer-biased** — no tool/product winner like Redo; `offer-matrix.md` on hold. |
| **call-corpus-search** | ⚠️ | Works well, but **not auto-invoked** — the closers' proven language (Henry/Colby) sat unused in Redo until Aaman pointed at it. |
| **evals** | ❌ | Test correctness/guardrails, **not excellence** — won't catch a slide back to 5/10. |
| **evergreen DB** | 🔧 | Spec done (`evergreen-db-spec.md`); Hilal builds. The compounding layer — **deferred; not needed until there's send volume/data.** |
| **Direction Sheet** (pre-copy hypothesis) | 🔧 | Designed; would prevent ~half the Redo friction. Not built. |
| **runbook** (end-to-end flow) | ❌ | **#1 hand-off blocker.** |
| **decision rules** (mechanism-vs-omit, lever choice, relevance weight) | ❌ | Implicit, in Aaman's head, scattered across references. |
| **relevance / Clay ideation** | ❌ | No method for ideating per-prospect Clay variables or making relevance read **human, not mail-merge**. It's the **heaviest rubric weight (30%)** and was the weak spot in Redo. See the note below. |
| **exemplar gallery + calibration set** | ❌ | A junior can't self-calibrate 8 vs 5 without graded end-to-end examples. |
| **performance metrics** | ❌ | No reply / booked-call data yet (greenfield) — **deferred until live sends; the weekly loop isn't needed yet.** |

### Verdict vs the launch bar: **NOT READY**

Quality is reachable; **consistency, speed, and hand-off-ability are the gaps.** Priority order of fixes:

1. **Systematize what only Aaman supplies** (Part 3) — the highest-leverage gap.
2. **Build the Direction Sheet** — forces the upfront judgment that prevents wrong-frame runs.
3. **Build a relevance / Clay ideation method** — heaviest rubric weight, current weak spot (see note below).
4. **Harden case-study-developer + fix the QA gate** — kill the off-script + misfire bugs.
5. **Write the runbook** — makes it hand-off-able at all.
6. **Run the hard-mechanism (SEO/GEO) stress test** — the #1 missing data point; the real audit.

> **Note — the relevance / Clay gap (Aaman flagged).** Relevance is 30% of the score and the system has *no*
> method for it. We need a way to **ideate the per-prospect signal**: which Clay variables to pull (role, recent
> launch, tech-stack, directory, hiring, etc.), how to **phrase them so they read human, not mail-merge**, and
> when relevance should lead vs. sit quiet (ties to Part 3 #8 — unique offer leans on mechanism, commodity offer
> leans on relevance). This becomes its own reference + a Direction Sheet input (the reserved per-prospect slot).
> *Not built yet — worth adding.*

---

## Part 3 — What only Aaman currently supplies (the brilliance to systematize)

> **STRAWMAN — redline hard.** The judgment *you* bring that a handed-off strategist probably won't — the reason
> the system "only works when you drive it." Stated as **general principles, NOT the one-off Redo instances that
> surfaced them** — the point is the durable judgment, not the example (don't bake the instance). Each has a
> **fix** and an **owner** (S = encode in skill · D = Direction Sheet · T = strategist training · QA = QA/voice gate).

| # | The judgment you supply (the principle) | Why it matters | Fix → owner |
|---|---|---|---|
| 1 | **Read the awareness level, then pick the frame** — is the buyer solution-aware (→ differentiate) or solution-unaware (→ make them *realize* the gap)? | Wrong frame = every line is off, before a word is written | **awareness/sophistication** question → **D** + a first step in case-study-developer → **S** |
| 2 | **Diagnose before re-writing** — when prior copy underperformed, find *why* it didn't land first | Stops repeating the same miss | Optional "what hasn't worked" input + a diagnose step → **S** |
| 3 | **Mine the real sales-call language first** — how the closers actually pitch + what prospects bite on | The best ammo lives in the calls and gets left there | **Auto-invoke call-corpus-search** *before* flooding → **S** |
| 4 | **The taste filter** — cut lines that are clever-but-hollow or don't read like a person typed them | Stops garbage shipping | per-line QA with examples + a calibration set → **QA / T** |
| 5 | **Choose the frame/wrapper** that fits the offer + persona (builder / peer / partner / …) | The wrapper *is* the hook, esp. for a novel offer | a **frame/wrapper menu** → **S** |
| 6 | **Flood real volume, then cut** — never hand a thin menu | The skill under-floods by default | a **numeric floor + self-count** → **S** |
| 7 | **Structure is offer-dependent** — know when to break the default anatomy (a unique offer can lead on the hook, proof second) | A blanket "anatomy rule" kills valid shapes | make the QA anatomy rule **offer-shape-aware** → **QA** |
| 8 | **Calibrate how much relevance the offer needs** — unique offer leans on the mechanism; commodity offer leans on relevance | Spends words where they earn the reply | encode the dial → **S / D** (+ the relevance gap below) |
| 9 | **Pick the proof and how to frame it** — which case leads, what number, in the persona's own unit | The right proof for the right reader | a Direction Sheet decision → **D** |
| 10 | **Rules serve the human read, not the reverse** — apply the banlist/anatomy with judgment, finish with a human polish (cadence, casual markers, signature) | The last 10% that makes it sound like a person | a voice-profile polish pass, judgment over blanket rules → **QA / T** |

**This list is two things at once:**
- the **spec for hardening the skills** (the S/QA items), and
- the **strategist-training checklist** (the T/D items — what a new hire must learn to supply, or what the system must supply *for* them).

It's the concrete, run-grounded version of "systematize the individual brilliance." When every row has an owner
and is built, an unaided strategist run should clear the launch bar — that's how we'll know the audit passed.

---

## How we'll know it worked (verification)

- After encoding each Part-3 item: does the **next real run need fewer rounds** for that move? (speed + consistency)
- Re-run this audit after the **hard-mechanism stress test** — does the system behave as the scorecard predicts?
- The audit is **PASS** only when a new strategist clears the launch bar unaided. Until then: beta.
```
