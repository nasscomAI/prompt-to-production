"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv


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

CATEGORY_KEYWORDS = {
    "Pothole": {"pothole", "crater", "road pit"},
    "Flooding": {"flood", "flooded", "waterlogging", "water-logged", "knee-deep", "inundated"},
    "Streetlight": {"streetlight", "street light", "lights out", "dark", "flickering", "sparking"},
    "Waste": {"garbage", "waste", "bins", "dumped", "dead animal", "smell", "stink"},
    "Noise": {"noise", "loud", "music", "midnight", "speaker", "dj"},
    "Road Damage": {"cracked", "sinking", "broken road", "road surface", "footpath", "tiles"},
    "Heritage Damage": {"heritage", "monument", "old city", "protected structure"},
    "Heat Hazard": {"heat", "hot", "heatwave", "heat wave", "sunstroke"},
    "Drain Blockage": {"drain blocked", "blocked drain", "manhole", "sewer", "drainage choke"},
}


def _normalize(text: str) -> str:
    return (text or "").strip().lower()


def _extract_matches(description: str):
    found = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        matched_terms = [kw for kw in keywords if kw in description]
        if matched_terms:
            found[category] = matched_terms
    return found


def _pick_category(matches: dict) -> tuple[str, list[str], str]:
    if not matches:
        return "Other", [], "NEEDS_REVIEW"

    ranked = sorted(matches.items(), key=lambda item: len(item[1]), reverse=True)
    best_category, best_terms = ranked[0]

    if len(ranked) > 1 and len(ranked[0][1]) == len(ranked[1][1]):
        return "Other", [], "NEEDS_REVIEW"

    if best_category not in ALLOWED_CATEGORIES:
        return "Other", [], "NEEDS_REVIEW"

    return best_category, best_terms, ""


def _pick_priority(description: str, category: str) -> str:
    if any(word in description for word in SEVERITY_KEYWORDS):
        return "Urgent"

    if category in {"Noise", "Waste", "Streetlight"}:
        return "Low"

    return "Standard"

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Enforces exact category taxonomy, urgency keywords, and ambiguity review flag.
    """
    complaint_id = row.get("complaint_id", "")
    description_raw = row.get("description", "")
    description = _normalize(description_raw)

    matches = _extract_matches(description)
    category, matched_terms, flag = _pick_category(matches)
    priority = _pick_priority(description, category)

    if matched_terms:
        reason = f"Classified as {category} due to terms: {', '.join(sorted(set(matched_terms)))}."
    elif flag == "NEEDS_REVIEW":
        reason = "Description did not contain a reliable category signal; manual review is required."
    else:
        reason = f"Classified as {category} based on complaint description."

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
    
    Processes all rows defensively and always writes a complete output CSV.
    """
    out_fields = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, "r", encoding="utf-8", newline="") as in_f:
        reader = csv.DictReader(in_f)
        rows = list(reader)

    with open(output_path, "w", encoding="utf-8", newline="") as out_f:
        writer = csv.DictWriter(out_f, fieldnames=out_fields)
        writer.writeheader()

        for row in rows:
            try:
                result = classify_complaint(row)
            except Exception as exc:  # pragma: no cover - defensive fallback
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification failed: {exc}",
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
