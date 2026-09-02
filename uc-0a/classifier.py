"""
UC-0A — Complaint Classifier
Deterministic classification based on uc-0a/agents.md and uc-0a/skills.md.
"""
import argparse
import csv
import re

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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_PATTERNS = [
    r"\binjur",
    r"\bchild",
    r"\bschool",
    r"\bhospital",
    r"\bambulance",
    r"\bfire\b",
    r"\bhazard",
    r"\bfell\b",
    r"\bcollapse",
]

CATEGORY_PATTERNS = {
    "Pothole": [
        r"\bpotholes?\b",
    ],
    "Flooding": [
        r"\bflooded\b",
        r"\bflooding\b",
        r"\bfloods\b",
        r"\bknee-deep\b",
        r"\bstanding in water\b",
        r"\bwaterlogging\b",
        r"\bwater-logged\b",
        r"\brainwater through\b",
    ],
    "Streetlight": [
        r"\bstreetlights?\b",
        r"\bstreet\s+lights?\b",
        r"\blights?\s+out\b",
        r"\blamp\s*posts?\b",
        r"\bunlit\b",
        r"\bflickering\b",
    ],
    "Waste": [
        r"\bgarbage\b",
        r"\bwaste\b",
        r"\bbins?\b",
        r"\bdumped\b",
        r"\bdead animal\b",
        r"\brubbish\b",
        r"\blitter\b",
    ],
    "Noise": [
        r"\bmusic\b",
        r"\bdrilling\b",
        r"\bamplifiers?\b",
        r"\bloudspeakers?\b",
        r"\bengines on\b",
        r"\bnoise\b",
    ],
    "Road Damage": [
        r"\broad surface cracked\b",
        r"\broad cracked\b",
        r"\bsinking\b",
        r"\broad collapsed\b",
        r"\bcrater\b",
        r"\bfootpath\b",
        r"\btiles broken\b",
        r"\bmanhole cover missing\b",
        r"\broad subsided\b",
        r"\broad subsidence\b",
        r"\bsurface buckled\b",
    ],
    "Heritage Damage": [
        r"\bhistoric tram\b",
        r"\bcobblestones broken\b",
        r"\bheritage residential building exterior defaced\b",
        r"\bdefaced\b",
        r"\bancient step well\b",
        r"\bheritage stone not replaced\b",
    ],
    "Heat Hazard": [
        r"\bmelting at\b",
        r"\bheatwave\b",
        r"\bdangerous temperatures?\b",
        r"\bsurface bubbling\b",
        r"\btemperature unbearable\b",
        r"\bburns on contact\b",
        r"\bfull sun\b",
        r"\bstoring heat\b",
    ],
    "Drain Blockage": [
        r"\bdrain blocked\b",
        r"\bblocked drain\b",
        r"\bstormwater drain\b",
        r"\bmain drain\b",
        r"\bdrainage\b",
    ],
}


def _extract_snippet(text: str, target: str) -> str:
    """Extract a single sentence or clause from text containing target."""
    clauses = re.split(r"(?<=[.!?])\s+", text)
    for c in clauses:
        if target.lower() in c.lower():
            return c.strip().rstrip(".!?")
    return target.strip().rstrip(".!?")


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    if not isinstance(row, dict):
        return {
            "complaint_id": "UNKNOWN",
            "category": "Other",
            "priority": "Standard",
            "reason": "Complaint description is missing or invalid.",
            "flag": "NEEDS_REVIEW",
        }

    complaint_id = str(row.get("complaint_id", "") or "UNKNOWN").strip()
    raw_desc = row.get("description")

    if raw_desc is None or not str(raw_desc).strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Complaint description is missing or invalid.",
            "flag": "NEEDS_REVIEW",
        }

    description = str(raw_desc).strip()

    # 1. Evaluate mandatory severity keywords (non-overridable Urgent)
    severity_matched = None
    for pattern in SEVERITY_PATTERNS:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            severity_matched = match.group(0)
            break

    # 2. Evaluate Category Matches
    matched_categories = {}
    for cat, patterns in CATEGORY_PATTERNS.items():
        for pat in patterns:
            match = re.search(pat, description, re.IGNORECASE)
            if match:
                matched_categories[cat] = match.group(0)
                break

    # Determine category and ambiguity flag
    if len(matched_categories) == 1:
        category = next(iter(matched_categories.keys()))
        category_trigger = matched_categories[category]
        flag = ""
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        category_trigger = ", ".join(matched_categories.values())
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        category_trigger = None

    # 3. Determine Priority
    if severity_matched:
        priority = "Urgent"
    elif category == "Noise":
        priority = "Low"
    else:
        priority = "Standard"

    # 4. Formulate single-sentence reason citing specific words from description
    if severity_matched:
        sev_quote = _extract_snippet(description, severity_matched)
        cat_quote = _extract_snippet(description, category_trigger) if category_trigger else ""
        if cat_quote and sev_quote and cat_quote.lower() != sev_quote.lower():
            reason = f'Classified as {category} based on "{cat_quote}" and assigned Urgent priority due to "{sev_quote}".'
        else:
            reason = f'Classified as {category} based on "{sev_quote or cat_quote}" and assigned Urgent priority due to severe safety risk.'
    elif flag == "NEEDS_REVIEW":
        if len(matched_categories) > 1:
            cat_phrases = [_extract_snippet(description, trig) for trig in matched_categories.values()]
            quoted_phrases = ' and '.join(f'"{p}"' for p in cat_phrases[:2])
            reason = f'Classified as Other and flagged NEEDS_REVIEW citing {quoted_phrases} due to conflicting categories, with {priority} priority as an active disruption.'
        else:
            first_clause = re.split(r"(?<=[.!?])\s+", description)[0].strip().rstrip(".!?")
            reason = f'Classified as Other and flagged NEEDS_REVIEW citing "{first_clause}" as it falls outside defined categories, with {priority} priority.'
    elif priority == "Low":
        quote = _extract_snippet(description, category_trigger)
        reason = f'Classified as {category} based on "{quote}" and assigned Low priority as a non-hazardous nuisance issue.'
    else:  # priority == "Standard"
        quote = _extract_snippet(description, category_trigger)
        reason = f'Classified as {category} based on "{quote}" and assigned Standard priority due to active municipal disruption without urgent safety hazards.'

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Safely handles malformed rows and avoids crashing.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                classified = classify_complaint(row)
            except Exception:
                complaint_id = row.get("complaint_id", "UNKNOWN") if isinstance(row, dict) else "UNKNOWN"
                classified = {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Complaint description is missing or invalid.",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(classified)

    with open(output_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
