# Variable Schema + CTA Patterns

> The slots that go into a draft, and the soft-CTA patterns to pull from at Step 3. Keep variables minimal —
> only what actually personalises the text. Always `{{double_braces}}`.

## Variables

**Core (almost always):**
- `{{first_name}}` — the prospect's first name.
- `{{company}}` — their company.
- **Signature** — the sender's sign-off, however the client formats it ("– Courtney, Kynship"). Set per client.

**Personalisation / Clay (when available — these are what lift relevance):**
> **The relevance slots and how to use them live in `sms-playbook/enrichment-menu.md`** (which enrichment
> buys which rung/lever, how to weave it, when not to) — that's the single source; don't restate it here.
> The headline ones: `{{competitor}}` (FOMO, **never fabricated**), `{{ICP_signal}}`/`{{dream_icp}}` (the
> highest-leverage per-prospect signal), `{{relevant_search_term}}` (the SEO/bridge slot), `{{relevance}}`
> (a true observation), `{{niche}}`/`{{product_category}}`/`{{subniche}}` (the rung-1 niche floor). Climb to
> the highest rung the data allows (`relevance-engine.md`); leave per-prospect vars as Clay merge slots.

**Case-study slots (for templating the proof line):**
- `{{case_client}}`, `{{result}}`, `{{timeframe}}`, `{{keyword}}` — the developed proof, dropped into the skeleton.

## Openers / hooks (PROPOSE the proven ones — don't default to "bit random")

The opener does heavy lifting; **propose the strongest fit from the proven winner hooks** instead of
defaulting to a weak "bit random." Pick by persona/sophistication:
- **Cracked-the-code** (curiosity/FOMO, high-soph) — "you don't know me but I think we cracked [the hard
  thing] for [niche]" *(W15/W16/W17)*.
- **Light disarmer** — "I know this is random but…" / "bit random, but…" *(W1)* — fine, but it's the floor,
  not the ceiling; reach higher when the case allows.
- **Permission opener** — "feel free to ignore if [a graceful fit/priority out], but…" *(W2/W8)* — never put
  the prospect's actual pain after the "if" (that's self-defeating; see QA Q14).
- **Capacity question** — "could [company] handle [n extra units] right now?" *(W4)*.
- **Credibility lead** — "it's [name] — I used to [real credential], and just helped…" *(W7)*.
- **Discovery source** — "found [company] on [directory]…" *(W6)* — only when true.

Match the hook to the lever + persona; if you propose "bit random" for a high-soph buyer when a stronger
hook fits, that's a miss.

## CTA patterns (soft — and every one carries relevance; vary them, don't repeat)

Every CTA must be **soft *and* tied to something for them**, and the skill should **wordsmith fresh
variation**, not slot the same "could do the same for {{company}}" every time. Avoid a bare "can we chat" /
"give me a ring" with no relevance. Variety to draw from:
- **Show-the-strategy:** "think [company] could take advantage of this — could I show you the strategy?" ·
  "could I show you how this'd work for [company]?"
- **Idea-give:** "had a couple of [niche] ideas for [company] — worth a quick look?" · "I've got a few
  [niche] creators/angles in mind for [company] — worth exploring?"
- **Soft-observation hook:** "I don't see many in [niche] doing this yet — think [company] could? could I show u how?"
- **Permission/low-pressure:** "not asking for your business — but could I show you how [company] could do
  this in [niche]?"
- **Value-give:** "happy to share what's working in [niche] right now."
- **Capacity / soft-scarcity:** "room for one more [niche] brand this quarter — worth exploring?"

Pull 2-3 at Step 3, match to ticket/persona (high-ticket → softer), push the **relevance** ("for [company]
in [niche]") as far as the data allows, and **never repeat the CTA across T1/T2** (and never two question
marks in one text).

**Vary for variety, never at the cost of aimedness.** When two variants want the same strong relevance
hook, it's fine to reuse it — a slightly-repeated *aimed* line ("haven't seen many [niche] brands run it
this way") beats a fresh *generic* one ("wild what that does"). If you must differentiate, change the
**case detail or the CTA**, not by dropping the niche/them hook into a generic reaction (that's rung 0,
QA Q4). `sms_qa.py` will flag a T2 that personalizes only on `{{company}}`.
