# Strike Tax — Copy Pattern Analysis (STRAWMAN — redline me)

**Date:** 2026-06-30 · corpus: [source/previous-copy-corpus.md](source/previous-copy-corpus.md)
**Question answered:** what patterns are running, what's been tested vs. static, what are we leaving on the table, and how do we fix FOMO + the "already claimed?" problem.

---

## 1. You're running ONE template, not a campaign
Strip the corpus down and almost every SMS is the same 2-text skeleton:

> **Text 1:** `it's {SDR} from Strike Tax - your {engineering|dev} team's salaries at {{company}} likely qualify for R&D tax credits going back 3 yrs. we recently helped {SecureCircle $668k} for 2022-2024`
> **Text 2:** `there's a federal deadline July 6 to claim 22/23/24… {1–2} weeks away. want an estimate? (success-fee basis)`

What actually changes month-to-month: **the SDR name, the team noun (engineering/dev), and the countdown number.** That's it. Same proof (SecureCircle), same structure, same two levers. **Your instinct is right — it's been one message for a month.**

Real variation only shows up *earlier* in the timeline (Feb–Mar) and got abandoned:
- Feb: "wayy too random" + big numbers ($750k/$2.7M)
- Mar: "bit random" + **vertical-paired** proof ("a manufacturer in texas") + "could be sitting on something similar"
- May→Jun: collapsed into the single "salaries…SecureCircle $668k" template.

So you didn't run *tests* — you **converged on one line and froze.** That's the thing to break.

---

## 2. The lever audit — you're using 4 of ~13 (this is the money left on the table)
You felt "we only went for 3–4 issues." Confirmed — here's the map.

**USED (4):** ① "you likely qualify" (mistaken-belief flip) · ② deadline FOMO · ③ missed past credits / retroactive recovery · ④ risk-reversal (success-fee/audit) — and ④ is usually a throwaway PS.

**SITTING UNUSED (9), all straight from the onboarding pains/dreams:**

| # | Unused lever | Best niche | Why it bites |
|---|---|---|---|
| ⑤ | **Non-dilutive capital / extend runway** ("fund engineers without giving up equity") | VC-backed SaaS/AI | founders feel burn weekly; this reframes credits as *fundraising* |
| ⑥ | **Valuation uplift** (refunds → retained earnings → restate financials → higher valuation) | CFO/founder pre-raise/exit | CFO catnip; nobody else says it |
| ⑦ | **Your CPA/last provider underclaimed** ("you left money on the table") | the **already-claimed** segment | opens the prospects you currently throw away (see §3) |
| ⑧ | **Big firms take 30–35% + you do the work; we cap 20% + do it all** | anyone with a current provider | concrete, comparative, ownable |
| ⑨ | **Missed state credits** (40 states, stack fed+state, +30–50%) | multi-state mfg/eng | "you claimed federal but left the state half" |
| ⑩ | **Claim BOTH credit AND deduction** (double benefit) | tax-savvy CFO | counterintuitive → curiosity |
| ⑪ | **Failed/abandoned/shelved projects still qualify** | "we're not inventing anything" skeptics | directly kills the #1 objection |
| ⑫ | **Peer/competitor FOMO** ("companies your size are claiming six/seven figures") | all | social proof > deadline for the un-urgent |
| ⑬ | **Audit fear dissolve as a LEAD** (not PS) ("claiming doesn't raise audit risk; we 100% defend") | conservative mfg/owner-run | removes the silent reason they ignore you |

**The point:** you have a 13-lever arsenal and you've been firing 1–2 per message, same two every time. Even just rotating ⑤⑥⑦⑫ into the mix doubles your angles overnight.

---

## 3. The biggest hole: you assume they HAVEN'T claimed — so half the market is wasted
Every message is built for one persona: *the founder who never claimed.* "not sure if you claimed… if you didn't, that window just closed." But the market splits in two:

- **Hasn't claimed / doesn't know** → current copy fits. Deadline FOMO lands.
- **Already claimed** → current copy is irrelevant *and* you've burned the touch. But this is the segment with **budget, a tax function, and a provider they may already resent** — and Strike's entire mechanism ("we find what others missed, we stack state, we max QREs") is *built for them.* You're discarding your warmest fit.

**Your instinct — "just ask if they've claimed" — is the unlock.** Make the opener a real qualifying question instead of an assumption:

> "Quick one {{first}} — has {{company}} already claimed R&D credits for 2023–24, or is that still on the table?"

A question gets replies (engagement), and the reply **self-segments the list for you:**
- **"No / not sure"** → deadline + "you likely qualify" + modeled estimate (your current play, refined).
- **"Yes, we claimed"** → pivot to ⑦⑧⑨: *"who ran it — did they get your state credits too? Most second opinions we run find 20–40% more, no charge to check."* This is the second-opinion mechanism from the onboarding, finally used.

