"""
source_inventory.py — Scans a client folder and returns a structured inventory
of available source materials for the sms-brief skill.

Usage (from Claude inside the skill):
    python source_inventory.py --client-folder "/path/to/Clients/Kinship"

Returns JSON to stdout with:
    {
        "client_folder": "...",
        "found": {
            "master_sheet": "/path/to/Master Sheet - Kinship.xlsx" | null,
            "onboarding_form": "/path/to/onboarding.docx" | null,
            "case_studies_scored": "/path/to/Scored & Tiered ...xlsx" | null,
            "transcripts": ["/path/to/transcript1.docx", ...],
            "prior_briefs": ["/path/to/2025-09-brief.docx", ...],
            "prior_campaigns": ["/path/to/campaign-log.xlsx", ...] | []
        },
        "gaps": [
            "no sales transcripts found",
            "no scored case studies xlsx — Phase 1 case inventory may not exist",
            ...
        ],
        "summary": {
            "transcript_count": 7,
            "master_sheet_present": true,
            "onboarding_present": true,
            "case_studies_present": true,
            "prior_briefs_count": 2,
            "tier_1_available": true,
            "tier_2_available": true
        }
    }

This is a deterministic file enumeration — doing it via Claude wastes tokens
and misses files randomly. The script's job is just to look around and report.
"""

import argparse
import json
import os
import sys
from pathlib import Path


# Heuristics for identifying file types by name. Adjust as your folder
# conventions evolve.
MASTER_SHEET_HINTS = ["master sheet", "master-sheet", "scaletopia master"]
ONBOARDING_HINTS = ["onboarding", "intake form", "client form"]
CASE_STUDIES_HINTS = ["case studies", "scored", "tiered"]
TRANSCRIPT_HINTS = ["transcript", "fathom", "discovery call", "sales call"]
BRIEF_HINTS = ["brief", "layer a", "tactical brief", "icp"]
CAMPAIGN_LOG_HINTS = ["campaign log", "campaign tracker", "sms log"]

# File extensions we'll consider for each type
TRANSCRIPT_EXTS = {".docx", ".txt", ".pdf", ".md"}
XLSX_EXTS = {".xlsx", ".xlsm", ".xls"}
DOC_EXTS = {".docx", ".pdf"}


def _has_hint(name_lower: str, hints) -> bool:
    return any(h in name_lower for h in hints)


def scan_folder(client_folder: Path) -> dict:
    found = {
        "master_sheet": None,
        "onboarding_form": None,
        "case_studies_scored": None,
        "transcripts": [],
        "prior_briefs": [],
        "prior_campaigns": [],
    }

    if not client_folder.exists():
        return {
            "client_folder": str(client_folder),
            "found": found,
            "gaps": [f"client folder does not exist: {client_folder}"],
            "summary": _empty_summary(),
        }

    # Walk the folder. We expect a flat-ish structure but support nested too.
    for root, _dirs, files in os.walk(client_folder):
        for file_name in files:
            full = Path(root) / file_name
            name_lower = file_name.lower()
            ext = Path(file_name).suffix.lower()

            # Master Sheet
            if ext in XLSX_EXTS and _has_hint(name_lower, MASTER_SHEET_HINTS):
                if not found["master_sheet"]:
                    found["master_sheet"] = str(full)
                continue

            # Case studies scored & tiered
            if ext in XLSX_EXTS and _has_hint(name_lower, CASE_STUDIES_HINTS):
                if not found["case_studies_scored"]:
                    found["case_studies_scored"] = str(full)
                continue

            # Campaign log
            if ext in XLSX_EXTS and _has_hint(name_lower, CAMPAIGN_LOG_HINTS):
                found["prior_campaigns"].append(str(full))
                continue

            # Onboarding form
            if ext in DOC_EXTS and _has_hint(name_lower, ONBOARDING_HINTS):
                if not found["onboarding_form"]:
                    found["onboarding_form"] = str(full)
                continue

            # Briefs
            if ext in DOC_EXTS and _has_hint(name_lower, BRIEF_HINTS):
                found["prior_briefs"].append(str(full))
                continue

            # Transcripts — caught last because they're the most generic
            if ext in TRANSCRIPT_EXTS and _has_hint(name_lower, TRANSCRIPT_HINTS):
                found["transcripts"].append(str(full))
                continue

            # If the file is in a "transcripts" subfolder, treat it as a transcript
            # regardless of name
            if "transcript" in str(full.parent).lower() and ext in TRANSCRIPT_EXTS:
                found["transcripts"].append(str(full))
                continue

    gaps = _compute_gaps(found)
    summary = _compute_summary(found)

    return {
        "client_folder": str(client_folder),
        "found": found,
        "gaps": gaps,
        "summary": summary,
    }


def _compute_gaps(found: dict) -> list:
    gaps = []
    if not found["master_sheet"]:
        gaps.append("no Master Sheet found — Tier 2 will be empty")
    if not found["onboarding_form"]:
        gaps.append("no onboarding form found — may have less context")
    if not found["case_studies_scored"]:
        gaps.append("no scored & tiered case studies xlsx — Tier 4 references missing")
    if not found["transcripts"]:
        gaps.append("no sales transcripts found — Tier 1 unavailable; Field 3 + Field 4b + Field 5 will degrade")
    elif len(found["transcripts"]) < 3:
        gaps.append(f"only {len(found['transcripts'])} transcript(s) found — recurring-pattern signal will be weak")
    if not found["prior_campaigns"]:
        gaps.append("no prior campaign log — Field 7 (Reply Behaviour) will be GAP-marked")
    return gaps


def _compute_summary(found: dict) -> dict:
    return {
        "transcript_count": len(found["transcripts"]),
        "master_sheet_present": found["master_sheet"] is not None,
        "onboarding_present": found["onboarding_form"] is not None,
        "case_studies_present": found["case_studies_scored"] is not None,
        "prior_briefs_count": len(found["prior_briefs"]),
        "tier_1_available": len(found["transcripts"]) > 0,
        "tier_2_available": found["master_sheet"] is not None,
    }


def _empty_summary() -> dict:
    return {
        "transcript_count": 0,
        "master_sheet_present": False,
        "onboarding_present": False,
        "case_studies_present": False,
        "prior_briefs_count": 0,
        "tier_1_available": False,
        "tier_2_available": False,
    }


def main():
    parser = argparse.ArgumentParser(description="Inventory a Scaletopia client folder for sms-brief sources.")
    parser.add_argument("--client-folder", required=True, help="Absolute path to the client folder")
    args = parser.parse_args()

    inventory = scan_folder(Path(args.client_folder))
    print(json.dumps(inventory, indent=2))


if __name__ == "__main__":
    main()
