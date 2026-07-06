#!/usr/bin/env python3
"""
sms_qa.py — deterministic QA for cold-SMS drafts (Layer C / sms-draft skill).

Runs the MECHANICAL half of the SMS preview check so the skill can self-report
before the human eyeballs the draft in the visual preview tool. It does NOT
judge naturalness — that is the human's gate.

Checks per text:
  - character count
  - SMS segment count (GSM-7: 160 single / 153 concatenated; Unicode: 70 / 67)
  - number-density (how many distinct numeric tokens — too many reads messy).
    Timeframes ("in 3 months", "in 4 years") are LOAD-BEARING and are excluded
    from the density count — never cut the timeframe to thin out numbers.
  - bulk warning (over a soft length ceiling)
  - absolute-claim flag ("ever", "single", "entire", "never" — usually overclaim)
  - SUPERLATIVE flag ("biggest in their history", "best month ever", "record …" —
    AI brag-flourishes a real person texting wouldn't say)
  - STATEMENT-LEAD flag (a T2 that asserts what the category does — "… brands are
    still …" — instead of speaking TO the prospect; the QA Q10 crime)
  - GENERIC-RELEVANCE flag (rung-0 tells: "could do the same for {{company}}", etc.)
  - RUNG-0 RISK flag (a T2 personalized only on {{company}}/{{first_name}} — no niche/
    signal hook; reacting to the case instead of speaking to their world)
  - BANLIST flag ("no X, no Y", "it's not just X", %/decimals — instant AI tells)

These are all WARNINGS, not auto-fails — they force a conscious check; the human /
model QA gate (qa-checklist.md) makes the final call so creativity survives.

Across the texts passed together (e.g. all the T2s of a batch):
  - REPEATED-CTA flag (the same soft CTA reused across variants — the "could I
    show u how? x15" sameness tell). Pass every variant's T2 in one call to scan.

Usage:
  python3 sms_qa.py "Text 1 here" "Text 2 here"
  python3 sms_qa.py "v1 T2" "v2 T2" "v3 T2"        # scan a batch for CTA sameness
  echo "Text 1 here" | python3 sms_qa.py            # one text via stdin
  python3 sms_qa.py --json "Text 1" "Text 2"        # machine-readable

No third-party dependencies.
"""

import sys
import re
import json

# --- tunable thresholds -------------------------------------------------------
SOFT_CHAR_CEILING = 160      # over this, Text 1 starts to feel bulky on a phone
NUMBER_DENSITY_FLAG = 2      # more than this many numeric tokens in one text = messy
ABSOLUTE_WORDS = ("ever", "single", "entire", "never", "always", "guaranteed")

# Rung-0 / generic-relevance tells (see relevance-engine.md). These are WARNINGS,
# not auto-fails — the QA gate decides (S-tier case studies may ship at rung 0).
GENERIC_RELEVANCE_PATTERNS = (
    (r"\bdo the same for\b", "(could) do the same for …"),
    (r"\bhad a few ideas for\b", "had a few ideas for …"),
    (r"\bideas in mind for\b", "ideas in mind for …"),
    (r"\bsame\b.{1,25}\bspace as\b", "same <X> space as …"),
)

# Core merge slots that give UNIQUENESS but not RELEVANCE (enrichment-menu.md). A T2
# whose only personalization is these is leaning on company-merge — rung 0 unless the
# case is S-tier. (A line with no slots may still be aimed via 2nd-person "your …", so
# we only flag when slots are PRESENT and all of them are core.) WARNING — Q4 decides.
CORE_SLOTS = {"company", "first_name", "firstname", "name", "fname"}

# Voice-Profile banlist items a script can match deterministically (see
# Cold-SMS-Voice-Profile-Scaletopia.md). WARNINGS — kill on the human gate.
BANLIST_PATTERNS = (
    (r"\bno\s+[\w']+,\s+no\s+[\w']+", "the 'no X, no Y' tell (reads instantly as AI)"),
    (r"\bnot just\b", "the 'it's not just X — it's Y' construction"),
    (r"\d\s?%", "a percentage — winners use absolute numbers, not %"),
    (r"\d+\.\d+", "a decimal — round it (winners use whole numbers)"),
)

# A timeframe is the load-bearing third leg of proof (number + unit + TIMEFRAME, see
# qa-checklist Q3). It must NOT be cut to satisfy number-density — so it's excluded
# from the density count and called out if present.
TIMEFRAME_RE = re.compile(
    r"\b\d+\s?(?:day|days|week|weeks|month|months|mo|year|years|yr|yrs)\b", re.I
)

