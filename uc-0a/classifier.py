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

CATEGORY_RULES = (
    ("Drain Blockage", ("drain blocked", "drain completely blocked", "stormwater drain", "drainage blocked", "drain 100% blocked")),
    ("Flooding", ("flooded", "flooding", "standing in water", "knee-deep", "underpass flooded")),
    ("Pothole", ("pothole", "potholes", "tyre blowouts", "motorcycle wheel")),
    ("Streetlight", ("streetlight", "streetlights", "unlit", "flickering", "sparking", "dark at night", "lamp post")),
    ("Waste", ("waste", "garbage", "bins", "smell affecting", "overflowing", "not cleared")),
    ("Noise", ("music", "noise", "drilling", "audible", "playing near", "past midnight", "5am daily")),
    ("Heat Hazard", ("44°c", "44c", "heatwave", "dangerous temperatures", "melting", "footwear sticking", "heat")),
    ("Heritage Damage", ("heritage", "historic", "museum", "tram road cobblestones", "cobblestones", "old city")),
    ("Road Damage", ("road surface cracked", "sinking", "upturned paving", "cracked", "utility work", "tarmac surface")),
)


def _normalize_text(value: str) -> str:
    return (value or "").strip().lower()


def _pick_category(description: str) -> tuple[str, str]:
    scores = []
    for category, keywords in CATEGORY_RULES:
        matches = [keyword for keyword in keywords if keyword in description]
        if matches:
            scores.append((category, matches))

    if not scores:
        return "Other", "NEEDS_REVIEW"

    scores.sort(key=lambda item: len(item[1]), reverse=True)
    best_category, best_matches = scores[0]

    if len(scores) > 1 and len(scores[1][1]) == len(best_matches):
        return "Other", "NEEDS_REVIEW"

    return best_category, ""


def _pick_priority(description: str) -> str:
    if any(keyword in description for keyword in SEVERITY_KEYWORDS):
        return "Urgent"
    return "Standard"


def _build_reason(description: str, category: str, priority: str, flag: str) -> str:
    severity_words = [keyword for keyword in SEVERITY_KEYWORDS if keyword in description]

    if flag == "NEEDS_REVIEW":
        if severity_words:
            return f"Marked for review because the description is ambiguous, but it includes '{severity_words[0]}' so priority is {priority}."
        return "Marked for review because the description does not map cleanly to one allowed category."

    evidence = "the description"
    for rule_category, keywords in CATEGORY_RULES:
        if rule_category != category:
            continue
        for keyword in keywords:
            if keyword in description:
                evidence = keyword
                break
        break

    if severity_words:
        return f"Classified as {category} because the description cites '{evidence}' and includes '{severity_words[0]}', which makes it {priority}."
    return f"Classified as {category} because the description cites '{evidence}', which is the strongest category signal."

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    complaint_id = (row.get("complaint_id") or "").strip() or "UNKNOWN"
    description = _normalize_text(row.get("description", ""))

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Marked for review because the complaint description is missing.",
            "flag": "NEEDS_REVIEW",
        }

    category, flag = _pick_category(description)
    priority = _pick_priority(description)
    reason = _build_reason(description, category, priority, flag)

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Marked for review because the derived category was outside the allowed taxonomy."

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

    with open(input_path, "r", newline="", encoding="utf-8") as input_file, open(
        output_path, "w", newline="", encoding="utf-8"
    ) as output_file:
        reader = csv.DictReader(input_file)
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()

        for index, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row)
            except Exception as error:
                complaint_id = (row.get("complaint_id") or f"ROW-{index}").strip() or f"ROW-{index}"
                result = {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Marked for review because classification failed: {error}.",
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
