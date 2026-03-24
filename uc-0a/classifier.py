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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

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
    "Pothole": ["pothole", "pot hole", "crater", "road hole"],
    "Flooding": [
        "flood",
        "flooded",
        "flooding",
        "waterlogged",
        "water logging",
        "standing in water",
        "inundated",
    ],
    "Streetlight": [
        "streetlight",
        "streetlights",
        "street light",
        "street lights",
        "lamp post",
        "lights out",
        "light not working",
        "flickering",
        "dark at night",
        "dark road",
    ],
    "Waste": ["garbage", "waste", "trash", "rubbish", "dump", "litter", "bin overflow"],
    "Noise": ["noise", "loud", "horn", "construction sound", "music", "speaker"],
    "Road Damage": [
        "road damaged",
        "road damage",
        "crack",
        "cracked",
        "sinking",
        "broken road",
        "uneven road",
        "damaged road",
        "footpath",
        "tiles broken",
        "manhole cover missing",
    ],
    "Heritage Damage": ["heritage", "monument", "historic", "vandal", "graffiti"],
    "Heat Hazard": ["heat", "heatwave", "hot", "burn", "sun exposure", "no shade"],
    "Drain Blockage": ["drain", "blocked drain", "clogged drain", "sewer block", "choked gutter", "stagnant water"],
}


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _extract_description(row: dict) -> str:
    for key in ["description", "complaint_description", "complaint", "text", "details"]:
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for value in row.values():
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _find_present_keywords(description: str, keywords: list[str]) -> list[str]:
    normalized = _normalize_text(description)
    present = []
    for keyword in keywords:
        pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
        if re.search(pattern, normalized):
            present.append(keyword)
    return present


def _classify_category(description: str) -> tuple[str, list[str], bool]:
    normalized = _normalize_text(description)
    scores: dict[str, int] = {}
    evidence: dict[str, list[str]] = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        matches = []
        for keyword in keywords:
            pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
            if re.search(pattern, normalized):
                matches.append(keyword)
        if matches:
            scores[category] = len(matches)
            evidence[category] = matches

    if not scores:
        return "Other", [], True

    max_score = max(scores.values())
    top_categories = [category for category, score in scores.items() if score == max_score]

    if len(top_categories) > 1:
        combined_evidence = []
        for category in top_categories:
            combined_evidence.extend(evidence.get(category, []))
        return "Other", combined_evidence[:3], True

    selected = top_categories[0]
    return selected, evidence.get(selected, [])[:3], False

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    description = _extract_description(row)

    if not description:
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing, so classification uses insufficient description evidence.",
            "flag": "NEEDS_REVIEW",
        }

    severity_hits = _find_present_keywords(description, SEVERITY_KEYWORDS)
    priority = "Urgent" if severity_hits else "Standard"

    category, category_evidence, is_ambiguous = _classify_category(description)
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    evidence_terms = category_evidence if category_evidence else severity_hits
    if evidence_terms:
        evidence_text = ", ".join(f"'{term}'" for term in evidence_terms[:3])
        reason = f"The description includes {evidence_text}, which supports category '{category}' and priority '{priority}'."
    else:
        reason = f"The description lacks clear category evidence, so it is classified as '{category}' with priority '{priority}'."

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

    return {
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
    required_fields = ["category", "priority", "reason", "flag"]

    with open(input_path, "r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        input_fields = reader.fieldnames or []
        output_fields = list(input_fields)
        for field in required_fields:
            if field not in output_fields:
                output_fields.append(field)

        rows_to_write = []
        for row in reader:
            safe_row = dict(row)
            try:
                classification = classify_complaint(safe_row)
            except Exception as error:
                classification = {
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification fallback due to row processing error: '{str(error)}'.",
                    "flag": "NEEDS_REVIEW",
                }

            safe_row.update(classification)
            rows_to_write.append(safe_row)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(rows_to_write)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
