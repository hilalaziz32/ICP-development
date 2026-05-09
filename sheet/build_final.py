"""Build the enriched CSV with transcript + categorization columns."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = json.load(open(ROOT / "transcripts_index.json"))

# Per-row analysis (1-indexed by row in rec.csv).
# For rows whose transcript fetch failed, only metadata is filled.
ANALYSIS = {
    1: {
        "category": "Discovery/Strategy Call",
        "one_liner": "Phoenix Energy explores Kynship's full-service Meta+Google management to scale DTC alongside retail expansion to 15 states.",
        "angle": "Holistic ecommerce growth tied to retail credibility; cost-control bidding + influencer-fueled creative volume.",
        "sub_categories": ["Meta ads", "Google ads", "Influencer seeding", "Retail expansion", "Cost control bidding"],
        "specialty": "DTC Energy Drink / Beverage",
        "pain_point": "Needs ad management + creative volume to scale post-launch DTC and feed retail credibility.",
    },
    2: {
        "category": "Discovery/Pitch Call",
        "one_liner": "Brand director evaluating Kynship for an August brand launch; wants startup-experienced, data-driven growth partner.",
        "angle": "Startup launch partner with proven scale case studies (Create $2M/6mo, Amol's $13.5M/18mo).",
        "sub_categories": ["Brand launch", "Meta ads", "TikTok", "Google ads", "Influencer seeding", "Unit economics"],
        "specialty": "DTC Nutrition (pre-launch startup)",
        "pain_point": "New brand needs proven launch playbook; needs proposal + case studies to evaluate fit.",
    },
    3: {
        "category": "Discovery/Strategy Call",
        "one_liner": "Fishkin scaling $2M→$5M and launching Slumber with $30K/mo paid; needs CAC plan in competitive wellness market.",
        "angle": "Cut CAC by 50% via bundling, paid efficiency, and influencer creative integration.",
        "sub_categories": ["CAC reduction", "Product launch", "Meta ads", "AOV / bundling", "Forecasting"],
        "specialty": "DTC Wellness / Sleep",
        "pain_point": "Projected CAC $100–168 in competitive wellness threatens profitability of Slumber launch.",
    },
    4: {
        "category": "Discovery → Audit",
        "one_liner": "$7M paid-media brand frustrated with current agency's creativity + cost control; planning Kynship audit by early Dec.",
        "angle": "Cross-channel ecosystem (Meta+Google+Amazon+TikTok) with high-volume creative + UGC.",
        "sub_categories": ["Meta ads", "Google ads", "Amazon", "TikTok", "Creative volume", "Audit"],
        "specialty": "DTC Food / BBQ",
        "pain_point": "Current agency lacks creativity and cost control; tariffs eroding YoY growth (~$1M impact).",
    },
    5: {
        "category": "Discovery/Strategy Call",
        "one_liner": "Burst (post-Applovin breakout) explores Meta audit + influencer seeding after losing agency before BFCM.",
        "angle": "Seeding program at scale (500 influencers, 150 paid + 60–90 organic posts/mo) and Meta efficiency vs Applovin reliance.",
        "sub_categories": ["Influencer seeding", "Meta ads", "Applovin", "Channel diversification", "Audit"],
        "specialty": "DTC CPG / Snack",
        "pain_point": "90% reliance on Applovin; Meta high-CAC + unprofitable; just lost agency 2 weeks before Black Friday.",
    },
    6: {
        "category": "Partnership/Referral",
        "one_liner": "Seth Barnes (advisor) explores ongoing referral + fractional-growth relationship with Kynship for early-stage brands.",
        "angle": "Lead/referral exchange — Seth sends Kynship-fit brands; receives early-stage deal flow that's not Kynship-fit.",
        "sub_categories": ["Referral partnership", "Fractional head of growth", "Agency-to-advisor", "LinkedIn outreach"],
        "specialty": "Agency-to-Advisor partnership",
        "pain_point": "Early-stage brands aren't Kynship-fit; need referral network for sub-$1M ARR brands.",
    },
    7: {
        "category": "Discovery → Pause/Decline",
        "one_liner": "Cuts Clothing pauses partnership — they run a segmented model (creative-only via boutique) that doesn't fit Kynship's integrated approach.",
        "angle": "Creative scaling for influencer content (the one gap they have).",
        "sub_categories": ["Creative scaling", "Influencer content", "Cost caps", "Pause/Decline"],
        "specialty": "DTC Apparel",
        "pain_point": "Struggles to scale influencer content; current agency structure is segmented, not integrated.",
    },
    8: {
        "category": "Discovery/Strategy Call",
        "one_liner": "Pre-launch Banuskin (Sephora Accelerate) evaluating Kynship for launch + fractional BDR; targeting $150K in 6 months.",
        "angle": "Early-stage beauty launch partner with creative + media buying + 250-ad volume + landing-page conversion.",
        "sub_categories": ["Beauty / Sephora", "Meta ads", "Creative production", "Landing pages", "Fractional BDR"],
        "specialty": "DTC Beauty / Skincare (pre-launch)",
        "pain_point": "Currently 0.6 ROAS at $6K/wk Meta spend; needs path to 1.5–2.0 break-even.",
    },
    9: {
        "category": "Discovery → Audit",
        "one_liner": "UK period-care brand at £6.7M targeting £8.5M; CAC up to £25–30, only 10% of UGC performs; planning audit.",
        "angle": "Blended attribution (MER) + creative efficiency on top of paid-driven 60–70% revenue.",
        "sub_categories": ["CAC reduction", "Creative efficiency", "MER / blended attribution", "UK market", "Audit"],
        "specialty": "DTC Period care (UK)",
        "pain_point": "CAC rising to £25–30; only 10% of UGC content performs — major creative inefficiency.",
    },
    11: {
        "category": "Discovery → Audit",
        "one_liner": "365 Holdings preparing GM hire + Kynship audit to return Brian Anthony's brand to a $10M run rate.",
        "angle": "Forecasting + reverse-engineering ad spend from revenue goals; bi-weekly cadence.",
        "sub_categories": ["Forecasting", "P&L-tied media", "GM hire", "Multi-brand", "Audit"],
        "specialty": "Multi-brand DTC holding co",
        "pain_point": "Revenue decay $10M → $7–8M; current forecasting unsophisticated; needs GM + agency together.",
    },
    12: {
        "category": "Discovery/Strategy Call",
        "one_liner": "XeroShoes (70 SKUs) wants better media buyer; previous vendor wasted budget on top-of-funnel without attribution.",
        "angle": "Attribution-accurate Shopify-first media buying with CPA cost controls for complex SKU portfolio.",
        "sub_categories": ["Attribution", "CPA cost controls", "Amazon transparency", "Repeat-customer cohorts", "Footwear"],
        "specialty": "DTC Footwear",
        "pain_point": "70 styles complicate targeting; prior vendor wasted budget; Amazon reseller (Orva) blocks data visibility.",
    },
    13: {
        "category": "Internal Sales Coaching",
        "one_liner": "Tumblerware founder Manuel coaches Tom on cold-calling, DTC profitability, and customer-centric strategy — not a client pitch.",
        "angle": "Sales/strategy mentorship for Tom; Tumblerware itself does NOT outsource media buying.",
        "sub_categories": ["Sales coaching", "Cold calling", "DTC profitability insights", "Internal"],
        "specialty": "Internal / Sales coaching",
        "pain_point": "Tom needs sharper cold-call playbook + insight on what makes DTC brands ready for an agency.",
    },
    14: {
        "category": "Discovery → Audit",
        "one_liner": "UK supplements brand wants to scale paid social (33% of £2–2.7M Q spend), 20% UK / 35% Germany growth target.",
        "angle": "Paid-social scaling + creative velocity (170 → 300+ assets in 6 weeks) on CPA goals.",
        "sub_categories": ["Paid social", "CPA goals", "Creative velocity", "Magento → Shopify", "Audit"],
        "specialty": "DTC Supplements (UK + DE)",
        "pain_point": "Paid social underused; Magento limits customer data; Amazon Vendor Central restricts insight.",
    },
    15: {
        "category": "Re-engagement (too early)",
        "one_liner": "£30K/mo brand too early for $15K/mo retainer; Tom to revisit in 3–6 months as revenue approaches $50K/mo.",
        "angle": "Future-fit; provide creative/ad-account resources now, partner later.",
        "sub_categories": ["Re-engagement", "Brand growth", "CAC", "Pet / Outdoor"],
        "specialty": "DTC Pet / Outdoor (early-stage)",
        "pain_point": "Stock shortages limit growth; revenue not yet sufficient for agency retainer.",
    },
    17: {
        "category": "Discovery → Audit (existing relationship expansion)",
        "one_liner": "365 Holdings expands audit scope to Cuddle Clones ($28M targeting $38–48M); Facebook declining.",
        "angle": "Channel diversification (Applovin/Google/Snap/Pin) + 700 creatives/month + better forecasting.",
        "sub_categories": ["Channel diversification", "Creative volume", "Forecasting", "Multi-brand", "Audit"],
        "specialty": "Multi-brand DTC / Pet (Cuddle Clones)",
        "pain_point": "Facebook performance declining; in-house media lacks strategic leadership; weak forecasting.",
    },
    18: {
        "category": "Partnership/Referral + Discovery (Barko)",
        "one_liner": "Cal Nutri (CPG accelerator) explores Kynship for Barko relaunch + portfolio of accelerator brands.",
        "angle": "Accelerator portfolio referral + Barko CAC fix tied to packaging/SKU relaunch.",
        "sub_categories": ["CPG accelerator", "Portfolio partnership", "CAC", "Product relaunch", "Pet wellness"],
        "specialty": "CPG / Pet wellness + Accelerator partnership",
        "pain_point": "Barko CAC ~$40–45 ≈ product price — campaigns paused, needs efficiency before relaunch.",
    },
    20: {
        "category": "Discovery → Audit",
        "one_liner": "Lawless (post-CEO transition) plans Q1 2026 agency switch with CPA-aligned media + media-mix modeling.",
        "angle": "Performance marketing aligned with financial goals; integrating D2C + Amazon + retail.",
        "sub_categories": ["Media mix modeling", "Performance marketing", "Agency transition", "UGC creative", "Audit"],
        "specialty": "DTC Beauty / Cosmetics",
        "pain_point": "CEO departure → needs CPA-aligned partner; segmented sales channels need unified analysis.",
    },
    22: {
        "category": "Discovery → Audit",
        "one_liner": "$100M holding co (9 brands) outsourcing Hey Nutrition UK due to capacity + UK supplement ad restrictions.",
        "angle": "Multi-brand outsourcing tied to rebrand + UK paid-search complications.",
        "sub_categories": ["UK supplements", "Multi-brand", "Forecasting", "Audit", "Rebrand"]
        ,
        "specialty": "Holding co / UK supplements",
        "pain_point": "Marketing manpower can't keep up post-COVID growth; UK supplement ad restrictions force outsourcing.",
    },
    23: {
        "category": "Discovery → Audit (agency replacement)",
        "one_liner": "Pott'd auditing $50K/mo current agency for value; planning Kynship audit + cost-controlled media.",
        "angle": "Replace existing agency with cost-controlled, profit-aligned media + 100–150 creative assets/batch.",
        "sub_categories": ["Cost controls", "Creative volume", "Forecasting", "Agency replacement", "Audit"],
        "specialty": "DTC Beauty / Skincare",
        "pain_point": "Paying $50K/mo to current agency without proportional value; needs efficiency assessment.",
    },
    24: {
        "category": "Discovery → Audit (agency replacement)",
        "one_liner": "Hello Jupiter ($10.8M → $20M target) replacing slow current agency; D2C share to grow from 22% → 33%.",
        "angle": "Influencer-led creative (500+ micro) + forecast deck for SALT meeting.",
        "sub_categories": ["DTC scaling", "Influencer creative", "Cost per lead", "Agency replacement", "Audit"],
        "specialty": "DTC Lead-gen / Subscription",
        "pain_point": "Current agency slow + creative quality poor; ROAS climbed 0.85 → 1.85 too slowly; $200 CPL.",
    },
    25: {
        "category": "Re-engagement / Backup positioning",
        "one_liner": "Yasmin keeps Kinship as a backup option; will discuss with Kyle for future engagement.",
        "angle": "Stay top-of-mind as financially transparent backup if current agency falters.",
        "sub_categories": ["Re-engagement", "Backup positioning", "Financial transparency"],
        "specialty": "DTC (vertical unspecified)",
        "pain_point": "Current arrangement is OK; Yasmin wants alternatives lined up in case of pivot.",
    },
    26: {
        "category": "Re-engagement (pre-funding)",
        "one_liner": "Glassette pivot + new skincare brand pre-launching in 102 Boots stores in May; future paid-media partner.",
        "angle": "Long-term skincare-brand + retail (Boots) play; revisit when funded/scaled.",
        "sub_categories": ["Skincare launch", "Retail (Boots)", "Re-engagement", "UGC + influencer"],
        "specialty": "Beauty / Skincare + Digital publishing",
        "pain_point": "Pre-funding/pre-revenue for skincare brand; not yet at scale for paid-media retainer.",
    },
    27: {
        "category": "Partnership/Referral",
        "one_liner": "Cal Nutri + Kinship align on accelerator referral, Vita Foods Expo, and joint brand-launch opportunities.",
        "angle": "Two-way referral + EU-brand expansion via Vita Foods Expo.",
        "sub_categories": ["Referral partnership", "CPG accelerator", "Cost optimization", "Trade show", "EU expansion"],
        "specialty": "CPG accelerator partnership",
        "pain_point": "Need joint pipeline; CPG ops + marketing alignment for accelerator brands.",
    },
    28: {
        "category": "Discovery → Audit",
        "one_liner": "WOW + Big Mouth ($40M) targeting $80M in 4–5 years; Kynship audit scheduled April 24.",
        "angle": "4-part creative strategy (IGC + UGC + AI + traditional) + multi-brand audit.",
        "sub_categories": ["Multi-brand", "Creative strategy (IGC/UGC/AI)", "DTC scaling", "Cost control", "Audit"],
        "specialty": "Personal care / Toys (multi-brand)",
        "pain_point": "Heavily seasonal ad spend (April–Aug); Big Mouth DTC underdeveloped (<5% of revenue).",
    },
    29: {
        "category": "Discovery → Audit",
        "one_liner": "Cuddle Clones finalizing agency by Memorial Day; need creative authenticity + fill internal strategy gap.",
        "angle": "Creative authenticity + bi-weekly strategic partner replacing vacant internal strategy role.",
        "sub_categories": ["Creative strategy", "Strategic leadership", "Bi-weekly cadence", "Pet", "Audit"],
        "specialty": "DTC Pet (custom)",
        "pain_point": "Internal strategy vacancy; needs differentiation + comprehensive multi-platform data audit.",
    },
    31: {
        "category": "Discovery (early-stage / referral-out likely)",
        "one_liner": "$30K/mo cortisol-sleep supplement brand wants to grow to $200K/mo; Tom may refer to a smaller firm.",
        "angle": "Cost-cap shift + influencer outreach (400–500/mo) + financial modeling spreadsheet.",
        "sub_categories": ["Sleep / CPG supplement", "Cost caps", "Influencer outreach", "Financial modeling", "Referral-out"],
        "specialty": "DTC Supplements / Sleep",
        "pain_point": "Sub-scale for Kynship retainer; needs financial modeling + smaller-firm fit.",
    },
}

# Build rows from the original CSV.
src_rows = []
with open(ROOT / "rec.csv") as f:
    for line in f:
        parts = [p.strip() for p in line.rstrip("\n").split("\t") if p.strip()]
        if len(parts) < 4:
            continue
        company, date, ctype, url = parts[0], parts[1], parts[2], parts[3]
        notes = parts[4] if len(parts) > 4 else ""
        src_rows.append({"company": company, "date": date, "call_type": ctype, "url": url, "notes": notes})

OUT = ROOT / "rec_enriched.csv"
fieldnames = [
    "row_id", "company", "date", "call_type", "fireflies_url", "notes",
    "transcript_id", "transcript_status", "category", "one_liner", "angle",
    "sub_categories", "specialty", "pain_point", "transcript_md",
]

with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    w.writeheader()
    for i, src in enumerate(src_rows, 1):
        meta = idx[i - 1]
        a = ANALYSIS.get(i, {})
        transcript_md = ""
        if meta["status"] == "ok":
            transcript_md = (ROOT / meta["file"]).read_text()
        status = "ok" if meta["status"] == "ok" else "no_access (workspace permission / not found)"
        w.writerow({
            "row_id": i,
            "company": src["company"],
            "date": src["date"],
            "call_type": src["call_type"],
            "fireflies_url": src["url"],
            "notes": src["notes"],
            "transcript_id": meta["transcript_id"],
            "transcript_status": status,
            "category": a.get("category", ""),
            "one_liner": a.get("one_liner", "[Transcript not accessible — categorization skipped]" if meta["status"] != "ok" else ""),
            "angle": a.get("angle", ""),
            "sub_categories": json.dumps(a.get("sub_categories", [])),
            "specialty": a.get("specialty", ""),
            "pain_point": a.get("pain_point", ""),
            "transcript_md": transcript_md,
        })

print(f"Wrote {OUT}")
print(f"Rows: {len(src_rows)} | with transcript: {sum(1 for r in idx if r['status']=='ok')}")
