"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

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
    "Pothole": ["pothole"],
    "Flooding": ["flood", "flooded", "waterlogged", "water-logged", "inundat"],
    "Streetlight": ["streetlight", "street light", "lights out", "light out", "flicker", "sparking", "dark at night"],
    "Waste": ["garbage", "trash", "waste", "dead animal", "bins", "dumped"],
    "Noise": ["noise", "loud", "music", "midnight", "speaker"],
    "Road Damage": ["road surface", "cracked", "sinking", "broken", "tiles", "upturned", "manhole", "cover missing"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "heatwave", "heat wave", "hot", "temperature"],
    "Drain Blockage": ["drain blocked", "drainage", "clogged drain", "blocked drain", "manhole blocked"],
}


def _safe_text(value) -> str:
    return str(value or "").strip()


def _extract_description(row: dict) -> str:
    for key in ("description", "complaint", "complaint_text", "details", "issue"):
        if key in row and _safe_text(row.get(key)):
            return _safe_text(row.get(key))
    for key, value in row.items():
        if isinstance(key, str) and "desc" in key.lower() and _safe_text(value):
            return _safe_text(value)
    return ""


def _extract_complaint_id(row: dict) -> str:
    for key in ("complaint_id", "id", "ticket_id"):
        if key in row and _safe_text(row.get(key)):
            return _safe_text(row.get(key))
    return ""


def _find_evidence_phrase(description: str, tokens: list) -> str:
    lowered = description.lower()
    for token in tokens:
        if token in lowered:
            return token
    first_words = " ".join(description.split()[:6]).strip()
    return first_words if first_words else "reported issue"


def _choose_category(description: str) -> tuple:
    lowered = description.lower()
    matches = []
    for category, words in CATEGORY_KEYWORDS.items():
        matched = [w for w in words if w in lowered]
        if matched:
            matches.append((category, matched))

    if not matches:
        return "Other", True, []

    if len(matches) == 1:
        return matches[0][0], False, matches[0][1]

    # Preserve deterministic behavior while marking category ambiguity for review.
    all_evidence = []
    for _, words in matches:
        all_evidence.extend(words)
    return "Other", True, all_evidence


def _choose_priority(description: str, category: str) -> tuple:
    lowered = description.lower()
    severity_hits = [kw for kw in SEVERITY_KEYWORDS if kw in lowered]
    if severity_hits:
        return "Urgent", severity_hits

    low_priority_hints = ["noise", "music", "past midnight", "weeknight"]
    if any(hint in lowered for hint in low_priority_hints) and category == "Noise":
        return "Low", low_priority_hints

    return "Standard", []

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Deterministic taxonomy and urgency mapping based only on row content.
    """
    complaint_id = _extract_complaint_id(row)
    description = _extract_description(row)

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing complaint description; unable to classify confidently.",
            "flag": "NEEDS_REVIEW",
        }

    category, is_ambiguous, category_evidence = _choose_category(description)
    priority, severity_hits = _choose_priority(description, category)

    evidence_tokens = severity_hits or category_evidence
    evidence = _find_evidence_phrase(description, evidence_tokens)

    if is_ambiguous:
        reason = f"The description includes overlapping issue cues such as '{evidence}', so classification is ambiguous."
        flag = "NEEDS_REVIEW"
    elif priority == "Urgent":
        reason = f"Marked Urgent because the description contains severity cue '{evidence}'."
        flag = ""
    else:
        reason = f"Assigned {category} based on complaint wording including '{evidence}'."
        flag = ""

    result = {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }

    if result["category"] not in ALLOWED_CATEGORIES:
        result["category"] = "Other"
        result["flag"] = "NEEDS_REVIEW"
    if result["priority"] not in ALLOWED_PRIORITIES:
        result["priority"] = "Standard"

    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Reads input CSV, classifies each row, and writes a stable output schema.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, mode="r", encoding="utf-8", newline="") as infile, open(
        output_path, mode="w", encoding="utf-8", newline=""
    ) as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {
                    "complaint_id": _extract_complaint_id(row if isinstance(row, dict) else {}),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row processing failed ({type(exc).__name__}); classified conservatively.",
                    "flag": "NEEDS_REVIEW",
                }

            writer.writerow({key: result.get(key, "") for key in fieldnames})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
