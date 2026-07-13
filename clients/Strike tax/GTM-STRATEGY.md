# Strike Tax — GTM Strategy (STRAWMAN — redline me)

**Campaign:** OBBBA retroactive R&D refund — **≤$31M deadline sprint** (election window closes **July 6, 2026**, ~6 days).
**Date:** 2026-06-30 · pairs with [CONTEXT.md](CONTEXT.md).
**Goal:** turn "run the whole ≤$31M market with FOMO" into a *targeted* list where every prospect provably does **U.S. R&D**, matched to the vertical where we have the strongest **named proof + dollar result**.

---

## 1. The strategy in one line
We don't blast "do you do R&D?" — we **infer R&D from engineer headcount**, target the verticals where we have **named clients + big credit results**, and ride the **July 6 deadline** as the spine. Lead with **Software** and **Manufacturing** (most names + best historical conversion), use **Engineering's $3.7M** as the credibility flex.

---

## 2. Named-proof density map (where can we lead with NAMED credibility?)
Counting the clearable, paid-in-full roster in [case-study-client-names-by-vertical.md](source/case-study-client-names-by-vertical.md), bucketed by R&D-fit quality:

| Vertical | Named clients (clean R&D fit) | Borderline / verify | Dollar proof we own | Historical outbound signal |
|---|---|---|---|---|
| **Software & Tech** | **~24** (SaaS 15, Cyber 3, HealthTech 4, AI/other ~2) | ~19 (agencies/dev-shops/services — R&D *maybe*) | Cyber **$668K**, SaaS **$588K**, AI **$575K**, Fintech **$366K**, Blockchain **$245K**, IT $550K, AdTech $560K | ★ "Most leads came from Software" |
| **Manufacturing (+ Food/Bev/Ag)** | **~18** (machinery/metals/consumer-goods 13, ag/food-bev 5) | ACS Scientific, Brewer Intl, Leisure Design | Automotive **$657K**, Hemp/Ag **$650K**, Graphite **$304K** | ★ "Most leads came from Manufacturing" |
| **Engineering** | **~6** (Geostructural, Venturi, Welch, Monument, BetaJones; PacRim verify) | Pyramid Heating (HVAC, weak) | **Robotics $3.7M** 🚀, Civil $351K, Structural $308K | ★ "Engineering engaged — civil, structural, robotics" |
| **Architecture** | **~6** (Burton, DXU, Batir, Designlab 252, Riverstone, Prefix DFMA) | — | soft — one-pager "36% / $1M+", no clean single case in our set | — |
| **Medical/Pharma** | **~2** (Microbe Formulas/BioCore, LaserMD) | Westchester Eyes (weak), Enterprise Architects | weak — $151K biotech *proxy* only | high-value **inbound**, not proven outbound |
| **Aerospace/Defense** | **0 cleared** | — | none named | use Atlantis (defense-adjacent) if forced |

**Takeaway:** named density and dollar proof both concentrate in **Software + Manufacturing**. Engineering is a small list but owns the single most jaw-dropping number ($3.7M). Architecture/Pharma/Aerospace are thin — don't lead with them.

---

## 3. Vertical prioritization (what we run, in what order)
Ranked on **named density × dollar proof × clean R&D fit × historical conversion**:

- **WAVE 1 (ship first — volume + proof):**
  - **Software/Tech** → sub-segments SaaS, Cybersecurity, AI/Fintech. Anchor proof: Cyber $668K / SaaS $588K / AI $575K.
  - **Manufacturing** → machinery, metals/fabrication, consumer products that *build* things, + Ag/Food-Bev. Anchor proof: Automotive $657K / Hemp $650K.
