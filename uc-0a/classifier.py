"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
from typing import Dict, List

CATEGORIES: List[str] = [
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

# Ordered by specificity to reduce misclassification drift.
CATEGORY_RULES = [
    ("Drain Blockage", ["drain block", "blocked drain", "clogged drain", "sewer", "manhole overflow", "waterlogging drain"]),
    ("Flooding", ["flood", "flooded", "waterlogging", "water logged", "inundat", "stagnant water"]),
    ("Streetlight", ["streetlight", "street light", "light pole", "lamp post", "dark street", "no light"]),
    ("Pothole", ["pothole", "potholes", "crater on road"]),
    ("Road Damage", ["road damage", "broken road", "damaged road", "cracked road", "road crack", "road caved", "uneven road"]),
    ("Waste", ["garbage", "trash", "waste", "dumping", "rubbish", "bin overflow", "unclean", "uncleaned"]),
    ("Noise", ["noise", "loud", "horn", "speaker", "construction sound", "dj", "sound pollution"]),
    ("Heritage Damage", ["heritage", "monument", "historic", "temple wall", "graffiti", "deface"]),
    ("Heat Hazard", ["heat", "heatwave", "heat wave", "sunstroke", "high temperature", "no shade"]),
]

AMBIGUITY_HINTS = ["unclear", "not sure", "unknown", "maybe", "seems like", "multiple issues", "various issues"]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _first_present(row: Dict[str, str], candidates: List[str]) -> str:
    lowered = {str(k).lower(): v for k, v in row.items()}
    for key in candidates:
        if key in lowered and lowered[key]:
            return str(lowered[key]).strip()
    return ""


def _extract_description(row: Dict[str, str]) -> str:
    # Accept common variants so the classifier can run on slightly different CSV headers.
    return _first_present(
        row,
        ["description", "complaint", "complaint_text", "text", "details", "issue", "message"],
    )


def _extract_id(row: Dict[str, str]) -> str:
    return _first_present(row, ["complaint_id", "id", "ticket_id", "case_id", "sr_no"])


def _infer_category(desc_norm: str) -> str:
    for category, terms in CATEGORY_RULES:
        if any(term in desc_norm for term in terms):
            return category
    return "Other"


def _infer_priority(desc_norm: str) -> str:
    return "Urgent" if any(k in desc_norm for k in SEVERITY_KEYWORDS) else "Standard"


def _is_ambiguous(desc_norm: str) -> bool:
    if not desc_norm:
        return True
    matched_categories = 0
    for _, terms in CATEGORY_RULES:
        if any(term in desc_norm for term in terms):
            matched_categories += 1
    return matched_categories > 1 or any(hint in desc_norm for hint in AMBIGUITY_HINTS)


def _build_reason(category: str, priority: str, raw_desc: str, desc_norm: str) -> str:
    evidence = []
    for keyword in sorted(SEVERITY_KEYWORDS):
        if keyword in desc_norm:
            evidence.append(keyword)
    if not evidence:
        # Use a short quote from description as grounded evidence.
        snippet = raw_desc.strip()
        snippet = snippet[:80] + ("..." if len(snippet) > 80 else "")
        evidence_text = f"'{snippet}'" if snippet else "'no clear description text'"
    else:
        evidence_text = ", ".join(evidence[:3])
    return f"Classified as {category} with {priority} priority based on description evidence: {evidence_text}."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Enforces UC-0A schema rules from agents.md:
    - Exact category labels
    - Priority in {Urgent, Standard, Low}
    - Urgent on severity keywords
    - One-sentence reason grounded in description
    - NEEDS_REVIEW for genuine ambiguity
    """
    complaint_id = _extract_id(row)
    description = _extract_description(row)
    desc_norm = _normalize(description)

    category = _infer_category(desc_norm)
    if category not in CATEGORIES:
        category = "Other"

    priority = _infer_priority(desc_norm)
    if priority not in {"Urgent", "Standard", "Low"}:
        priority = "Standard"

    ambiguous = _is_ambiguous(desc_norm)
    flag = "NEEDS_REVIEW" if ambiguous else ""

    reason = _build_reason(category, priority, description, desc_norm)
    if "." not in reason:
        reason = f"{reason}."

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
    
    Reads input CSV, classifies each row, and writes result CSV.
    Resilient behavior:
    - does not crash on malformed rows
    - flags rows with missing text for review
    - always writes output rows
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(input_path, "r", newline="", encoding="utf-8") as infile, open(
        output_path, "w", newline="", encoding="utf-8"
    ) as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
                if not _extract_description(row):
                    result["flag"] = "NEEDS_REVIEW"
                    result["category"] = result["category"] if result["category"] in CATEGORIES else "Other"
                    result["priority"] = "Standard"
                    result["reason"] = "Classified conservatively because the complaint description is missing or empty."
            except Exception:
                # Keep pipeline robust; do not stop on single-row failures.
                result = {
                    "complaint_id": _extract_id(row),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Classified conservatively because row parsing failed due to invalid or missing complaint text.",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
