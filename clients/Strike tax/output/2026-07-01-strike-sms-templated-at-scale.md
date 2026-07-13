# Strike Tax — SMS templates at scale (variablized + "not asking for your business" CTA)

Date: 2026-07-01 · One skeleton, run across the whole list. **Clay fills two layers:** (1) per-**vertical** case vars (which named client + result + descriptor), (2) per-**prospect** merge vars (name, company, optional signal). Education-play spine + the July-6 window. Validated against striketax.com ("overpaid" = their word; 2022-2024; july 6 = ≤$31M election).

---

## ★★ FINAL — SEND-READY (3-day sprint → deadline MONDAY, July 6)

**Structure:** T1 = identity + peer-eligibility + light rule + **question**; T2 = **proof** + line-break + no-pitch CTA. (Tightened to ~190/180 — profile length. Dropped the "60-yr molder" descriptor — case is vertical-matched per row already.)

**V1 — default (light education)**
- T1: Hi {{first_name}}, it's {{sdr}} from Strike Tax - random one, but most {{peer_group}} qualify for R&D refunds and never claim them. the rule that blocked 22-24 got repealed last year - have you claimed yours yet?
- T2: we just helped {{case_client}} recover {{case_result}}.
  not asking for your business - but the deadline's monday, so could I at least share an estimate of what you could still claim?

**V2 — mechanism named (anti-fishy: 5-year write-off)**
- T1: Hi {{first_name}}, it's {{sdr}} from Strike Tax - random one, but {{peer_group}} had to write off R&D over 5 years since 2022, so most overpaid and never claimed it back. that just got repealed - have you claimed 22-24 yet?
- T2: we just helped {{case_client}} recover {{case_result}}.
  not asking for your business - but the deadline's monday, could I at least share an estimate of what you could still claim?

**V3 — Section 174 named (CFO / tech founder)**
- T1: Hi {{first_name}}, it's {{sdr}} from Strike Tax - random one, but section 174 had most {{peer_group}} overpay on R&D from 22-24 without knowing it. it just got repealed - have you claimed those refunds back yet?
- T2: we just helped {{case_client}} recover {{case_result}}.
  not asking for your business - but since the deadline's monday, could I share an estimate of what you could still claim?

**V4 — proof-FIRST (per profile; the A/B against V1-3)**
- T1: Hi {{first_name}}, it's {{sdr}} from Strike Tax - random one, but we just helped {{case_client}} recover {{case_result}} in R&D refunds for 22-24.
- T2: most {{peer_group}} qualify and never claim it - the rule blocking it got repealed last year. have you claimed yours? not asking for your business, but the deadline's monday - could I share a rough estimate?

**Rendered (V1, American Plastic):**
- T1: Hi Dave, it's Erika from Strike Tax - random one, but most injection molders qualify for R&D refunds and never claim them. the rule that blocked 22-24 got repealed last year - have you claimed yours yet?
- T2: we just helped Atlantis Industries recover $657k. // not asking for your business - but the deadline's monday, so could I at least share an estimate of what you could still claim?

**The real A/B:** V1-3 (question-first, proof in T2) vs V4 (proof-first) — tests whether the eligibility line carries T1 without a number.

**T1 swap-bank — peer-eligibility (makes them self-ID as qualified; "eligible/more eligible" was the awkward version — these fix it):**
1. most {{peer_group}} qualify for R&D refunds and never claim them  ← *default*
2. {{peer_group}} like you are exactly who this is for - most just never claim it
3. most {{peer_group}} don't realize they qualify for R&D refunds
4. (CFO/174) since section 174 got repealed, {{peer_group}} can claim back the R&D they overpaid on in 22-24
- ⚠️ **Do NOT use "most {{peer_group}} have already claimed this"** — untrue (most haven't; that's the opportunity) + self-defeating (if everyone did it, why text them?). Use *eligibility* ("qualify"), not false social proof.

**CTA phrasings ("what you'd get back"):** "could I at least send you a rough number of what you'd get back?" · "could I at least show you what you could claim back before it closes?" · "could I at least run you an estimate of what's recoverable?"

**Locked knobs (sprint picks — override if needed):** {{case_result}} Atlantis = **$657k** (real, defensible) · {{sdr}} = **Erika** · deadline said as **"monday"** (July 6). Verify each prospect ≤$31M + profitable-in-22-24 before send.

---

## 1. Variable legend
| Variable | What it is | Example fill (American Plastic) | Filled by |
|---|---|---|---|
| `{{first_name}}` | contact first name | Dave | list |
| `{{company}}` | prospect co. (short form) | American Plastic | list |
| `{{sdr}}` | sender name | Erika | fixed / rotated |
| `{{peer_group}}` | plural noun for their tribe (education/FOMO line) | injection molders | **vertical map** |
| `{{case_client}}` | named case client (leadership-authorized) | Atlantis Industries | **vertical map** |
| `{{case_descriptor}}` | the relevance bridge — how the case relates to them | another 60-year injection molder | **vertical map** |
| `{{case_result}}` | the $ figure (real case result) | $657k | **vertical map** |
| `{{relevance_hook}}` *(optional, rung-3)* | a real per-prospect signal | "the mold + tool design you do" / a Clay signal | Clay enrichment |
| `{{days_left}}` *(optional)* | live countdown to july 6 | "5" | computed at send |

