"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
from typing import Dict, List, Tuple


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

SEVERITY_KEYWORDS = {
    "injury",
    "child",
    "children",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
}


def _score_categories(text: str) -> Dict[str, int]:
    lowered = text.lower()
    scores = {category: 0 for category in ALLOWED_CATEGORIES}

    keyword_map = {
        "Pothole": ["pothole", "tyre", "crater"],
        "Flooding": ["flood", "flooded", "waterlogged", "water"],
        "Streetlight": ["streetlight", "streetlights", "dark", "flicker", "sparking"],
        "Waste": ["garbage", "waste", "bins", "dumped", "dead animal", "smell"],
        "Noise": ["noise", "music", "loud", "midnight"],
        "Road Damage": ["road surface", "cracked", "sinking", "tiles", "broken", "footpath"],
        "Heritage Damage": ["heritage", "monument", "old city"],
        "Heat Hazard": ["heat", "hot", "sunstroke", "dehydration"],
        "Drain Blockage": ["drain", "manhole", "blocked", "clogged"],
    }

    for category, keywords in keyword_map.items():
        scores[category] = sum(1 for kw in keywords if kw in lowered)

    return scores


def _extract_evidence(text: str) -> List[str]:
    lowered = text.lower()
    evidence: List[str] = []

    for token in sorted(SEVERITY_KEYWORDS):
        if token in lowered:
            evidence.append(token)

    candidates = [
        "pothole",
        "flooded",
        "drain blocked",
        "streetlight",
        "sparking",
        "garbage",
        "noise",
        "cracked",
        "heritage",
        "manhole",
    ]
    for token in candidates:
        if token in lowered and token not in evidence:
            evidence.append(token)

    return evidence[:3]


def _pick_category(scores: Dict[str, int]) -> Tuple[str, bool]:
    scored = [(cat, val) for cat, val in scores.items() if cat != "Other"]
    top_score = max(val for _, val in scored)
    if top_score <= 0:
        return "Other", True

    top_cats = [cat for cat, val in scored if val == top_score]
    if len(top_cats) > 1:
        return "Other", True

    return top_cats[0], False

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    complaint_id = (row.get("complaint_id") or "").strip() or "UNKNOWN"
    description = (row.get("description") or "").strip()
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing, so category could not be determined from complaint text.",
            "flag": "NEEDS_REVIEW",
        }

    scores = _score_categories(description)
    category, ambiguous = _pick_category(scores)

    lowered = description.lower()
    urgent_hit = [kw for kw in sorted(SEVERITY_KEYWORDS) if kw in lowered]
    if urgent_hit:
        priority = "Urgent"
    elif any(token in lowered for token in ["past midnight", "flickering", "minor"]):
        priority = "Low"
    else:
        priority = "Standard"

    evidence = _extract_evidence(description)
    evidence_text = ", ".join(f"'{item}'" for item in evidence) if evidence else "the complaint wording"
    reason = (
        f"Classified as {category} with {priority} priority based on {evidence_text} in the description."
    )

    flag = "NEEDS_REVIEW" if ambiguous else ""
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
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, "r", encoding="utf-8", newline="") as infile, open(
        output_path, "w", encoding="utf-8", newline=""
    ) as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for index, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row)
            except Exception as exc:  # noqa: BLE001
                fallback_id = (row.get("complaint_id") or "").strip() or f"ROW-{index}"
                result = {
                    "complaint_id": fallback_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row processing failed: {str(exc)}.",
                    "flag": "NEEDS_REVIEW",
                }

            if result["category"] not in ALLOWED_CATEGORIES:
                result["category"] = "Other"
                result["flag"] = "NEEDS_REVIEW"
            if result["priority"] not in {"Urgent", "Standard", "Low"}:
                result["priority"] = "Standard"

            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
