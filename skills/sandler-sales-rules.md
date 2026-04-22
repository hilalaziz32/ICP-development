# Sandler Sales Rules — AI Skill for Copy & Sales Output Tweaking

**Source:** *The Sandler Rules: Forty-Nine Timeless Selling Principles* — David Mattson (adapted from David H. Sandler's Sandler Selling System, rooted in Transactional Analysis).

**Purpose:** A reference layer any AI agent can load before generating or refining SMS copy, cold emails, discovery scripts, objection handling, offer pages, or booked-call scripts. Use it to pressure-test copy against behavioral-sales principles that are OUTSIDE what raw ICP research can tell you.

---

## 🧠 Core Mental Model (use this before touching any copy)

Sandler's foundational claim:

> **"People make buying decisions emotionally, and justify them intellectually."**

Every prospect has three simultaneous voices (Transactional Analysis):

| Ego State | What it wants | In copy terms |
|-----------|---------------|---------------|
| **Child** (emotion) | "I want this." | Pain, desire, frustration, relief — the HOOK. Fires first. |
| **Parent** (permission) | "Is this the right/appropriate thing to do?" | Social proof, authority, "people like me", category norms. |
| **Adult** (logic) | "Do the numbers check out?" | Mechanism, ROI, timeline, specifics, comparisons. |

**Rule of thumb for SMS / cold copy:** Child FIRST (pain + emotional charge), Adult SECOND (mechanism + proof with specifics), Parent closes (permission/low-risk CTA). Skipping Child = no reply. Skipping Adult = flagged as hypey. Skipping Parent = ghosted at the CTA.

Map to [frameworks/sms_frameworks.md](../frameworks/sms_frameworks.md): the `Pain → Mechanism → Proof + Outcome` skeleton is already Child → Adult → Parent. Sandler just tells you *why* it works.

---

## 📜 The 49 Rules — Mapped to GTM Work

Each rule has: **the rule**, **what it actually means**, and **how an AI should apply it to this repo's artifacts** (SMS, cold email, discovery scripts, value props, objection responses).

### Part One: Core Concepts

**1. You have to learn to fail, to win.**
Separate the REAL-you from the ROLE-you. A failed test is data, not identity.
→ *Apply to:* copy iteration. When a segment/SMS dies, extract the lesson (wrong pain? wrong trigger? wrong UM?) — never rewrite as if the first draft was personally flawed. Pairs with [rules/copy-iterator.md](../rules/copy-iterator.md).

**2. Don't spill your candy in the lobby.** ⭐ HIGH RELEVANCE
Don't dump features/proof/expertise before the prospect has revealed their situation.
→ *Apply to:* SMS + email. A 3-line SMS that lists mechanism + 3 results + a case study + a calendar link = candy spilled. Keep one pain, one mechanism, one proof, one ask. Extra "value" early trains the prospect they don't need the call.

**3. No mutual mystification.**
Never let enthusiasm hide ambiguity. Confirm what was agreed, what's next, on whose terms.
→ *Apply to:* booked-call scripts, recap emails, objection handling. After any positive signal, *restate* the next step in explicit language ("So we'll hop on a 20-min call Thursday where I'll show you X — that right?").

**4. A decision not to make a decision is a decision.** ⭐
"Let me think about it" = No. Give permission to say No up front.
→ *Apply to:* CTAs. Frictionless ≠ vague. "If this isn't relevant, just say 'pass' — no worries" outperforms "let me know what you think." Low-risk NO = higher quality YES.

**5. Never answer an unasked question.** ⭐
Introducing a topic the prospect didn't raise invents objections.
→ *Apply to:* SMS, especially. Don't preempt "we're not cheap but…" or "I know you get a lot of messages like this…" — you just seeded the objection. Address only what the prospect surfaces. Strip "you're probably wondering…" phrasing from all drafts.

**6. Don't buy back tomorrow the product/service you sold today.**
After a yes, stress-test it. Surface buyer's remorse NOW, not after wire transfer.
→ *Apply to:* post-booking confirmation, sales call close. Add: "Before we lock this — what could come up in the next 48h that would make you want to pause?"

### Part Two: Execute

**7. You never have to like prospecting, you just have to do it.**
Focus on end result, not the activity.
→ *Apply to:* agency internal — reminder for volume targets, not copy.

**8. When prospecting, go for the appointment.** ⭐
Cold outreach ≠ selling. The ONLY goal of an SMS/cold email is the next micro-step.
→ *Apply to:* every SMS CTA. Stop pitching outcomes "why you should buy." The SMS sells the *15-min call*, not the service. Cross-check every draft: "Is this SMS trying to close, or trying to get a reply?"

**9. Every unsuccessful prospecting call earns compound interest.**
Volume + consistency compounds. Skipped days cost double.
→ *Apply to:* cadence design in [sops/](../sops/). Argue for consistent daily send volume over burst campaigns.

**10. Develop a prospecting awareness.**
Everything is a potential lead source if you're tuned in.
→ *Apply to:* trigger research. Expand trigger libraries beyond the obvious (hiring, funding) — conferences attended, podcast appearances, LinkedIn posts expressing pain.

**11. Money does grow on trees.**
Referrals + existing networks are underused.
→ *Apply to:* agency internal — post-close referral asks.

**12. Answer every question with a question.** ⭐
Answering commits you to a position before you know what they meant.
→ *Apply to:* reply-handling templates, objection library. When prospect asks "how much?" or "what do you do?", the AI should generate a clarifying reply, not a pitch: "Depends on X — what's driving the question?"

**13. No mind reading.**
Don't assume what a vague word means. Ask.
→ *Apply to:* reply parsing. If prospect says "interesting" or "maybe later" — drafts should ask "what specifically caught your attention?" not assume buying intent.

**14. A prospect who is listening is no prospect at all.** ⭐
If you're doing all the talking, they're not qualifying themselves.
→ *Apply to:* discovery scripts, sales call decks. Invert monologue sections to questions. On a booked call, salesperson should talk <40% of the time in discovery.

**15. The best sales presentation you'll ever give, the prospect will never see.**
Over-preparing a pitch = over-selling. They buy when THEY discover the fit.
→ *Apply to:* pitch decks — keep them short; the magic is in the discovery preceding them.

**16. Never ask for the order — make the prospect give up.** ⭐
Negative-reverse. Let them pull the sale toward themselves.
→ *Apply to:* SMS replies to lukewarm leads. Instead of "ready to book?", try "sounds like the timing might not be right — should I circle back in Q3?" — forces them to disqualify or re-engage.

**17. The professional does what he did as a dummy on purpose.**
Study your accidental wins. Convert them to repeatable process.
→ *Apply to:* agency internal — turn one-off wins into frameworks.

**18. Don't paint "seagulls" in your prospect's picture.**
Don't add uninvited details/promises/features to the prospect's mental image of the deal.
→ *Apply to:* SMS + proposal writing. Strip adjectives and "also we…" additions. The prospect's picture is the one that closes.

**19. Never help the prospect end the interview.**
Don't wrap up a call early just because it feels socially awkward.
→ *Apply to:* call scripts — don't let "well, I don't want to take up your time" end discovery prematurely.

**20. The bottom line of professional selling is going to the bank.**
Activity ≠ revenue. A full calendar of unqualified calls is a failure, not a win.
→ *Apply to:* internal metrics — qualified conversations > total appointments.

**21. Sell today, educate tomorrow.**
Prospects don't pay for education they didn't ask for.
→ *Apply to:* SMS/email. Cut the "did you know that 73% of agencies…" stat-as-hook. Only educate after they've expressed the pain.

**22. Only give a presentation for the "kill."**
Don't present until qualifying is complete. A presentation to an unqualified prospect is a free consulting session.
→ *Apply to:* sales process design — gatekeep the demo behind discovery.

**23. The way to get rid of a bomb is to defuse it before it blows up.** ⭐
Name the likely objection BEFORE the prospect does.
→ *Apply to:* sales scripts (NOT cold SMS — see rule 5). On a discovery call: "A lot of agencies we talk to think this is just another cold email tool — if that comes up for you, tell me early."

**24. Product knowledge used at the wrong time can be intimidating.**
Jargon dumps shut down the Child's curiosity.
→ *Apply to:* copy voice. Strip acronyms and technical detail from first-touch. Plain English, one idea.

**25. When you want to know the future, bring it back to the present.**
"How do you plan to decide?" → "Walk me through the last time you evaluated something like this."
→ *Apply to:* discovery scripts. Past behavior > stated intention.

**26. People buy in spite of the hard sell, not because of it.**
→ *Apply to:* [rules/anti_patterns_and_mistakes.md](../rules/anti_patterns_and_mistakes.md) — hypey close phrases ("limited spots," "act now") corrode trust with sophisticated ICPs.

**27. You can't sell anybody anything — they must discover they want it.** ⭐
The job of copy/scripts is to trigger *their own* realization.
→ *Apply to:* all SMS drafts. Instead of asserting "you have pipeline problems," ask the implicit question that makes them think it ("Still pulling pipeline from referrals after 3 years?").

**28. When under attack, fall back.**
Don't defend. Reflect the attack back as a question.
→ *Apply to:* objection responses. "Your pricing is too high" → "Compared to what you had in mind?" — not a justification.

**29. Your meter's always running.**
Your time has value. Unpaid extended scoping = giving the product away.
→ *Apply to:* agency internal — scope discipline.

**30. You can't lose anything you don't have.**
Prospects aren't "lost" until they were qualified and committed. Stop mourning cold leads.
→ *Apply to:* pipeline hygiene.

**31. Close the sale or close the file.** ⭐
No permanent "maybes." Either move forward or kill it and move on.
→ *Apply to:* reply-cadence logic. After N touches with no concrete next step, the AI should draft a "close-the-file" message ("I'll take you off this list — feel free to reach out when timing changes.")

**32. Get an I.O.U. for everything you do.**
Never give free value without a reciprocal commitment.
→ *Apply to:* "send over the proposal/audit" requests → trade for a scheduled call to walk through it.

**33. On your way to the bank, keep one eye over your shoulder.**
Watch for post-close cancellation signals; follow up proactively.
→ *Apply to:* post-close comms.

### Part Three: Course-Correct

**34. Work smart, not hard.**
→ Automate/systemize. Resonates with the repo's Clay/trigger approach.

**35. If your competition does it, stop doing it right away.** ⭐
Generic copy = drowned in the mass. If your SMS template could be sent by any agency, rewrite.
→ *Apply to:* every draft. QA question: "Could a competitor paste their logo on this and send it? If yes, the UM is too weak." Pairs with the UM requirement in [sops/sms_guidelines.md](../sops/sms_guidelines.md).

**36. Only decision makers can get others to make decisions.**
→ *Apply to:* targeting. Avoid champion-only outreach when the champion has no buying authority.

**37. All prospects lie, all the time.** ⭐
Not maliciously — they tell you what seems safe/easy. Verify.
→ *Apply to:* discovery + reply parsing. Treat "we're looking at this Q2" as a signal to investigate, not a commitment. Ask "what would have to be true in Q2 for this to move?"

**38. The problem the prospect brings you is never the real problem.** ⭐
Stated pain is a symptom. Real pain is 1–2 layers deeper.
→ *Apply to:* VOC research (the deepsearch skill) and SMS. "We need more leads" → real: unpredictable revenue → real: can't hire/invest/plan. Write to the deeper layer. This is the #1 rule for upgrading pain-aware SMS from generic to surgical.

**39. When all else fails, become a consultant.**
Drop the sales role; help solve the problem honestly.
→ *Apply to:* stalled deals and long-tail nurture.

**40. Fake it 'til you make it.**
Act the role until behaviors become natural. (Confidence is a behavior.)
→ Agency internal.

**41. There are no bad prospects — only bad salespeople.**
Usually about process/fit mismatch, not prospect quality.
→ *Apply to:* internal review. Before blaming list quality, audit the mechanism + messaging fit.

**42. A winner has alternatives, a loser puts all his eggs in one basket.**
→ *Apply to:* [rules/core_principles.md](../rules/core_principles.md) Principle 5 (test multiple segments). Also: never let one big deal anchor the quarter.

**43. You don't learn how to win by getting a "yes" — you learn by getting a "no."** ⭐
No's sharpen the process. Yeses hide the flaws.
→ *Apply to:* post-campaign reviews. Interrogate the No's and ghost's more than the Yes's.

**44. When your foot hurts, you're probably standing on your own toe.**
Most repeating sales problems are self-inflicted (behavior/process), not external.
→ Internal.

**45. Express your feelings through third-party stories.** ⭐
"One of our clients was in the same spot — they told me they felt X…" defuses resistance.
→ *Apply to:* sales scripts, long-form email, call-back replies. Safer than saying "you probably feel X."

**46. There is no such thing as a good try.**
Either you hit the behavior/outcome or you didn't. "Almost" doesn't count as a data point — it distorts the funnel.
→ *Apply to:* metrics discipline.

**47. Selling is a broadway play performed by a psychiatrist.** ⭐
The salesperson's job is to direct an emotional scene while diagnosing underneath. Structure + empathy.
→ *Apply to:* voice in copy. Structured formula underneath, natural human language on top. Pairs with the "read it aloud" QA in [sops/sms_guidelines.md](../sops/sms_guidelines.md).

**48. A life without risk is a life without growth.**
→ Internal.

**49. Leave your child in the car.**
Don't bring YOUR emotional Child (your need for approval, your fear of rejection) into the call — it leaks through and costs deals.
→ *Apply to:* copy voice. Neediness ("would love the chance to…", "hoping we can…", over-apology) = your Child leaking. Strip it.

---

## 🎯 Priority Rules for This Repo's Work

If you (the AI) only remember 10 rules while editing copy in this repo:

1. **#38** — Write to the real pain, not the stated pain.
2. **#2** — Don't dump everything in the SMS.
3. **#5** — Don't preempt objections in cold touches.
4. **#8** — Sell the next step, not the service.
5. **#27** — Make them discover it; don't assert it.
6. **#4** — Give explicit permission to say No in CTAs.
7. **#35** — If a competitor could send this message, rewrite.
8. **#21** — Cut "did you know…" stat-openers.
9. **#47** — Structured inside, human outside.
10. **#49** — Strip neediness/approval-seeking from voice.

---

## 🔌 Where to Plug This Into the Existing Playbook

| Existing file | How Sandler augments it |
|---|---|
| [rules/core_principles.md](../rules/core_principles.md) | Add Child/Parent/Adult model as Principle 6 (copy psychology layer). |
| [rules/anti_patterns_and_mistakes.md](../rules/anti_patterns_and_mistakes.md) | Add: candy-spilling, unasked-question answering, hard-sell, neediness, stating-not-discovering, generic-pain (Rule 35/38). |
| [rules/copy_and_prompt_guidelines.md](../rules/copy_and_prompt_guidelines.md) | Add voice rules: no "you're probably wondering…", no pre-empted objections, no adjective-stacking (Rule 18). |
| [sops/sms_guidelines.md](../sops/sms_guidelines.md) QA checklist | Add 4 checks: (a) Would a competitor's logo fit? (Rule 35) (b) Is this addressing stated pain or real pain? (Rule 38) (c) Does the CTA give permission to say No? (Rule 4) (d) Any preempted objections to strip? (Rule 5) |
| [frameworks/sms_frameworks.md](../frameworks/sms_frameworks.md) | Annotate each framework with which ego state each line fires (Child/Adult/Parent). Add Framework variant using negative-reverse (Rule 16) for lukewarm re-engagement. |
| [frameworks/value_prop_frameworks.md](../frameworks/value_prop_frameworks.md) | Use Rule 38 to force value props one layer deeper than stated pain. |
| [frameworks/email_templates.md](../frameworks/email_templates.md) | Apply Rule 2 (one idea per email) and Rule 45 (third-party stories) for warmup sequences. |
| [skills/ICP-skills-deepsearch-engine/02_pain_points_and_consequences.md](./ICP-skills-deepsearch-engine/02_pain_points_and_consequences.md) | Use Rule 38 as a research directive: always push stated pain to 2nd-order consequence ("can't plan," "can't hire," "founder can't take vacation"). |
| [skills/ICP-skills-deepsearch-engine/05_objections_and_triggers.md](./ICP-skills-deepsearch-engine/05_objections_and_triggers.md) | Rule 28 (fall back / reflect) + Rule 5 (don't preempt in cold) shape where objections are surfaced vs. handled. |
| [skills/copies/sms-skills.md](./copies/sms-skills.md) | Load this file as context BEFORE drafting, and validate each output against the Priority-10. |
| Sales-call scripts (any future SOP) | Rules 3, 6, 12, 14, 22, 23, 25, 28, 31, 45 are the spine of a Sandler-style discovery call. |

---

## 🛠 How an AI Agent Should Use This File

When asked to **generate** SMS / email / scripts:
1. Load the Core Mental Model + Priority-10.
2. Draft using the framework from [frameworks/sms_frameworks.md](../frameworks/sms_frameworks.md).
3. Run the draft through Priority-10 as a QA gate.
4. Report which rules were applied and why (one line each).

When asked to **refine / tweak** existing copy:
1. Identify which Sandler rule(s) the current draft violates (usually 2, 5, 35, 38, or 49).
2. Rewrite only the violating lines — do not restructure unnecessarily.
3. Name the rule applied in the change note.

When asked to **review** a campaign that underperformed:
1. Rule 43 framing — interrogate No's/ghosts first.
2. Check Rule 38 (were we solving stated vs. real pain?).
3. Check Rule 35 (was the UM differentiated?).
4. Check Rule 8 (was the CTA selling the call or the service?).

---

*Last updated: 2026-04-21*
*Source: The Sandler Rules, David Mattson / David H. Sandler, © 2009 Sandler Systems, Inc.*