> **Rule:** keep `{{case_result}}` **one consistent number per case client** (don't vary the number across a list — vary the lever + relevance). Confirm the Atlantis figure ($657k real-case vs your $1.2M) once, then lock the column.

## 2. The scale engine — vertical → case map (swap these columns per segment)
| Prospect vertical | `{{peer_group}}` | `{{case_client}}` | `{{case_descriptor}}` | `{{case_result}}` |
|---|---|---|---|---|
| Plastics / injection molding | injection molders | Atlantis Industries | another 60-year injection molder | $657k |
| Machinery / custom mfg | manufacturers | Atlantis Industries | a custom manufacturer like you | $657k |
| Automotive parts | auto companies | CORE 4X4 | an auto parts maker like you | $657k |
| Chemicals / materials | materials companies | Brewer International | a specialty chemicals maker | $304k |
| Engineering (civil/structural/robotics) | engineering firms | *(engineering case)* | an engineering firm like you | $3.7M |
| SaaS / software | software founders | SecureCircle | a software team, acquired by CrowdStrike | $668k |
| Cybersecurity | cybersecurity teams | SecureCircle | a cyber team, acquired by CrowdStrike | $668k |

*(One skeleton below serves every row — Clay just swaps these four columns. Verify each prospect is ≤$31M + profitable-in-22-24 before the deadline version.)*

---

## 3. The templates (with the "not asking for your business" CTA)

> ⚠️ **Anti-fishy rule:** never say the vague "a 2022 tax rule made you overpay, claim it back before the deadline" — that's the exact shape of a refund *scam* (no mechanism, just "you're owed money, act now"), and everyone says it. **Name the actual mechanism** (R&D had to be written off over 5 years / Section 174 repeal) — that specificity is what a real expert says and a scammer can't. This explains the *rule*, not their business (still no over-explaining what they do).

### Template A — education-LED (name the rule — this is what kills the "fishy")
- **T1 (plain mechanism — owners):** Hi {{first_name}}, it's {{sdr}} from Strike Tax - random one, but since 2022 you've had to write off R&D over 5 years instead of upfront, which overtaxed a lot of {{peer_group}}. that just got repealed - 22-24 is refundable till july 6.
- **T1 alt (Section 174 named — CFO/finance/tech founders who know the 174 pain):** Hi {{first_name}}, it's {{sdr}} from Strike Tax - random one, but you know how section 174 forced everyone to amortize R&D over 5 years since 2022? congress just reversed it retroactively - so 22-24 R&D is refundable if you amend before july 6.
- **T2:** we got {{case_client}}, {{case_descriptor}}, {{case_result}} back doing exactly that. not asking for your business - but july 6's days away, could I at least run {{company}} a rough number so you don't miss it?

### Template B — proof-LED (case first, education + disarm-CTA in T2)
- **T1:** Hi {{first_name}}, it's {{sdr}} from Strike Tax - know this is random, but we recently got {{case_client}}, {{case_descriptor}}, {{case_result}} back in R&D tax credits.
- **T2:** a 2022 rule had companies overpay on R&D, congress reversed it so 22-24 is claimable till july 6. not asking for your business - just don't want you leaving it on the table with the deadline days away. could I at least show you what's there?

### Template C — permission-LED (softest; best for a guard-up owner)
- **T1:** Hi {{first_name}}, it's {{sdr}} from Strike Tax - feel free to ignore if {{company}}'s already handled this, but {{case_client}} ({{case_descriptor}}) just got {{case_result}} back in R&D credits.
- **T2:** honestly not asking for your business - but july 6 is the deadline to claim 22-24 and it's days away, so could I at least flag what you'd be walking away from? (you only pay if credits land)

---

## 4. CTA swap-bank — "not asking for your business, but could I at least…"
Drop-in T2 closers (why they disarm: money/IRS reads scammy → the no-pitch posture + a real deadline reframes it as a helpful heads-up, not a grab):
- `not asking for your business - but with july 6 days away, could I at least run {{company}} a quick number so you don't miss it?`
- `genuinely not trying to win your business - just don't want you leaving this sitting when it closes july 6. could I at least show you what's claimable?`
- `not asking for your business here - could I at least flag what {{company}}'s walking away from before july 6?`
- `no pitch - with july 6 days out, could I at least send you a rough estimate before it's gone?`
- `not asking you to switch anything - could I at least tell you if there's real money here before the deadline? (only pay if it lands)`

## 5. Worked example — Template A rendered (American Plastic Products)
- **T1:** Hi Dave, it's Erika from Strike Tax - random one, but since 2022 you've had to write off R&D over 5 years instead of upfront, which overtaxed a lot of injection molders. that just got repealed - 22-24 is refundable till july 6.
- **T2:** we got Atlantis Industries, another 60-year injection molder, $657k back doing exactly that. not asking for your business - but july 6's days away, could I at least run American Plastic a rough number so you don't miss it?

**Cyber render (same skeleton, case columns swapped; use the Section 174 T1 — tech founders know it):**
- **T1:** Hi {{first_name}}, it's Erika from Strike Tax - random one, but you know how section 174 forced everyone to amortize R&D over 5 years since 2022? congress just reversed it retroactively - so 22-24 R&D is refundable if you amend before july 6.
- **T2:** we got SecureCircle, a cyber team acquired by CrowdStrike, $668k back doing exactly that. not asking for your business - but july 6's days away, could I at least run {{company}} a rough number so you don't miss it?

---

## 6. Notes
- **Countdown:** templates say "days away" (evergreen through the final week). For the sprint, swap in `{{days_left}} days left` for a live ticker — strong FOMO, but only if the send fires same-day.
- **`{{relevance_hook}}` (rung-3):** to climb higher, prepend a real per-prospect signal in T1 ("saw {{relevance_hook}} - ...") — fill from Clay; never invent it (honest rung-1 beats fake rung-3).
- **Casing:** lowercase-casual as written; pull slightly more proper for old-school execs (test).
- **QA:** no %, absolutes only ✓ · disarmer + identity + named proof + result ✓ · question CTA ✓ · education traces to striketax.com ✓. Confirm ≤$31M + profitable-22-24 per prospect before the deadline line.
