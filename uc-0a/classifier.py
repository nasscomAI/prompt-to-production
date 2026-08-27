"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_PATTERNS = [
    (r"\binjur\w*", "injury"),
    (r"\bchild\w*", "child"),
    (r"\bschool\w*", "school"),
    (r"\bhospital\w*", "hospital"),
    (r"\bambulance\w*", "ambulance"),
    (r"\bfire\w*", "fire"),
    (r"\bhazard\w*", "hazard"),
    (r"\bfell\b", "fell"),
    (r"\bcollaps\w*", "collapse"),
]


def _check_severity(text: str) -> Tuple[bool, List[str]]:
    """Check for severity keywords that trigger Urgent priority."""
    matched = []
    for pattern, name in SEVERITY_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            matched.append(match.group(0))
    return len(matched) > 0, matched


def _extract_citation(text: str) -> str:
    """Extract a representative concise quote from the description for the reason sentence."""
    clean = text.strip().strip('"').strip("'")
    if not clean:
        return "no description provided"
    # Take first sentence or up to 80 characters
    sentences = re.split(r"[.!?]\s+", clean)
    if sentences and sentences[0]:
        first_clause = sentences[0].strip()
        if len(first_clause) <= 90:
            return first_clause
        return first_clause[:87] + "..."
    return clean[:87] + "..." if len(clean) > 90 else clean


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Classified as Other because no description was provided for this complaint.",
            "flag": "NEEDS_REVIEW",
        }

    is_urgent, severity_matches = _check_severity(description)
    priority = "Urgent" if is_urgent else "Standard"

    desc_lower = description.lower()
    scores = {}
    flags = []

    # Category matching rules
    # 1. Pothole
    if re.search(r"\bpotholes?\b|\bcrater\b", desc_lower):
        scores["Pothole"] = scores.get("Pothole", 0) + 4

    # 2. Flooding
    if re.search(r"\bflood\w*|\bwaterlogg\w*|\bsubmerged\b|underpass flooded|floods in|standing in water|channel rainwater", desc_lower):
        scores["Flooding"] = scores.get("Flooding", 0) + 4

    # 3. Drain Blockage
    if re.search(r"\bdrain\w*|\bstormwater\b|\bsewage\b|\bgutter\b|mosquito breeding|drainage", desc_lower):
        scores["Drain Blockage"] = scores.get("Drain Blockage", 0) + 4
        if "blocked" in desc_lower or "debris" in desc_lower or "clogged" in desc_lower:
            scores["Drain Blockage"] = scores.get("Drain Blockage", 0) + 3

    # 4. Streetlight
    if re.search(r"\bstreetlights?\b|\blamp post\b|\blights? out\b|\bsparking\b|\bsubstation tripped\b|\bwiring theft\b|\bunlit\b|\bdarkness\b", desc_lower):
        scores["Streetlight"] = scores.get("Streetlight", 0) + 4

    # 5. Waste
    if re.search(r"\bwaste\b|\bgarbage\b|\bbins\b|\bdumped\b|\bdead animal\b|\brubbish\b|\btrash\b", desc_lower):
        scores["Waste"] = scores.get("Waste", 0) + 4

    # 6. Noise
    if re.search(r"\bnoise\b|\bmusic\b|\bloudspeaker\b|\bamplifiers?\b|\bdrilling\b|\bidling\b|\bwedding (venue|band)\b|\bclub music\b|\bengines on\b", desc_lower):
        scores["Noise"] = scores.get("Noise", 0) + 4

    # 7. Heritage Damage
    if re.search(r"\bheritage\b|\bmonument\b|\bhistoric\b|\bancient step well\b|\bmuseum\b|\bdefaced\b|heritage stone|cobblestones broken", desc_lower):
        scores["Heritage Damage"] = scores.get("Heritage Damage", 0) + 4

    # 8. Heat Hazard
    if re.search(r"\bheat\w*|\bmelting\b|\btemperatures?\b|44°c|45°c|52°c|burns on contact|full sun|bubbling|grass dying", desc_lower):
        scores["Heat Hazard"] = scores.get("Heat Hazard", 0) + 4

    # 9. Road Damage
    if re.search(r"\broad surface\b|\broad collapsed\b|\broad subsid\w*|\bfootpath\b|\bpaving\b|\bbroken tiles\b|\bmanhole cover\b|\bbuckled\b|\bsubsidence\b|road cracked|cracked and sinking|broken bench", desc_lower):
        scores["Road Damage"] = scores.get("Road Damage", 0) + 4
        if "collapsed" in desc_lower or "cracked and sinking" in desc_lower or "subsid" in desc_lower:
            scores["Road Damage"] = scores.get("Road Damage", 0) + 2

    citation = _extract_citation(description).rstrip(".").strip()

    # Resolve category and ambiguity flag
    if not scores:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_category, top_score = sorted_scores[0]

        # Check for ambiguity: secondary category with close score or specific overlaps
        if len(sorted_scores) > 1 and sorted_scores[1][1] >= top_score - 1:
            flag = "NEEDS_REVIEW"
        elif "heritage" in desc_lower and top_category != "Heritage Damage":
            # Mentions heritage context but primary issue is waste/noise/lights
            flag = "NEEDS_REVIEW"
        elif ("flood" in desc_lower or "flooding" in desc_lower) and "drain" in desc_lower:
            flag = "NEEDS_REVIEW"
        else:
            flag = ""

        category = top_category

    # Ensure category is strictly allowed
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Construct single-sentence reason citing description
    if is_urgent:
        reason = f"Classified as {category} with Urgent priority because the complaint reports \"{citation}\" containing safety hazard trigger '{severity_matches[0]}'."
    else:
        reason = f"Classified as {category} with Standard priority because the complaint reports \"{citation}\"."

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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    try:
        with open(input_path, mode="r", encoding="utf-8-sig", errors="replace") as infile:
            reader = csv.DictReader(infile)
            for row_idx, row in enumerate(reader, start=1):
                try:
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as row_err:
                    cid = row.get("complaint_id", f"UNKNOWN_ROW_{row_idx}") if isinstance(row, dict) else f"UNKNOWN_ROW_{row_idx}"
                    results.append({
                        "complaint_id": cid,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Classified as Other due to row processing error: {str(row_err)}.",
                        "flag": "NEEDS_REVIEW",
                    })
    except Exception as file_err:
        print(f"Error opening or reading input file '{input_path}': {file_err}")
        raise

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

