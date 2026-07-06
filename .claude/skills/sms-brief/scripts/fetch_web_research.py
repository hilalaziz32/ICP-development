"""
fetch_web_research.py — Tier 3 gap-filling helper.

This script is invoked by Claude (the skill) during Step 5 when Tier 1 + Tier 2
sources are thin for a given field. It returns query strings to run via the
WebSearch and WebFetch tools available in the runtime — Claude executes the
actual searches and collects the results.

WHY THIS IS A SCRIPT INSTEAD OF JUST PROMPTING:
- The query templates from web-search-prompts.md need to be substituted with
  {persona}, {industry}, {tool_category} consistently across runs
- Centralizing query construction here avoids drift across runs
- The script returns structured query manifests Claude can execute via WebSearch

USAGE:
    python fetch_web_research.py --field 4b --persona "VP of Marketing" --industry "DTC supplements" --tool-category "marketing agencies"

OUTPUT (stdout JSON):
    {
        "field": "4b",
        "queries": [
            {
                "query": "site:reddit.com \"cold email\" OR \"cold outreach\" marketing agencies frustrating",
                "type": "reddit_websearch",
                "purpose": "service hidden objections — Reddit cold-outreach reactions"
            },
            ...
        ],
        "instructions": "Run each query via WebSearch. For top 5-10 Reddit threads per query, fetch via WebFetch and extract verbatim objection-shaped statements. Tag each with [source: <url>]."
    }

Claude reads this output and runs the queries via its available WebSearch /
WebFetch tools. The script itself does not make HTTP calls — that's done by
the runtime tooling.
"""

import argparse
import json
import sys


# ============================================================
# Query templates (mirrored from references/web-search-prompts.md)
# ============================================================

QUERIES_BY_FIELD = {
    "4b": {
        "purpose": "service hidden objections — what {persona} thinks when receiving cold outreach from {tool_category}",
        "reddit_queries": [
            'site:reddit.com "cold email" OR "cold outreach" {tool_category} frustrating',
            'site:reddit.com "marketing agency" OR "{tool_category}" red flags',
            'site:reddit.com {persona} "tired of" cold outreach',
            'site:reddit.com "another agency" pitched me',
            'site:reddit.com agency promises empty',
        ],
        "subreddit_queries": {
            "b2b_saas": [
                'site:reddit.com/r/sales {tool_category} cold outreach',
                'site:reddit.com/r/SaaS agency pitched',
            ],
            "dtc_ecom": [
                'site:reddit.com/r/ecommerce agency horror story',
                'site:reddit.com/r/Entrepreneur marketing agency disappeared',
                'site:reddit.com/r/shopify hired agency budget burned',
            ],
        },
    },
    "3": {
        "purpose": "verbatim language quotes from {persona} in {industry}",
        "g2_capterra_queries": [
            'site:g2.com {industry} reviews',
            'site:capterra.com {industry} reviews',
        ],
        "reddit_queries": [
            'site:reddit.com {persona} {industry} "the worst part is" OR "what\'s frustrating"',
            'site:reddit.com {persona} {industry} "I wish" OR "if only"',
        ],
    },
    "4a": {
        "purpose": "industry mistaken beliefs — what {persona} in {industry} commonly believes wrongly",
        "reddit_queries": [
            'site:reddit.com {industry} "is SEO dead" OR "is X dead"',
            'site:reddit.com {industry} "AI replacing"',
        ],
        "linkedin_queries": [
            'site:linkedin.com/pulse {industry} myth OR misconception',
        ],
        "general_queries": [
            '{industry} "common myth" OR "biggest misconception"',
            '{industry} "I used to think" agency OR marketing',
        ],
    },
    "5": {
        "purpose": "dream outcome statements from {persona} in {industry} (Tier 3 fallback only)",
        "linkedin_queries": [
            'site:linkedin.com/posts {persona} {industry} "my goal" OR "this quarter"',
            'site:linkedin.com/pulse {persona} "what success looks like"',
        ],
        "reddit_queries": [
            'site:reddit.com {persona} {industry} "if I could just"',
            'site:reddit.com {persona} {industry} "what I really want"',
        ],
    },
}


SUBREDDIT_CATEGORIES = {
    "b2b_saas": ["b2b saas", "saas", "b2b tech", "software"],
    "dtc_ecom": ["dtc", "ecommerce", "ecom", "d2c", "shopify", "supplements", "beauty", "apparel"],
}


def _categorize_industry(industry: str) -> str:
    """Map a free-text industry string to a subreddit category."""
    industry_lower = industry.lower()
    for category, keywords in SUBREDDIT_CATEGORIES.items():
        if any(kw in industry_lower for kw in keywords):
            return category
    return "general"


def build_query_manifest(field: str, persona: str, industry: str, tool_category: str) -> dict:
    if field not in QUERIES_BY_FIELD:
        return {
            "error": f"Unknown field '{field}'. Supported: {list(QUERIES_BY_FIELD.keys())}",
        }

    spec = QUERIES_BY_FIELD[field]
    industry_category = _categorize_industry(industry)

    queries = []

    # Reddit queries (always include)
    for q in spec.get("reddit_queries", []):
        queries.append({
            "query": q.format(persona=persona, industry=industry, tool_category=tool_category),
            "type": "reddit_websearch",
            "purpose": spec["purpose"],
        })

    # Subreddit-specific queries (only if we match a category)
    subreddit_specific = spec.get("subreddit_queries", {}).get(industry_category, [])
    for q in subreddit_specific:
        queries.append({
            "query": q.format(persona=persona, industry=industry, tool_category=tool_category),
            "type": "reddit_websearch_subreddit_specific",
            "purpose": f"{spec['purpose']} — {industry_category}-specific subreddits",
        })

    # Other query types per field
    for query_key in ["g2_capterra_queries", "linkedin_queries", "general_queries"]:
        for q in spec.get(query_key, []):
            queries.append({
                "query": q.format(persona=persona, industry=industry, tool_category=tool_category),
                "type": query_key,
                "purpose": spec["purpose"],
            })

    return {
        "field": field,
        "persona": persona,
        "industry": industry,
        "tool_category": tool_category,
        "industry_category_detected": industry_category,
        "queries": queries,
        "instructions": (
            "Run each query via WebSearch. For each query, scan results for relevant threads. "
            "For the top 3-5 highest-signal results per query, use WebFetch to read the thread. "
            "Extract verbatim statements that match the field's purpose. Each extraction must be "
            "tagged with [source: <url>]. Drop low-signal results (vendor blogs, listicles, AI-generated content)."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description="Build a web research query manifest for a brief field.")
    parser.add_argument("--field", required=True, help="Brief field to gap-fill (e.g., '4b', '3', '4a', '5')")
    parser.add_argument("--persona", required=True, help="Target persona (e.g., 'VP of Marketing')")
    parser.add_argument("--industry", required=True, help="Target industry (e.g., 'DTC supplements')")
    parser.add_argument("--tool-category", default="marketing agencies",
                        help="Category of service being pitched (default: 'marketing agencies')")
    args = parser.parse_args()

    manifest = build_query_manifest(args.field, args.persona, args.industry, args.tool_category)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
