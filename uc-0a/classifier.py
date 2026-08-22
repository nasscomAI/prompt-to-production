"""
UC-0A — Complaint Classifier

Deterministic, rule-based classifier for civic complaints.
Enforcement rules mirror agents.md; skill contracts mirror skills.md.

Usage:
    python classifier.py --input ../data/city-test-files/test_pune.csv \
        --output results_pune.csv
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage",
    "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
]
LOW_KEYWORDS = ["minor", "cosmetic", "trivial"]

# Cue phrases per category. Ordered: earlier entries win ties.
CATEGORY_CUES = [
    ("Heritage Damage", [r"heritage"]),
    ("Pothole", [r"pothole"]),
    ("Flooding", [r"flood", r"inundat", r"knee-?deep water", r"waterlog"]),
    ("Drain Blockage", [r"drain\s+block", r"clogged drain", r"blocked drain"]),
    ("Streetlight", [r"streetlight", r"street light", r"lights?\s+(out|flicker|sparking)", r"lamp post"]),
    ("Waste", [r"garbage", r"waste", r"trash", r"dump(ed|ing)?\b", r"dead animal", r"bins?"]),
    ("Noise", [r"\bnoise\b", r"music", r"loudspeaker"]),
    ("Road Damage", [r"road\s+(surface|crack|sink)", r"footpath", r"sinking", r"upturned"]),
    ("Heat Hazard", [r"heat\s?(wave|hazard|stroke)", r"extreme heat"]),
]


def _find_cue_matches(text):
    """Return list of (category, matched_term) preserving CATEGORY_CUES order."""
    matches = []
    lowered = text.lower()
    for category, patterns in CATEGORY_CUES:
        for pattern in patterns:
            m = re.search(pattern, lowered)
            if m:
                start = max(0, m.start() - 15)
                end = min(len(lowered), m.end() + 15)
                snippet = lowered[start:end].strip()
                matches.append((category, snippet))
                break
    return matches


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = row.get("description") or ""
    if not isinstance(description, str):
        description = str(description)

    cue_matches = _find_cue_matches(description)
    if not cue_matches:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": _priority(description),
            "reason": (
                "No known category cue found in description "
                f"'{description[:60]}'" if description
                else "Description missing or empty"
            ),
            "flag": "NEEDS_REVIEW",
        }

    distinct = {c for c, _ in cue_matches}
    category, snippet = cue_matches[0]
    ambiguous = len(distinct) > 1
    if ambiguous:
        others = sorted(distinct - {category})
        reason = (
            f"Mentions '{snippet}' suggesting {category}, but also "
            f"{', '.join(others)} cues"
        )
    else:
        reason = f"Mentions '{snippet}' which maps to {category}"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": _priority(description),
        "reason": reason,
        "flag": "NEEDS_REVIEW" if ambiguous else "",
    }


def _priority(description: str) -> str:
    lowered = (description or "").lower()
    if any(k in lowered for k in SEVERITY_KEYWORDS):
        return "Urgent"
    if any(k in lowered for k in LOW_KEYWORDS):
        return "Low"
    return "Standard"


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags bad rows as NEEDS_REVIEW instead of crashing; always produces output.
    """
    with open(input_path, newline="", encoding="utf-8-sig") as fin:
        reader = csv.DictReader(fin)
        rows = list(reader)

    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception:  # noqa: BLE001 - never crash the batch
            results.append({
                "complaint_id": (row.get("complaint_id") or "").strip(),
                "category": "Other",
                "priority": "Standard",
                "reason": "Classifier error on this row",
                "flag": "NEEDS_REVIEW",
            })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