# Brag-superlatives / AI flourishes — the "biggest in their history" tell. A closer on
# a call states the number; the flourish is what reads as AI. WARNINGS.
SUPERLATIVE_PATTERNS = (
    (r"\bin (?:their|its|the brand'?s?|the company'?s?|company'?s?|brand'?s?) history\b",
     "'in their history' — brag-flourish, reads AI (state the number, drop the flourish)"),
    (r"\b(?:biggest|best|largest|highest|fastest|greatest|strongest)\b[^.?!]{0,30}?\b(?:ever|of all time|on record|in history)\b",
     "a 'biggest/best … ever' superlative — AI brag-flourish"),
    (r"\bof all time\b", "'of all time' — brag-flourish"),
    (r"\brecord[- ](?:breaking|month|quarter|year|setting|high)\b", "a 'record-…' flourish"),
)

# STATEMENT-LEAD: a T2 that asserts what the category/market DOES ("… brands are still
# …", "… companies keep …") instead of speaking TO the prospect. The Q10 crime. NOTE
# the line: a first-person observation ("haven't seen many brands do this") is FINE —
# the tell is the category noun as the SUBJECT of a market-state verb. Low-false-
# positive on purpose; the model gate (Q10) catches the subtler ones.
STATEMENT_LEAD_RE = re.compile(
    r"\b(?:brands|companies|founders|teams|firms|businesses|stores|agencies|sellers)\s+"
    r"(?:are|is|keep|keeps|still|can'?t|cannot|won'?t|aren'?t|isn'?t|tend|struggle|rely|love|hate)\b",
    re.I,
)


# GSM-7 basic character set (chars that DON'T force Unicode encoding).
GSM7 = set(
    "@£$¥èéùìòÇØøÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?"
    "¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà"
    "\n\r"
)
GSM7_EXT = set("^{}\\[~]|€")  # these count as 2 GSM-7 chars each


def is_gsm7(text: str) -> bool:
    return all((c in GSM7) or (c in GSM7_EXT) for c in text)


def gsm7_length(text: str) -> int:
    return sum(2 if c in GSM7_EXT else 1 for c in text)


