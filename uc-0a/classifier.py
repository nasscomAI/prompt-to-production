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
    ("Heritage Damage", [r"\bheritage\b"]),
    ("Pothole", [r"\bpotholes?\b"]),
    ("Flooding", [r"\bflood", r"\binundat", r"\bknee-?deep water\b", r"\bwaterlog"]),
    ("Drain Blockage", [r"\bdrain(s)?\s+block", r"\bclogged drain\b", r"\bblocked drain\b"]),
    ("Streetlight", [r"\bstreetlights?\b", r"\bstreet lights?\b", r"\blights?\s+(out|flickering|sparking)\b", r"\blamp posts?\b"]),
    ("Waste", [r"\bgarbage\b", r"\bwaste\b", r"\btrash\b", r"\bdump(ed|ing)?\b", r"\bdead animal\b", r"\bbins?\b"]),
    ("Noise", [r"\bnoise\b", r"\bmusic\b", r"\bloudspeakers?\b"]),
    ("Road Damage", [r"\broad\s+(surface|crack|sinking)", r"\bfootpaths?\b", r"\bsinking\b", r"\bupturned\b"]),
    ("Heat Hazard", [r"\bheat\s?(wave|hazard|stroke)\b", r"\bextreme heat\b"]),
]


def _find_cue_matches(text):
    """Return list of (category, quoted_words) preserving CATEGORY_CUES order."""
    matches = []
    lowered = text.lower()
    for category, patterns in CATEGORY_CUES:
        for pattern in patterns:
            m = re.search(pattern, lowered)
            if m:
                start, end = m.start(), m.end()
                while start > 0 and lowered[start - 1].isalnum():
                    start -= 1
                while end < len(lowered) and lowered[end].isalnum():
                    end += 1
                matches.append((category, text[start:end]))
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


def _matches_word(text: str, keywords) -> bool:
    """Whole-word match allowing plural/verb inflections (child->children)."""
    for keyword in keywords:
        if re.search(r"\b" + re.escape(keyword) + r"(s|es|ed|d|ing|ren)?\b",
                     text):
            return True
    return False


def _priority(description: str) -> str:
    lowered = (description or "").lower()
    if _matches_word(lowered, SEVERITY_KEYWORDS):
        return "Urgent"
    if _matches_word(lowered, LOW_KEYWORDS):
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
