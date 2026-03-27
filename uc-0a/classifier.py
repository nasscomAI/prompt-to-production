"""
UC-0A — Complaint Classifier
Classifies citizen complaint descriptions into category, priority, reason, and flag.
"""
import argparse
import csv
import re
import sys

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

CATEGORY_KEYWORDS = {
    "Pothole": [
        r"\bpotholes?\b", r"\bpot\s+holes?\b", r"\bcrater\b", r"\btyre damage\b",
        r"\bsinkhole\b",
    ],
    "Flooding": [
        r"\bflood\w*\b", r"\bwaterlog\w*\b", r"\binundat\w*\b", r"\bstranded\b",
        r"\bstanding in water\b", r"\bknee.deep\b", r"\bwaist.deep\b",
    ],
    "Streetlight": [
        r"\bstreet\s*light\w*\b", r"\bstrlight\w*\b", r"\blight\w*\s+out\b",
        r"\blight\w*\s+not working\b", r"\blight\w*\s+flicker\w*\b",
        r"\blight\w*\s+sparking\b", r"\barea very dark\b", r"\blamp post\b",
        r"\blamps?\s+not working\b", r"\bunlit\b", r"\bdarkness\b",
        r"\bsubstation tripped\b",
    ],
    "Waste": [
        r"\bgarbage\b", r"\bwaste\b", r"\bbin\w*\s+overflow\w*\b",
        r"\brubbish\b", r"\btrash\b", r"\bdump\w*\b", r"\bdead animal\b",
        r"\bnot removed\b", r"\bsmell\b", r"\bstink\b", r"\bdebris\b",
    ],
    "Noise": [
        r"\bnoise\b", r"\bnoisy\b", r"\bmusic\b", r"\bdecibel\b",
        r"\bloud\b", r"\bloudspeaker\b", r"\bdrill\w*\b", r"\bconstruction noise\b",
        r"\bamplifier\b", r"\bidling\b", r"\bengine\b",
    ],
    "Road Damage": [
        r"\broad\s*surface\b", r"\broad\s*damaged\b", r"\broads?\s+crack\w*\b",
        r"\bsink\w*\b", r"\bfootpath\w*\s+broken\b", r"\btiles?\s+broken\b",
        r"\btiles?\s+upturned\b", r"\broads?\s+broke\w*\b", r"\bcobblestone\w*\b",
        r"\bbroken up\b", r"\bsubsid\w*\b", r"\bbuckled\b",
    ],
    "Heritage Damage": [
        r"\bheritage\b", r"\bhistor\w+\s+building\b", r"\bmonument\b",
        r"\bold\s+city\b", r"\bheritage\s+street\b", r"\bstep well\b",
        r"\bdefaced\b",
    ],
    "Heat Hazard": [
        r"\bheatwave\b", r"\bheat\w*\b", r"\bhot\b", r"\btemperatures?\b",
        r"\bscorch\w*\b", r"\bsunstroke\b", r"\bmelting\b", r"\bburn\w*\b",
    ],
    "Drain Blockage": [
        r"\bdrain\w*\s+block\w*\b", r"\bdrain\w*\s+clog\w*\b",
        r"\bsewer\w*\s+block\w*\b", r"\bsewage\b",
        r"\bgutter\w*\b", r"\bmanhole\b", r"\bsewer\b",
    ],
}


def _find_severity_keywords(desc_lower: str) -> list[str]:
    """Return list of severity keywords found in the description."""
    found = []
    for kw in SEVERITY_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", desc_lower):
            found.append(kw)
    return found


CATEGORY_PRIORITY = [
    "Drain Blockage",
    "Pothole",
    "Flooding",
    "Road Damage",
    "Streetlight",
    "Waste",
    "Heritage Damage",
    "Noise",
    "Heat Hazard",
]


def _match_category(desc_lower: str) -> tuple[str, list[str]]:
    """
    Score each category by keyword match count.
    Returns (category, matched_keywords) or ("Other", []) if ambiguous.
    On tie, prefer category higher in CATEGORY_PRIORITY.
    """
    scores: dict[str, list[str]] = {}
    for cat, patterns in CATEGORY_KEYWORDS.items():
        matched = []
        seen_spans = set()
        for pat in patterns:
            m = re.search(pat, desc_lower)
            if m and m.span() not in seen_spans:
                matched.append(m.group())
                seen_spans.add(m.span())
        if matched:
            scores[cat] = matched

    if not scores:
        return "Other", []

    max_score = max(len(v) for v in scores.values())
    top_cats = [cat for cat, kws in scores.items() if len(kws) == max_score]

    if len(top_cats) == 1:
        return top_cats[0], scores[top_cats[0]]

    # Tiebreaker: prefer category higher in CATEGORY_PRIORITY
    for preferred in CATEGORY_PRIORITY:
        if preferred in top_cats:
            return preferred, scores[preferred]

    return "Other", []


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "")
    if not desc or not desc.strip():
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Standard",
            "reason": "Empty description — cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = desc.lower()
    category, matched_kws = _match_category(desc_lower)
    severity_kws = _find_severity_keywords(desc_lower)

    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    priority = "Urgent" if severity_kws else "Standard"

    # Build reason
    reason_parts = []
    if matched_kws:
        reason_parts.append("Category matched on: " + ", ".join(f'"{w}"' for w in matched_kws))
    else:
        reason_parts.append("No clear category keywords found")
    if severity_kws:
        reason_parts.append("Severity keywords found: " + ", ".join(f'"{w}"' for w in severity_kws))

    reason = "; ".join(reason_parts) + "."

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print(f"ERROR: Input file {input_path} is empty or has no data rows.", file=sys.stderr)
        sys.exit(1)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    for row in rows:
        try:
            result = classify_complaint(row)
        except Exception as e:
            result = {
                "complaint_id": row.get("complaint_id", "UNKNOWN"),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Classification error: {e}",
                "flag": "NEEDS_REVIEW",
            }
        results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
