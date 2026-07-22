"""
UC-0A — Complaint Classifier.

Deterministic, rule-based classifier for civic complaints. Every decision
is driven by keyword matches quoted back in the `reason` field so a human
reviewer can audit it.

See agents.md for the enforcement rules this implements.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from typing import Optional


# ── Allowed taxonomy — exact strings, no variations. ────────────────────────
ALLOWED_CATEGORIES = [
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other",
]

# Keywords per category. Order does not affect scoring — each match adds 1.
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "flooded", "flooding", "waterlog", "water-log"],
    "Streetlight": ["streetlight", "street light", "street-light", "lamp post", "lamppost"],
    "Waste": ["garbage", "waste", "trash", "litter", "dumping", "rubbish"],
    "Noise": ["noise", "drilling", "idling", "loud"],
    "Road Damage": [
        "road collapsed",
        "road collapse",
        "road damage",
        "road caved",
        "road caving",
        "crater",
        "sinkhole",
    ],
    "Heritage Damage": [
        "heritage",
        "monument",
        "historic",
        "charminar",
        "fort",
    ],
    "Heat Hazard": [
        "heat",
        "heatstroke",
        "heatwave",
        "temperature",
        "sun exposure",
    ],
    "Drain Blockage": [
        "drain blocked",
        "drain completely blocked",
        "stormwater drain",
        "drain 100%",
        "drainage blocked",
        "sewer blocked",
        "drain choke",
        "drain chocked",
        "main drain",
    ],
}

# Severity keywords that force priority=Urgent (README section on Urgent).
# Match is case-insensitive substring so inflected forms are covered
# (hospitalised → 'hospital', collapsed → 'collapse', children → 'child').
SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]


def _find_keyword_hits(text: str, keywords: list[str]) -> list[str]:
    """Return the keywords (lowercased) that appear as substrings in text."""
    t = text.lower()
    return [kw for kw in keywords if kw in t]


def _score_categories(text: str) -> dict[str, list[str]]:
    """Return {category: [matched_keywords]} for every category with ≥1 hit."""
    hits: dict[str, list[str]] = {}
    for cat, kws in CATEGORY_KEYWORDS.items():
        matches = _find_keyword_hits(text, kws)
        if matches:
            hits[cat] = matches
    return hits


def _quote_phrase(description: str, keyword: str, window: int = 40) -> str:
    """Return a short quote from description containing keyword (for the reason)."""
    idx = description.lower().find(keyword.lower())
    if idx < 0:
        return keyword
    start = max(0, idx - window // 2)
    end = min(len(description), idx + len(keyword) + window // 2)
    snippet = description[start:end].strip()
    # Trim to word boundaries for readability.
    snippet = re.sub(r"^\S*\s", "", snippet, count=1) if start > 0 else snippet
    snippet = re.sub(r"\s\S*$", "", snippet, count=1) if end < len(description) else snippet
    return snippet


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row per agents.md enforcement rules."""
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()
    location = (row.get("location") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "no description provided",
            "flag": "NEEDS_REVIEW",
        }

    search_text = f"{description} {location}"

    # ── Category scoring ────────────────────────────────────────────────
    hits = _score_categories(search_text)

    if not hits:
        category = "Other"
        flag = "NEEDS_REVIEW"
        cat_reason_bits = ["no category keyword matched the description"]
    else:
        # Pick the category with the most keyword hits.
        max_count = max(len(v) for v in hits.values())
        top = [c for c, v in hits.items() if len(v) == max_count]
        if len(top) == 1:
            category = top[0]
            flag = ""
            cat_reason_bits = [
                f"matched '{kw}' in description" for kw in hits[category]
            ]
        else:
            # Tie between multiple categories → per agents.md refuse to pick.
            category = "Other"
            flag = "NEEDS_REVIEW"
            cat_reason_bits = [
                f"ambiguous between {', '.join(sorted(top))} — "
                f"equal keyword hits: "
                + "; ".join(
                    f"{c}:{'|'.join(hits[c])}" for c in sorted(top)
                )
            ]

    # ── Priority ────────────────────────────────────────────────────────
    severity_hits = _find_keyword_hits(description, SEVERITY_KEYWORDS)
    if severity_hits:
        priority = "Urgent"
        sev_reason = f"severity keyword(s) present: {', '.join(severity_hits)}"
    else:
        priority = "Standard"
        sev_reason = "no severity keyword"

    # ── Reason — must quote at least one phrase from the description ────
    quotes = []
    if hits and category != "Other":
        first_kw = hits[category][0]
        quotes.append(f'"{_quote_phrase(description, first_kw)}"')
    if severity_hits:
        quotes.append(f'"{_quote_phrase(description, severity_hits[0])}"')
    quote_str = " / ".join(quotes) if quotes else f'"{description[:60].strip()}"'

    reason = f"{'; '.join(cat_reason_bits)}; {sev_reason}; quoted: {quote_str}"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> list[dict]:
    """Read CSV, classify each row, write results CSV, report summary."""
    try:
        f_in = open(input_path, newline="", encoding="utf-8")
    except OSError as e:
        sys.exit(f"ERROR: cannot open input file '{input_path}': {e}")

    with f_in:
        reader = csv.DictReader(f_in)
        if "description" not in (reader.fieldnames or []):
            sys.exit(
                f"ERROR: input CSV is missing required column 'description'. "
                f"Found: {reader.fieldnames}"
            )
        rows = list(reader)

    results: list[dict] = []
    skipped = 0
    for row in rows:
        if "description" not in row:
            skipped += 1
            print(
                f"[batch_classify] WARN: row missing description column: {row}",
                file=sys.stderr,
            )
            continue
        results.append(classify_complaint(row))

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    urgent_n = sum(1 for r in results if r["priority"] == "Urgent")
    review_n = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
    print(
        f"[batch_classify] wrote {len(results)} rows to {output_path}; "
        f"Urgent={urgent_n}, NEEDS_REVIEW={review_n}, skipped={skipped}",
        file=sys.stderr,
    )
    return results


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    p.add_argument("--input", required=True, help="Path to test_[city].csv")
    p.add_argument("--output", required=True, help="Path to write results CSV")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    batch_classify(args.input, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
