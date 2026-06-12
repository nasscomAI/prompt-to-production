"""
UC-0A — Complaint Classifier

Implements the skills described in skills.md / README.md:
- `classify_complaint(row) -> {complaint_id, category, priority, reason, flag}`
- `batch_classify(input_path, output_path)` reads CSV, applies `classify_complaint`, writes results

Enforcements:
- Category must be exactly one of the allowed taxonomy strings
- Priority must be Urgent if severity keywords present
- Reason must cite specific words from the description
- Flag MUST be `NEEDS_REVIEW` for ambiguous cases or missing description
"""

import argparse
import csv
import re
from typing import Dict


# Allowed categories (exact strings)
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

# Severity keywords that must trigger Urgent
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

# Simple patterns to detect categories (lowercased)
CATEGORY_PATTERNS = {
    "Pothole": r"\bpothole|pot hole\b",
    "Flooding": r"\bflood|flooded|knee-deep|inundat|water logged|waterlogged|water\b",
    "Streetlight": r"\bstreetlight|street light|light(s)? out|lights out|dark at night|flicker|sparking|electric",
    "Waste": r"\bgarbage|trash|rubbish|waste|dumped|dumping|dead animal|overflowing bins|bulk waste",
    "Noise": r"\bnoise|music|loud|loudspeaker|playing music|past midnight",
    "Road Damage": r"\bcrack|cracked|sinking|surface (?:crack|damage)|manhole cover missing|upturned tiles|road surface",
    "Heritage Damage": r"\bheritage|monument|historic|old city|heritage street",
    "Heat Hazard": r"\bheat|heat wave|extreme temp|temperature",
    "Drain Blockage": r"\bdrain.*block|drainage.*block|drain blocked|drainage blocked|clogged drain|drainage",
}


def _contains_severity(description: str) -> bool:
    d = description.lower()
    return any(k in d for k in SEVERITY_KEYWORDS)


def _find_evidence(description: str, pattern: str) -> str:
    m = re.search(pattern, description, flags=re.IGNORECASE)
    if not m:
        return ""
    return m.group(0)


def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    """Classify a single complaint row according to UC-0A skills.

    Returns a dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id") or row.get("id") or "UNKNOWN"
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    matched = []
    evidence = None
    for cat, pat in CATEGORY_PATTERNS.items():
        ev = _find_evidence(description, pat)
        if ev:
            matched.append(cat)
            if not evidence:
                evidence = ev

    if len(matched) == 0:
        category = "Other"
        flag = ""
    elif len(matched) == 1:
        category = matched[0]
        flag = ""
    else:
        # ambiguous: choose the first match but flag for review
        category = matched[0]
        flag = "NEEDS_REVIEW"

    # Priority
    priority = "Urgent" if _contains_severity(description) else "Standard"

    # Reason must cite specific words from description
    if evidence:
        reason = f"Description contains '{evidence}' indicating {category.lower()}."
    else:
        # fallback: include a short excerpt
        excerpt = description[:80].split(".")[0]
        reason = f"Classified as {category} based on description excerpt: '{excerpt}'."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, apply classify_complaint per row, write results CSV.

    Guarantees:
    - Writes an output file even if some rows fail
    - Flags problematic rows with NEEDS_REVIEW
    """
    results = []
    try:
        with open(input_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for rn, row in enumerate(reader, start=2):
                try:
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", f"ROW_{rn}"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Error during classification: {e}",
                        "flag": "NEEDS_REVIEW",
                    })
    except FileNotFoundError:
        raise

    # Ensure output directory exists implicitly by attempting to write
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, 'w', newline='', encoding='utf-8') as out:
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")