- **WAVE 2 (credibility flex, smaller list):**
  - **Engineering** → civil/structural/robotics. Anchor proof: **Robotics $3.7M** (lead creative with the big number even though the list is smaller — it's a high-intent niche blast).
- **WAVE 3 (only if time/credits allow):**
  - **Architecture** (named list OK, soft $ — pair with the 36%/$1M+ one-pager), **Pharma** (thin — better as inbound). **Aerospace: skip** for named-led.

> Per [CONTEXT.md](CONTEXT.md): the case studies are all **TY 2016–2021** → they prove *Strike finds big credits*, NOT the OBBBA retro. In copy: **proof = the numbers, urgency = the July 6 window.** Keep them separate.

---

## 4. The targeting thesis: **engineer headcount = the qualification proxy**
The buyer's #1 objection is *"we don't do R&D."* We don't argue it — we **pre-qualify around it.** A company with **10+ U.S.-based technical employees** almost certainly generates qualifying QREs (wages drive the credit). So the whole list-build reduces to one question Clay can answer:

> **Does this company have ≥10 U.S.-based engineers/developers/scientists, ≤$31M revenue, in a target vertical?**

That single filter does the heavy lifting the cold copy can't. It also auto-kills the disqualifiers (offshore R&D, too-small, pure-service firms).

---

## 5. The Clay build (what "Clay stuff" to do)
Status: workspace **has credits**, **no subroutines built yet** → we build a fresh enrichment table. Recommended waterfall, in order (filter hard *early* to save credits — don't phone-enrich the raw list):

**Step 0 — Source companies (two feeds):**
- **(A) Lookalike seeds (highest quality):** feed the **named roster clients** as seeds → find similar companies. Mirrors who actually pays Strike. Start with Software seeds (SecurEnds, Cloverleaf, Aatrix…) + Manufacturing seeds (Atlantis, CORE 4X4, Simolex…).
- **(B) ICP filter pull (Apollo/Sales Nav/Clay search):** industry = target verticals · HQ = US · employees 10–200 · revenue ≤$31M.

**Step 1 — Company firmographics** (`find-and-enrich-company`) → **filter immediately:**
- Revenue **≤$31M** (HARD — campaign eligibility) and ideally **≥$3–5M** (enough payroll to matter).
- Employees **10–200**. HQ country **= US**. Industry/NAICS in scope. Founded year (flags <5yr + <$5M = startup payroll-offset angle).

**Step 2 — THE KEY LAYER: technical headcount + geo** (the qualifier):
- Count employees by function/title: *Engineer, Developer, Software, R&D, Research, Scientist, Chemist, Designer (technical), DevOps, Data/ML, CTO/VP Eng.*
- **% of those who are U.S.-based** → drop companies whose engineering is majority offshore.
- Keep **≥10 U.S. technical employees** (5–10 = marginal bucket; <5 = drop).
- R&D-active signals (bonus, great for personalization): open engineering reqs, USPTO patents, recent product launches.

**Step 3 — Trigger layers (prioritize + personalize):**
- Recent funding (burn pressure → *non-dilutive capital* angle). Hiring engineers now (active R&D). Patents filed (slam-dunk R&D evidence + a killer opener).

**Step 4 — Decision-makers** (`find-and-enrich-contacts-at-company`) — only on Step-2 survivors:
- Titles: **CFO + Founder/CEO first** (feel the cash pain, own the call), then CTO/COO, VP/Dir Finance, Controller, Tax Director.
- Enrich **verified work email** (email channel) **+ mobile/direct phone** (SMS) via waterfall. *Phone-enrich only qualified survivors* — that's the expensive step.

**Step 5 — Scrub + route:**
- Remove **block-list** companies ([sheet](https://docs.google.com/spreadsheets/d/1pX4JXULLUu7vDJqcRG88v1iQt8PC16ECguwlCMUUAko/edit?gid=1489239345#gid=1489239345)). Dedupe. **Split by vertical** so creative matches that vertical's named proof. Push to email sequencer + SMS tool.

**Credit discipline (6-day sprint):** enrich Software + Manufacturing lookalike seeds first; hard-filter on revenue + engineer count *before* spending on phone/email waterfalls. Don't enrich Wave 3 until Wave 1 is firing.

---

## 6. Hard dependencies / caveats (confirm before/while building)
- **SMS = A2P 10DLC must be live** (EIN doc on file). If not registered, **email-first** while it clears — but still phone-enrich in Clay so SMS is loaded and ready. → status?
- **Deadline mechanics (ask Strike, today):** a full study takes 4–8 wks, so nobody *completes* by July 6 — the deadline is to **engage/preserve the claim** in time. Also the **2022** amend deadlines (Mar/Apr 2026) already passed → live retro years are likely **2023–2024 + the July 6 election**. Get the exact claimable scope so our FOMO is *true*, not just loud.
- **Named-client welding guardrail** (from [case-studies-detailed.md](source/case-studies-detailed.md)): pair the **vertical**, not the **invoice**, unless Strike confirms a specific name↔result. Ask them to clear 2–3 we can quote outright.

---

## 7. Open decisions for you
1. **Wave 1 confirm:** Software + Manufacturing first — agree? Or do you want Engineering's $3.7M leading because the number is so strong?
2. **Source feed:** want me to start with **lookalike-seed** enrichment (rec) or do you already have a list to import into Clay?
3. **A2P 10DLC status** — live or pending? (decides SMS-now vs email-first.)
4. **Green-light Clay spend:** say go and I'll run a first **find-and-enrich batch on the Software + Manufacturing lookalike seeds**, hard-filter to ≤$31M + ≥10 US engineers, and hand back a qualified count before we spend on phone/email enrichment.

---
*Next once you confirm: pick Wave-1 vertical → I run **sms-brief** (Layer A) on it → case-study-developer on its anchor ($668K cyber / $657K auto / $3.7M robotics) → sms-draft + email, July-6 deadline as the spine.*
