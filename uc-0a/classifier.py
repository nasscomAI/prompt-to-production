"""
UC-0A — Complaint Classifier
Implementation guided by agents.md (RICE framework) and skills.md.

Design: Rule-based keyword matching — no LLM dependency required.
All classification decisions are traceable to words in the description.
"""
from __future__ import annotations
import argparse
import csv
import re
import sys

# ── Allowed categories (exact strings) ──────────────────────────────────────
CATEGORIES = [
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

# ── Severity keywords → Urgent (case-insensitive, partial-word) ─────────────
URGENT_KEYWORDS = [
    r"\binjur",        # injury, injured
    r"\bhospitalis",   # hospitalised
    r"\bhospitaliz",   # hospitalized
    r"\bchild\b",
    r"\bschool\b",
    r"\bhospital\b",
    r"\bambulance\b",
    r"\bfire\b",
    r"\bhazard\b",
    r"\bfell\b",
    r"\bcollapse",     # collapse, collapsed
    r"lives at risk",
    r"\bdanger\b",
    r"\bemergency\b",
]

# ── Category keyword rules (order matters — first match wins) ────────────────
# Each entry: (category_name, list_of_regex_patterns)
CATEGORY_RULES = [
    ("Drain Blockage", [
        r"\bdrain\b",
        r"\bblocked\b.*\bdrain",
        r"\bstormwater\b",
        r"\bsewer\b",
        r"\bdrainage\b",
        r"\bmosquito.*breeding",
    ]),
    ("Flooding", [
        r"\bflood",
        r"\binundat",
        r"\bwaterlog",
        r"\bwater.*standing",
        r"\bunderpas.*flood",
        r"\bflood.*underpass",
        r"\bcars.*abandoned",
        r"\bwater.*channel",
        r"\brainwater.*through",
    ]),
    ("Pothole", [
        r"\bpothole",
        r"\bpot.?hole",
    ]),
    ("Road Damage", [
        r"\broad.*collaps",
        r"\bcollaps.*road",
        r"\bcrater\b",
        r"\bcave.?in",
        r"\bcollapsed.*partially",
        r"\bpartially.*collapsed",
        r"\broad.*crack",
    ]),
    ("Streetlight", [
        r"\bstreetlight",
        r"\bstreet.*light",
        r"\blamp.*post",
        r"\blight.*not.*work",
        r"\blighting\b",
    ]),
    ("Heritage Damage", [
        r"\bheritage\b",
        r"\bmonument\b",
        r"\bhistoric\b",
        r"\bheritage.*zone",
    ]),
    ("Waste", [
        r"\bgarbage\b",
        r"\bwaste\b",
        r"\brubbish\b",
        r"\boverflow\b",
        r"\buncollected\b",
        r"\bsolid.*waste",
        r"\btrash\b",
        r"\bwaste.*not.*clear",
        r"\bwaste.*area\b",
    ]),
    ("Noise", [
        r"\bnoise\b",
        r"\bdrilling\b",
        r"\bidling\b",
        r"\bengine.*on\b",
        r"\bloud\b",
        r"\bsound\b",
        r"\bpollution.*noise",
        r"\bnoise.*pollution",
    ]),
    ("Heat Hazard", [
        r"\bheat\b",
        r"\btemperature\b",
        r"\bsunstroke\b",
        r"\bshade\b",
        r"\bheat.*hazard",
    ]),
]


def _is_urgent(description: str) -> bool:
    """Return True if any severity keyword appears in the description."""
    text = description.lower()
    return any(re.search(pattern, text) for pattern in URGENT_KEYWORDS)


def _detect_category(description: str) -> tuple[str, bool]:
    """
    Return (category, is_ambiguous).
    Applies rules in order; returns Other + ambiguous if nothing matches.
    """
    text = description.lower()
    matched = []
    for category, patterns in CATEGORY_RULES:
        if any(re.search(p, text) for p in patterns):
            matched.append(category)

    if len(matched) == 1:
        return matched[0], False
    if len(matched) > 1:
        # Prefer Drain Blockage over Flooding when drain is the stated cause
        if "Drain Blockage" in matched and "Flooding" in matched:
            if re.search(r"\bblocked\b|\bdrain.*blocked\b|\bdrain.*100%", text):
                return "Drain Blockage", False
            return "Flooding", False
        return matched[0], False  # first match wins for other overlaps
    return "Other", True  # nothing matched → ambiguous


def _build_reason(description: str, category: str, priority: str) -> str:
    """Build a one-sentence reason citing specific words from the description."""
    # Extract up to 10 words of the most relevant part of the description
    words = description.split()
    snippet = " ".join(words[:12]) + ("..." if len(words) > 12 else "")
    priority_note = "Urgent due to safety keyword in description." if priority == "Urgent" else ""
    reason = f'Classified as {category} based on "{snippet}"'
    if priority_note:
        reason += f"; {priority_note}"
    return reason + "."


def classify_complaint(row: dict) -> dict:
    """
    skill: classify_complaint
    Classify a single complaint row per agents.md enforcement rules.
    Returns dict with keys: complaint_id, category, priority, reason, flag.
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description field is empty — cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    category, is_ambiguous = _detect_category(description)
    urgent = _is_urgent(description)

    if urgent:
        priority = "Urgent"
    elif is_ambiguous:
        priority = "Low"
    else:
        # Heuristic: descriptions mentioning sustained disruption → Standard
        sustained_patterns = [
            r"\bdays\b", r"\bweeks\b", r"\bmonths\b", r"\bregularly\b",
            r"\bdaily\b", r"\btraders\b", r"\bsuffering\b", r"\blosses\b",
            r"\busable\b", r"\bunusable\b", r"\bslow\b",
        ]
        text_lower = description.lower()
        is_sustained = any(re.search(p, text_lower) for p in sustained_patterns)
        priority = "Standard" if is_sustained else "Low"

    flag = "NEEDS_REVIEW" if is_ambiguous else ""
    reason = _build_reason(description, category, priority)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    skill: batch_classify
    Read input CSV, classify each row, write results CSV.
    Never crashes silently — failed rows are written as Other/Low/NEEDS_REVIEW.
    """
    try:
        with open(input_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        raise

    results = []
    urgent_count = 0
    review_count = 0

    for row in rows:
        try:
            result = classify_complaint(row)
        except Exception as exc:
            cid = row.get("complaint_id", "UNKNOWN")
            print(f"WARNING: Failed to classify {cid}: {exc}", file=sys.stderr)
            result = {
                "complaint_id": cid,
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification error: {exc}",
                "flag": "NEEDS_REVIEW",
            }
        results.append(result)
        if result["priority"] == "Urgent":
            urgent_count += 1
        if result["flag"] == "NEEDS_REVIEW":
            review_count += 1

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(
        f"Done: {len(results)} rows processed | "
        f"{urgent_count} Urgent | "
        f"{review_count} NEEDS_REVIEW"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Results written to {args.output}")
