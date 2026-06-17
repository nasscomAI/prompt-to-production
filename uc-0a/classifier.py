"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
from typing import Dict, List


ALLOWED_CATEGORIES: List[str] = [
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

SEVERITY_KEYWORDS = {
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
}

# Simple keyword -> category mapping (lowercase keys)
CATEGORY_KEYWORDS = {
    "pothole": "Pothole",
    "potholes": "Pothole",
    "flood": "Flooding",
    "flooded": "Flooding",
    "flooding": "Flooding",
    "drain": "Drain Blockage",
    "drains": "Drain Blockage",
    "blocked drain": "Drain Blockage",
    "streetlight": "Streetlight",
    "streetlights": "Streetlight",
    "light out": "Streetlight",
    "light": "Streetlight",
    "garbage": "Waste",
    "waste": "Waste",
    "trash": "Waste",
    "rubbish": "Waste",
    "noise": "Noise",
    "music": "Noise",
    "loud": "Noise",
    "crack": "Road Damage",
    "cracked": "Road Damage",
    "sinkhole": "Road Damage",
    "road damage": "Road Damage",
    "heritage": "Heritage Damage",
    "heat": "Heat Hazard",
    "heatwave": "Heat Hazard",
    "hot": "Heat Hazard",
    "manhole": "Road Damage",
    "manhole cover": "Road Damage",
    "dead animal": "Waste",
    "animal carcass": "Waste",
}


def _find_category_candidates(text: str) -> List[str]:
    text_l = text.lower()
    found = []
    for kw, cat in CATEGORY_KEYWORDS.items():
        if kw in text_l:
            if cat not in found:
                found.append(cat)
    return found


def _find_severity_words(text: str) -> List[str]:
    text_l = text.lower()
    return [w for w in SEVERITY_KEYWORDS if w in text_l]


def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    """Classify a single complaint row.

    Returns a dict with keys: complaint_id, category, priority, reason, flag

    Rules enforced:
    - `category` must be one of ALLOWED_CATEGORIES (exact strings)
    - `priority` is `Urgent` if any SEVERITY_KEYWORDS appear in description
    - `reason` is one sentence and cites specific words found in description
    - `flag` is `NEEDS_REVIEW` when classification is genuinely ambiguous
    """
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    candidates = _find_category_candidates(description)
    severity_hits = _find_severity_words(description)

    # Determine category
    if len(candidates) == 0:
        category = "Other"
    elif len(candidates) == 1:
        category = candidates[0]
    else:
        # multiple categories matched -> ambiguous
        category = candidates[0]

    # Determine flag for ambiguity
    flag = ""
    if len(candidates) > 1:
        flag = "NEEDS_REVIEW"

    # Priority
    priority = "Urgent" if severity_hits else "Standard"

    # Build reason: cite specific words from description
    cited_terms = []
    # prefer category-related keywords
    text_l = description.lower()
    for kw in CATEGORY_KEYWORDS:
        if kw in text_l:
            cited_terms.append(kw)
    # add severity words
    for w in severity_hits:
        if w not in cited_terms:
            cited_terms.append(w)

    if cited_terms:
        cited_display = ", ".join(f"'{t}'" for t in cited_terms[:5])
        reason = f"Description mentions {cited_display}."
    else:
        # fall back to short quoted snippet
        snippet = description.split(".")[0]
        if len(snippet) > 120:
            snippet = snippet[:117] + "..."
        reason = f"Description: '{snippet}'"

    return {
        "complaint_id": complaint_id,
        "category": category if category in ALLOWED_CATEGORIES else "Other",
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV.

    Writes columns: complaint_id, category, priority, reason, flag
    The function is defensive: it continues on row errors and marks problematic rows.
    """
    with open(input_path, newline="", encoding="utf-8") as inp:
        reader = csv.DictReader(inp)
        rows = list(reader)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as outp:
        writer = csv.DictWriter(outp, fieldnames=fieldnames)
        writer.writeheader()
        for i, row in enumerate(rows):
            try:
                result = classify_complaint(row)
            except Exception as e:
                # On failure, write a conservative row and continue
                result = {
                    "complaint_id": row.get("complaint_id", f"row-{i}"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification failed: {e}",
                    "flag": "NEEDS_REVIEW",
                }
            # Ensure we only write allowed category exact strings
            if result.get("category") not in ALLOWED_CATEGORIES:
                result["category"] = "Other"
            writer.writerow(
                {
                    "complaint_id": result.get("complaint_id", ""),
                    "category": result.get("category", "Other"),
                    "priority": result.get("priority", "Standard"),
                    "reason": result.get("reason", ""),
                    "flag": result.get("flag", ""),
                }
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
