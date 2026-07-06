"""
score_pain_points.py — Cluster and score pain-point extractions (also language
quotes and service hidden objections) from multiple sources.

Input: a JSON list of extractions, each tagged with source tier.
Output: a ranked, deduped, scored list.

USAGE:
    python score_pain_points.py --input extractions.json --output ranked.json

INPUT FORMAT (extractions.json):
    [
        {
            "text": "CaC is creeping up",
            "source": "transcript-005.docx, ~14:20",
            "tier": 1,
            "kind": "pain"   // "pain", "language_quote", "objection_4b"
        },
        {
            "text": "Customer acquisition cost is too high",
            "source": "Master Sheet Tab 2, B2B SaaS row",
            "tier": 2,
            "kind": "pain"
        },
        ...
    ]

OUTPUT FORMAT (ranked.json):
    [
        {
            "cluster_id": 1,
            "canonical": "CaC out of control",
            "variants_with_sources": [
                {"text": "CaC is creeping up", "source": "transcript-005.docx, ~14:20", "tier": 1},
                {"text": "Customer acquisition cost is too high", "source": "Master Sheet Tab 2", "tier": 2},
                {"text": "We're burning paid budget", "source": "reddit.com/r/marketing/xyz", "tier": 3}
            ],
            "score": 8,
            "appearance_count": 3,
            "tier_breakdown": {"tier_1": 1, "tier_2": 1, "tier_3": 1},
            "verification_status": "verified"  // or "unverified — single Tier 2/3 source"
        },
        ...
    ]

CLUSTERING APPROACH:
This script does the SCORING and FORMAT WORK. The CLUSTERING itself is judgment
work that LLMs do better than embedding-similarity heuristics — so when invoked,
the script can either:
  (a) Accept pre-clustered input (Claude clusters first, then passes structured
      JSON to this script for scoring), OR
  (b) Use a simple keyword-overlap heuristic to PRE-cluster, then return that
      structure for Claude to refine

For v1, we use approach (a) — Claude does the clustering judgment, this script
does the deterministic scoring.

TIER WEIGHTS:
    Tier 1: 3
    Tier 2: 2
    Tier 3: 1

VERIFICATION RULE (rule-of-two):
    A cluster is "verified" if:
      - It has at least one Tier 1 appearance, OR
      - It appears in at least 2 sources (any tier)
    Otherwise it is "unverified — single Tier 2/3 source"
"""

import argparse
import json
import sys
from collections import defaultdict


TIER_WEIGHTS = {1: 3, 2: 2, 3: 1}


def score_clusters(clusters: list) -> list:
    """
    clusters: list of {
        "canonical": str,
        "variants_with_sources": [{"text": str, "source": str, "tier": int}, ...]
    }
    Returns same list with score, appearance_count, tier_breakdown, verification_status added.
    """
    ranked = []
    for idx, cluster in enumerate(clusters, start=1):
        variants = cluster.get("variants_with_sources", [])
        if not variants:
            continue

        tier_breakdown = defaultdict(int)
        score = 0
        for v in variants:
            tier = v.get("tier")
            if tier not in TIER_WEIGHTS:
                # Unknown tier — skip but warn
                print(f"WARNING: variant has unknown tier {tier}, skipping", file=sys.stderr)
                continue
            score += TIER_WEIGHTS[tier]
            tier_breakdown[f"tier_{tier}"] += 1

        # Verification rule
        has_tier_1 = tier_breakdown.get("tier_1", 0) > 0
        appearance_count = len(variants)
        if has_tier_1 or appearance_count >= 2:
            verification_status = "verified"
        else:
            verification_status = "unverified — single Tier 2/3 source"

        ranked.append({
            "cluster_id": idx,
            "canonical": cluster.get("canonical", variants[0]["text"]),
            "variants_with_sources": variants,
            "score": score,
            "appearance_count": appearance_count,
            "tier_breakdown": dict(tier_breakdown),
            "verification_status": verification_status,
        })

    # Sort by score descending
    ranked.sort(key=lambda x: (-x["score"], -x["appearance_count"]))

    return ranked


def main():
    parser = argparse.ArgumentParser(
        description="Score and rank pre-clustered pain extractions from multiple sources."
    )
    parser.add_argument("--input", required=True, help="Path to clustered extractions JSON")
    parser.add_argument("--output", required=True, help="Path to write ranked output JSON")
    args = parser.parse_args()

    with open(args.input) as f:
        clusters = json.load(f)

    if not isinstance(clusters, list):
        print("ERROR: input must be a JSON list of clusters", file=sys.stderr)
        sys.exit(1)

    ranked = score_clusters(clusters)

    with open(args.output, "w") as f:
        json.dump(ranked, f, indent=2)

    print(f"Wrote {len(ranked)} ranked clusters to {args.output}")
    if ranked:
        print(f"Top cluster: '{ranked[0]['canonical']}' (score: {ranked[0]['score']})")


if __name__ == "__main__":
    main()