That's two campaigns out of one list, and it converts the segment you're currently throwing in the bin. **Strongly recommend building this as the new spine.**

---

## 4. Fix the FOMO — right now it's inconsistent and partly untrue
Three different deadline stories shipped:
- "2022 closed, 23–24 open" (May/Mar) vs. "claim 22, 23, 24 all at once" (Jun) — **direct contradiction.**
- Per our research, the **2022 amend deadlines (Mar/Apr 2026) already passed** → "claim 22/23/24 all at once" is likely **wrong now.** Live retro years = **2023–24 + the July 6 election.**

**One true story, then layer FOMO so it doesn't die on July 7:**
1. **Hard date:** "July 6 is the federal election deadline to lock the 2022–24 retroactive reversal." (confirm exact scope with Strike *today*.)
2. **Rolling deadline (survives any single date):** "every month you wait, another tax year ages out of the 3-yr amendment window." Urgency that never expires.
3. **Peer FOMO (⑫):** "companies your size are quietly pulling six figures back before this closes." Works even on the deadline-numb.

→ After July 6, pivot the spine from "the date" to **rolling + peer + valuation** so the campaign has a life past next week.

---

## 5. Credibility leaks — fix before scaling (these quietly kill reply rates & are a liability)
- **Three conflicting aggregate stats:** $300M+/1,100 (site) · $200M+/800 (onboarding) · **$823M+/1,025 (email)**. Lock ONE true set; use it everywhere.
- **Fabricated client-specific numbers:** "Atlantis Industries claim $1.2M" (not a real case), "hvac supplier recover $657,000" (that's the *automotive* number relabeled). This is the welding-guardrail violation, live. **SecureCircle $668k is your one clean, verifiable anchor — that's why the SaaS email "worked."** Standardize on verifiable anchors; vertical-pair everything else ("a manufacturer in TX," not a fake name).
- **QA bugs shipping:** raw merge field mid-sentence ("…repeal means Thank god it's natural could recover…"), and a **machinery template sent to a hair-care company.** Pre-qualify by vertical *before* send.
- **Year ranges** drift ("2022-24", "2023-25", "22-24") — pick one format.

---

## 6. What's already working — copy its DNA
The two emails you flagged as "worked decent" share a recipe the frozen SMS template lost:
- **Question opener** ("r&d credits for 22?", "did you file for the retroactive refund?") — not a pitch.
- **One clean, named, verifiable anchor** (SecureCircle) **+ a disarming human detail** ("12 people, encryption product, nothing out of the ordinary" → kills "we're not special enough").
- **A modeled "what YOU could get" number** ("Klima could recover ~$400k") — makes it about them.
- **Low-friction ask** ("15 mins on my end", "no meeting needed").
- **Risk-reversal as a confident PS** (success-fee + lifetime audit defense).
- Machinery one also nailed peer-proof: *"most we assess qualify for $200–800k they didn't know existed."*

That recipe = the template to scale. The losing sends are the generic same-skeleton blasts with no modeled number and a stale proof.

---

## 7. Recommended direction (ties to the GTM plan)
This is exactly where the [GTM-STRATEGY.md](GTM-STRATEGY.md) engineer-count pre-qualification pays off, and it matches your own read:

1. **Pre-qualify on signals at scale** (Clay: ≥10 US engineers, ≤$31M, target vertical) so we're not guessing at fit.
2. **Open with the question** ("already claimed 23–24, or still on the table?") → self-segments claimed vs. not.
3. **Branch the copy** by answer (not-claimed → deadline+estimate; claimed → second-opinion/state-credits).
4. **Rotate levers by niche** (SaaS→⑤⑥⑫ runway/valuation/peer · Mfg→⑧⑨⑬ fee/state/audit · all→⑪ "failed projects count").
5. **Standardize proof** (one aggregate stat; SecureCircle-class verifiable anchors; vertical-pair the rest).
6. **Layer FOMO** (hard date → rolling → peer) so it outlives July 6.

---

## Open decisions for you
1. **Adopt the "ask if they've claimed" opener as the new spine?** (my strong rec — it doubles your addressable segment.)
2. **Which 2 niches to write first?** (rec: SaaS + Machinery — most names, both have a "worked decent" email to build on.)
3. **Confirm the exact deadline scope with Strike** (what's truly claimable as of June 30) so FOMO is true.
4. **Lock the one true aggregate stat** ($300M/1,100? confirm with Strike).
→ Then I run sms-brief on niche #1 and draft the branched SMS + email with the new spine.
