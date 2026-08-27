"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
from typing import Dict, List, Tuple


ALLOWED_CATEGORIES = {
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
}

SEVERITY_KEYWORDS = (
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


def _contains_any(text: str, keywords: Tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def _build_reason(label: str, evidence: List[str]) -> str:
    evidence_text = ", ".join([f"'{item}'" for item in evidence[:3]]) if evidence else "reported issue"
    return f"Classified as {label} based on words {evidence_text} in the description."


def _category_candidates(description: str) -> Dict[str, List[str]]:
    txt = description.lower()
    candidates: Dict[str, List[str]] = {}

    def add(category: str, evidence: str):
        candidates.setdefault(category, []).append(evidence)

    if _contains_any(txt, ("pothole", "potholes")):
        add("Pothole", "pothole")

    if _contains_any(txt, ("flood", "flooded", "flooding", "underpass flooded", "waterlogged", "water logging")):
        add("Flooding", "flood")

    if _contains_any(txt, ("streetlight", "street light", "lights not working", "dark street", "no lights")):
        add("Streetlight", "streetlight")

    if _contains_any(txt, ("garbage", "waste", "overflow", "not cleared", "trash", "litter")):
        add("Waste", "waste")

    if _contains_any(txt, ("noise", "drilling", "loud", "idling", "horn", "5am")):
        add("Noise", "noise/drilling")

    if _contains_any(txt, ("road collapsed", "collapsed", "crater", "road damage", "road broken")):
        add("Road Damage", "collapsed/crater")

    if _contains_any(txt, ("heritage", "old city", "monument")):
        add("Heritage Damage", "heritage")

    if _contains_any(txt, ("heat", "heatstroke", "heat stroke", "sun exposure")):
        add("Heat Hazard", "heat")

    if _contains_any(txt, ("drain blocked", "drain completely blocked", "main drain blocked", "stormwater drain", "drainage blocked")):
        add("Drain Blockage", "drain blocked")

    return candidates

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Deterministic rules derived from agents.md and skills.md.
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description_raw = row.get("description")
    description = (description_raw or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description missing; unable to classify reliably.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()
    candidates = _category_candidates(description)

    if not candidates:
        category = "Other"
        flag = "NEEDS_REVIEW"
        evidence = ["insufficient category-specific words"]
    elif len(candidates) == 1:
        category = next(iter(candidates.keys()))
        flag = ""
        evidence = candidates[category]
    else:
        # If both flooding and drain blockage appear together, prefer drain blockage
        # when explicit "blocked" wording is present; otherwise treat as ambiguous.
        if (
            "Flooding" in candidates
            and "Drain Blockage" in candidates
            and "blocked" in text
        ):
            category = "Drain Blockage"
            flag = ""
            evidence = candidates["Drain Blockage"] + ["blocked"]
        elif "Heritage Damage" in candidates and "Waste" in candidates:
            # Heritage area with garbage is still operationally a waste complaint.
            category = "Waste"
            flag = ""
            evidence = candidates["Waste"] + candidates["Heritage Damage"]
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"
            evidence = ["multiple competing issue signals"]

    priority = "Urgent" if _contains_any(text, SEVERITY_KEYWORDS) else "Standard"
    reason = _build_reason(category, evidence)

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Classified as Other because category mapping was invalid for this description."

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
    
    Read input CSV, classify each row, and write deterministic results.
    Preserves row order and degrades gracefully on malformed rows.
    """
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    rows_out = []

    try:
        with open(input_path, "r", encoding="utf-8", newline="") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    result = classify_complaint(row or {})
                except Exception as exc:
                    complaint_id = ((row or {}).get("complaint_id") or "").strip()
                    result = {
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Row processing error: {str(exc)[:120]}",
                        "flag": "NEEDS_REVIEW",
                    }
                rows_out.append(result)
    except Exception as exc:
        # Write a single error row so downstream checks get a valid CSV artifact.
        rows_out = [
            {
                "complaint_id": "",
                "category": "Other",
                "priority": "Standard",
                "reason": f"Input read error: {str(exc)[:120]}",
                "flag": "NEEDS_REVIEW",
            }
        ]

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(rows_out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