def segments(text: str):
    """Return (encoding, units, segment_count)."""
    if is_gsm7(text):
        units = gsm7_length(text)
        single, multi = 160, 153
        enc = "GSM-7"
    else:
        units = len(text)
        single, multi = 70, 67
        enc = "Unicode"
    if units <= single:
        seg = 1
    else:
        seg = -(-units // multi)  # ceil division
    return enc, units, seg


def numeric_tokens(text: str):
    # Matches $8m, 85m, 100k, $1m/month, 3, 40%, 1,000, 160 etc.
    return re.findall(r"\$?\d[\d,\.]*\s?(?:[kKmMbB%]|/mo(?:nth)?)?", text)


def timeframe_tokens(text: str):
    return TIMEFRAME_RE.findall(text)


def content_numeric_tokens(text: str):
    """Numbers that count toward density — i.e. excluding the load-bearing timeframe
    (a timeframe is never the thing to cut; see qa-checklist Q3)."""
    stripped = TIMEFRAME_RE.sub(" ", text)
    return numeric_tokens(stripped)


def superlative_flags(text: str):
    low = text.lower()
    return [label for pat, label in SUPERLATIVE_PATTERNS if re.search(pat, low)]


def statement_lead_flag(text: str):
    return bool(STATEMENT_LEAD_RE.search(text))


def company_only_relevance(text: str):
    """True if the text HAS merge slots and every one is a core (uniqueness-only) slot —
    i.e. it personalizes only on {{company}}/{{first_name}}, no niche/account/signal hook.
    That's rung-0 relevance unless the case is S-tier (see relevance-engine.md §4)."""
    slots = re.findall(r"\{\{(.*?)\}\}", text)
    if not slots:
        return False  # no slots → may be aimed via 2nd-person "your …"; not our call
    return all(s.strip().lower() in CORE_SLOTS for s in slots)


def absolute_flags(text: str):
    low = text.lower()
    return [w for w in ABSOLUTE_WORDS if re.search(r"\b" + re.escape(w) + r"\b", low)]


def generic_relevance_flags(text: str):
    low = text.lower()
    return [label for pat, label in GENERIC_RELEVANCE_PATTERNS if re.search(pat, low)]


def banlist_flags(text: str):
    low = text.lower()
    return [label for pat, label in BANLIST_PATTERNS if re.search(pat, low)]


def normalize(text: str) -> str:
    """Lowercase, blank out merge slots so {{company}}/[company] don't break matching."""
    t = text.lower()
    t = re.sub(r"\{\{.*?\}\}", "X", t)
    t = re.sub(r"\[.*?\]", "X", t)
    return re.sub(r"\s+", " ", t).strip()


def cta_of(text: str) -> str:
    """Best-effort extract of the trailing soft-CTA for cross-variant dup detection."""
    norm = normalize(text)
    # split on sentence ends or a ' - ' / dash join; the CTA is the last chunk
    pieces = [p for p in re.split(r"(?<=[.?!])\s+|\s+[-–—]\s+", norm) if p.strip()]
    return pieces[-1].strip(" .?!") if pieces else norm


def analyze(text: str) -> dict:
    text = text.strip()
    enc, units, seg = segments(text)
    nums = numeric_tokens(text)
    flags = []
    if units > SOFT_CHAR_CEILING:
        flags.append(f"BULK: {units} chars (> {SOFT_CHAR_CEILING}) — trim for the phone")
    if seg > 1:
        flags.append(f"MULTI-SEGMENT: {seg} SMS segments — costs more & may split oddly")
    content_nums = content_numeric_tokens(text)
    has_timeframe = bool(timeframe_tokens(text))
    if len(content_nums) > NUMBER_DENSITY_FLAG:
        keep_note = " (keep the timeframe — cut a $/volume number instead)" if has_timeframe else ""
        flags.append(
            f"NUMBER-DENSITY: {len(content_nums)} non-timeframe numbers ({', '.join(content_nums)}) — cut one, reads messy{keep_note}"
        )
    abs_w = absolute_flags(text)
    if abs_w:
        flags.append(f"ABSOLUTE-CLAIM: {', '.join(abs_w)} — defensible on a call? soften or cut")
    for label in superlative_flags(text):
        flags.append(f"SUPERLATIVE: {label}")
    if statement_lead_flag(text):
        flags.append(
            "STATEMENT-LEAD: asserts what the category does (\"… brands are still …\") — make it speak TO them, not about the market (QA Q10)"
        )
    for label in generic_relevance_flags(text):
        flags.append(f"GENERIC-RELEVANCE (rung 0): \"{label}\" — climb a rung (enrichment-menu.md), or S-tier case only")
    if company_only_relevance(text):
        flags.append(
            "RUNG-0 RISK: personalizes only on {{company}}/{{first_name}} — no niche/account/signal hook. Add one (or confirm S-tier); don't trade an aimed line for a generic one (Q4)"
        )
    for label in banlist_flags(text):
        flags.append(f"BANLIST: {label}")
    return {
        "text": text,
        "encoding": enc,
        "chars": units,
        "words": len(text.split()),
        "segments": seg,
        "numbers": nums,
        "cta": cta_of(text),
        "flags": flags,
    }


def repeated_ctas(results):
    """Across all texts passed, flag any soft-CTA reused in 2+ of them (the sameness tell)."""
    counts = {}
    for r in results:
        c = r["cta"]
        if len(c.split()) >= 3:  # ignore trivially-short tails
            counts.setdefault(c, []).append(r["text"])
    return {c: texts for c, texts in counts.items() if len(texts) > 1}


def render(results) -> str:
    out = []
    for i, r in enumerate(results, 1):
        out.append(f"--- Text {i} ---")
        out.append(f'"{r["text"]}"')
        out.append(f"  chars: {r['chars']} ({r['encoding']})   words: {r['words']}   segments: {r['segments']}")
        if r["flags"]:
            for f in r["flags"]:
                out.append(f"  ⚠ {f}")
        else:
            out.append("  ✓ clean (still run the visual preview for naturalness)")
        out.append("")
    dups = repeated_ctas(results)
    if dups:
        out.append("--- Batch ---")
        for cta, texts in dups.items():
            out.append(f"  ⚠ REPEATED-CTA: \"{cta}\" reused across {len(texts)} variants — vary it (variable-schema.md)")
        out.append("")
    return "\n".join(out)


def main():
    args = sys.argv[1:]
    as_json = False
    if "--json" in args:
        as_json = True
        args = [a for a in args if a != "--json"]
    texts = args if args else ([sys.stdin.read()] if not sys.stdin.isatty() else [])
    texts = [t for t in texts if t.strip()]
    if not texts:
        print("usage: python3 sms_qa.py \"Text 1\" [\"Text 2\"]", file=sys.stderr)
        sys.exit(1)
    results = [analyze(t) for t in texts]
    if as_json:
        payload = {"texts": results, "repeated_ctas": repeated_ctas(results)}
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(render(results))


if __name__ == "__main__":
    main()
