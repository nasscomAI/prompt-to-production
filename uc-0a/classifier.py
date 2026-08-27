"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
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

ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}

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

# Phrase-level signals are used to reduce taxonomy drift and keep classification deterministic.
CATEGORY_PATTERNS = {
    "Pothole": [
        r"\bpothole\b",
    ],
    "Flooding": [
        r"\bflood\b",
        r"\bflooded\b",
        r"\bflooding\b",
        r"\bwater[ -]?logged\b",
        r"\bstranded\b",
        r"\bundergroundpass\b",
        r"\bunderpass\b",
        r"\binaccessible\b",
    ],
    "Streetlight": [
        r"\bstreet ?light\b",
        r"\blights? out\b",
        r"\bflicker(?:ing)?\b",
        r"\bsparking\b",
        r"\bdark at night\b",
    ],
    "Waste": [
        r"\bgarbage\b",
        r"\bbins?\b",
        r"\bwaste\b",
        r"\blitter\b",
        r"\bdead animal\b",
        r"\bdumped\b",
        r"\boverflow(?:ing)?\b",
        r"\bsmell\b",
    ],
    "Noise": [
        r"\bnoise\b",
        r"\bmusic\b",
        r"\bloud\b",
        r"\bdrilling\b",
        r"\bidling\b",
        r"\bengines? on\b",
        r"\bmidnight\b",
    ],
    "Road Damage": [
        r"\bcrack(?:ed)?\b",
        r"\bsinking\b",
        r"\bcollapse(?:d)?\b",
        r"\bcrater\b",
        r"\bbroken\b",
        r"\bupturned\b",
        r"\bmanhole\b",
        r"\bmissing\b",
        r"\broad surface\b",
        r"\bfootpath\b",
        r"\btiles\b",
    ],
    "Heritage Damage": [
        r"\bheritage\b",
    ],
    "Heat Hazard": [
        r"\bheat\b",
        r"\bheatwave\b",
        r"\bheat hazard\b",
        r"\bextreme hot\b",
    ],
    "Drain Blockage": [
        r"\bdrain(?:age)? blocked\b",
        r"\bblocked drain\b",
        r"\bstormwater drain\b",
        r"\bdrain blocked\b",
        r"\bclogged drain\b",
        r"\bdebris\b",
    ],
}


def _match_terms(text: str, patterns: list[str]) -> list[str]:
    matched = []
    for pattern in patterns:
        if re.search(pattern, text):
            matched.append(pattern.replace("\\b", ""))
    return matched


def _detect_priority(text: str) -> tuple[str, list[str]]:
    matches = []
    for kw in SEVERITY_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}", text):
            matches.append(kw)
    if matches:
        return "Urgent", matches
    return "Standard", []


def _choose_category(text: str) -> tuple[str, list[str], bool]:
    category_hits: dict[str, list[str]] = {}
    for category, patterns in CATEGORY_PATTERNS.items():
        hits = _match_terms(text, patterns)
        if hits:
            category_hits[category] = hits

    if not category_hits:
        return "Other", [], True

    # Strong disambiguation rules for overlapping classes.
    if "Pothole" in category_hits:
        return "Pothole", category_hits["Pothole"][:2], False
    if "Heritage Damage" in category_hits:
        return "Heritage Damage", category_hits["Heritage Damage"][:2], False
    if "Streetlight" in category_hits:
        return "Streetlight", category_hits["Streetlight"][:2], False
    if "Heat Hazard" in category_hits:
        return "Heat Hazard", category_hits["Heat Hazard"][:2], False

    # Flooding takes precedence over drain blockage if flood impact is explicit.
    if "Flooding" in category_hits:
        return "Flooding", category_hits["Flooding"][:2], False
    if "Drain Blockage" in category_hits:
        return "Drain Blockage", category_hits["Drain Blockage"][:2], False

    # If multiple remaining categories tie by hit count, mark as ambiguous.
    ranked = sorted(category_hits.items(), key=lambda item: len(item[1]), reverse=True)
    top_category, top_hits = ranked[0]
    if len(ranked) > 1 and len(ranked[1][1]) == len(top_hits):
        return "Other", top_hits[:2], True
    return top_category, top_hits[:2], False


def _build_reason(category: str, category_evidence: list[str], severity_hits: list[str]) -> str:
    evidence = []
    for item in category_evidence:
        cleaned = item.strip().replace("(?:ing)?", "ing")
        if cleaned and cleaned not in evidence:
            evidence.append(cleaned)
    for kw in severity_hits:
        if kw not in evidence:
            evidence.append(kw)

    if evidence:
        cited = "', '".join(evidence[:3])
        return f"Classified as {category} because description includes '{cited}'."
    return f"Classified as {category} based on the available description text."


def _normalize_output(record: dict) -> dict:
    category = record.get("category", "Other")
    priority = record.get("priority", "Standard")
    reason = str(record.get("reason", "")).strip()
    flag = str(record.get("flag", "")).strip()

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
        if not reason:
            reason = "Invalid category generated; moved to Other for review."

    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"
        flag = "NEEDS_REVIEW"
        if not reason:
            reason = "Invalid priority generated; moved to Standard for review."

    if not reason:
        reason = "Description missing; unable to classify from evidence."

    return {
        "complaint_id": str(record.get("complaint_id", "")).strip(),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "NEEDS_REVIEW" if flag == "NEEDS_REVIEW" else "",
    }

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Applies UC-0A enforcement:
    - strict category taxonomy
    - Urgent when severity keywords are present
    - one-sentence reason with cited evidence
    - ambiguous cases flagged for review
    """
    complaint_id = str((row or {}).get("complaint_id", "")).strip()
    description_raw = (row or {}).get("description", "")
    description = str(description_raw).strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description missing; unable to classify from evidence.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()
    category, category_evidence, ambiguous = _choose_category(text)
    priority, severity_hits = _detect_priority(text)

    result = {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": _build_reason(category, category_evidence, severity_hits),
        "flag": "NEEDS_REVIEW" if ambiguous else "",
    }
    return _normalize_output(result)


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Reads input CSV, classifies all rows, and writes output CSV.
    Invalid rows are not dropped; they are marked NEEDS_REVIEW.
    """
    results = []

    with open(input_path, "r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        for idx, row in enumerate(reader, start=1):
            row = row or {}
            row.setdefault("complaint_id", f"ROW-{idx}")
            try:
                classified = classify_complaint(row)
            except Exception:
                classified = {
                    "complaint_id": str(row.get("complaint_id", f"ROW-{idx}")),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Row processing error; unable to classify from evidence.",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(_normalize_output(classified))

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
