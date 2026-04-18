"""
UC-0A — Complaint Classifier
Rule-based classifier aligned with uc-0a/README.md schema (no external APIs).
"""
from __future__ import annotations

import argparse
import csv
import re
from typing import Any

# Exact strings required by workshop schema
CATEGORIES = (
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
)

PRIORITIES = ("Urgent", "Standard", "Low")

SEVERITY_KEYWORDS = (
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
)

# (category, patterns that must match description) — first matching rule wins.
# Patterns are lowercase; matched against lowercase description.
CATEGORY_RULES: list[tuple[str, tuple[str, ...]]] = [
    (
        "Heritage Damage",
        ("heritage", "historic", "old city"),
    ),
    (
        "Heat Hazard",
        ("heat hazard", "heat stroke", "extreme heat", "sunstroke"),
    ),
    (
        "Drain Blockage",
        (
            "drain blocked",
            "drain block",
            "clogged drain",
            "sewage",
            "manhole blocked",
        ),
    ),
    (
        "Flooding",
        (
            "flood",
            "flooded",
            "knee-deep",
            "stranded",
            "underpass",
            "inundat",
            "becomes inaccessible",
        ),
    ),
    (
        "Streetlight",
        (
            "streetlight",
            "street light",
            "lights out",
            "dark at night",
            "flickering",
            "sparking",
            "lamp",
            "electrical",
        ),
    ),
    (
        "Waste",
        (
            "garbage",
            "bins",
            "smell",
            "dead animal",
            "bulk waste",
            "dumped",
            "overflowing",
            "renovation",
        ),
    ),
    (
        "Noise",
        (
            "noise",
            "music",
            "midnight",
            "loud",
            "wedding",
        ),
    ),
    (
        "Pothole",
        (
            "pothole",
            "potholes",
            "crater",
            "tyre damage",
        ),
    ),
    (
        "Road Damage",
        (
            "road surface",
            "cracked",
            "sinking",
            "footpath",
            "manhole",
            "tiles broken",
            "upturned",
            "utility work",
        ),
    ),
]


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def _priority_for_description(desc_lc: str) -> str:
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lc:
            return "Urgent"
    return "Standard"


def _pick_category(desc_lc: str) -> tuple[str, bool]:
    """
    First matching rule in CATEGORY_RULES wins (stable, auditable order).
    Returns (category, needs_review). Other → NEEDS_REVIEW when nothing matched.
    """
    for cat, patterns in CATEGORY_RULES:
        if any(p in desc_lc for p in patterns):
            return cat, False
    return "Other", True


def _reason_from_description(desc: str, category: str, desc_lc: str) -> str:
    """One sentence citing words from the description."""
    quoted: list[str] = []
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lc:
            m = re.search(re.escape(kw), desc, re.IGNORECASE)
            if m:
                quoted.append(m.group(0))
    # category cues
    for token in re.findall(r"[A-Za-z][A-Za-z']+", desc):
        if len(token) > 3 and token.lower() in desc_lc:
            if len(quoted) < 3:
                quoted.append(token)
    snippet = ", ".join(dict.fromkeys(quoted))[:200]
    if not snippet:
        snippet = desc[:120].strip() + ("…" if len(desc) > 120 else "")
    return f"Matched {category.lower()} using wording from the report: {snippet}."


def classify_complaint(row: dict[str, Any]) -> dict[str, Any]:
    """
    Classify a single complaint row.
    Returns: complaint_id, category, priority, reason, flag
    """
    desc = str(row.get("description") or "")
    desc_lc = _norm(desc)
    cid = str(row.get("complaint_id") or "").strip()

    category, ambiguous = _pick_category(desc_lc)
    if category not in CATEGORIES:
        category = "Other"
        ambiguous = True

    priority = _priority_for_description(desc_lc)
    if priority not in PRIORITIES:
        priority = "Standard"

    flag = "NEEDS_REVIEW" if ambiguous else ""

    reason = _reason_from_description(desc, category, desc_lc)

    return {
        "complaint_id": cid,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """Read input CSV, classify each row, write results CSV."""
    rows_out: list[dict[str, Any]] = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                out = classify_complaint(row)
                rows_out.append(out)
            except Exception as exc:
                cid = row.get("complaint_id", "")
                rows_out.append(
                    {
                        "complaint_id": cid,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Classifier error: {exc}",
                        "flag": "NEEDS_REVIEW",
                    }
                )

    out_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(rows_out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
