"""
UC-0A — Complaint Classifier
Implements agents.md enforcement and skills.md contracts.
"""
from __future__ import annotations

import argparse
import csv
from typing import Any

ALLOWED_CATEGORIES = (
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

# README: severity keywords → Urgent
URGENT_KEYWORDS = (
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


def _priority_from_description(description: str) -> str:
    ld = (description or "").lower()
    for kw in URGENT_KEYWORDS:
        if kw in ld:
            return "Urgent"
    return "Standard"


def _category_and_flag(description: str) -> tuple[str, str]:
    """
    Returns (category, flag) where flag is '' or 'NEEDS_REVIEW'.
    Uses description text only; tie-breakers favor more specific infrastructure issues.
    """
    ld = (description or "").strip().lower()
    if not ld:
        return "Other", "NEEDS_REVIEW"

    # Specificity-first chain (see README schema)
    if "heritage" in ld:
        return "Heritage Damage", ""

    if "drain" in ld and any(x in ld for x in ("block", "clog", "choked")):
        return "Drain Blockage", ""

    if any(
        x in ld
        for x in (
            "heatwave",
            "heat wave",
            "heat hazard",
            "extreme heat",
            "melting tar",
            "heat stroke",
        )
    ):
        return "Heat Hazard", ""

    if any(
        x in ld
        for x in (
            "flood",
            "flooded",
            "flooding",
            "knee-deep",
            "knee deep",
            "stranded",
        )
    ):
        return "Flooding", ""

    if any(
        x in ld
        for x in (
            "streetlight",
            "street light",
            "street lights",
            "lights out",
            "lamp post",
            "lamp ",
            "flickering",
            "sparking",
        )
    ):
        return "Streetlight", ""

    if "pothole" in ld:
        return "Pothole", ""

    if any(x in ld for x in ("music", "noise", "loud", "midnight", "wedding")):
        return "Noise", ""

    if any(
        x in ld
        for x in (
            "garbage",
            "bins",
            "bulk waste",
            "dead animal",
            "overflowing",
            "waste dumped",
        )
    ):
        return "Waste", ""

    if any(
        x in ld
        for x in (
            "manhole",
            "road surface",
            "cracked",
            "sinking",
            "footpath",
            "tiles broken",
            "upturned",
        )
    ):
        return "Road Damage", ""

    return "Other", "NEEDS_REVIEW"


def _make_reason(description: str, category: str) -> str:
    """One sentence citing words from the complaint (agents.md)."""
    d = (description or "").strip()
    if not d:
        return "No description text was available to cite."
    snippet = d.replace("\n", " ")
    if len(snippet) > 100:
        snippet = snippet[:97].rsplit(" ", 1)[0] + " …"
    return (
        f'Classification uses exact wording from the complaint such as: "{snippet}" '
        f"({category})."
    )


def classify_complaint(row: dict[str, Any]) -> dict[str, str]:
    """
    One row in → category + priority + reason + flag out (skills.md: classify_complaint).
    """
    cid = str(row.get("complaint_id", "") or "").strip()
    desc = row.get("description")
    if desc is None:
        desc = ""
    else:
        desc = str(desc)

    try:
        priority = _priority_from_description(desc)
        category, flag = _category_and_flag(desc)

        if category not in ALLOWED_CATEGORIES:
            category = "Other"
            flag = "NEEDS_REVIEW"

        reason = _make_reason(desc, category)

        return {
            "complaint_id": cid,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag,
        }
    except Exception:
        return {
            "complaint_id": cid,
            "category": "Other",
            "priority": "Standard",
            "reason": "Row could not be classified safely; defaulting to Other pending review.",
            "flag": "NEEDS_REVIEW",
        }


def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify each row, write results CSV (skills.md: batch_classify).
    """
    fieldnames = ("complaint_id", "category", "priority", "reason", "flag")
    rows_out: list[dict[str, str]] = []

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Input CSV has no header row.")

        for row in reader:
            if row is None:
                continue
            try:
                rows_out.append(classify_complaint(dict(row)))
            except Exception:
                cid = ""
                try:
                    cid = str((row or {}).get("complaint_id", "") or "").strip()
                except Exception:
                    pass
                rows_out.append(
                    {
                        "complaint_id": cid,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Row failed during classification; flagged for review.",
                        "flag": "NEEDS_REVIEW",
                    }
                )

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
