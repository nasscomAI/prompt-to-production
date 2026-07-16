"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re


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

CATEGORY_RULES = [
    ("Drain Blockage", ["drain blocked", "drain completely blocked", "drain 100% blocked", "main drain blocked", "stormwater drain"]),
    ("Pothole", ["pothole", "potholes"]),
    ("Flooding", ["flooded", "floods", "flooding", "rainwater", "knee-deep", "standing in water"]),
    ("Streetlight", ["streetlight", "streetlights", "lights out", "lamp post", "unlit", "darkness", "dark at night"]),
    ("Waste", ["garbage", "waste", "bins overflowing", "dead animal", "not cleared", "dumped", "overflowing"]),
    ("Noise", ["music", "drilling", "amplifiers", "playing", "trucks idling", "engines on", "audible"]),
    ("Heritage Damage", ["heritage", "historic", "museum", "cobblestones", "tram road", "defaced", "heritage stone", "ancient step well"]),
    ("Heat Hazard", ["heat", "heatwave", "44", "45", "52", "temperature", "melting", "dangerous temperatures", "full sun", "burns"]),
    ("Road Damage", ["road surface", "surface cracked", "surface buckled", "collapsed", "subsidence", "subsided", "footpath", "tiles broken", "paving", "crater", "buckled"]),
]

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def find_severity_keyword(description: str) -> str | None:
    normalized = normalize(description)
    for keyword in SEVERITY_KEYWORDS:
        if re.search(rf"\b{re.escape(keyword)}\w*\b", normalized):
            return keyword
    return None


def find_category_matches(description: str) -> list[tuple[str, str]]:
    normalized = normalize(description)
    matches = []
    for category, keywords in CATEGORY_RULES:
        for keyword in keywords:
            if keyword in normalized:
                matches.append((category, keyword))
                break
    return matches


def fallback_evidence(description: str) -> str:
    words = normalize(description).split()
    if not words:
        return "missing description"
    return " ".join(words[:6])


def choose_category(description: str) -> tuple[str, str, str]:
    matches = find_category_matches(description)
    if not matches:
        return "Other", fallback_evidence(description), "NEEDS_REVIEW"

    categories = {category for category, _ in matches}
    category, evidence = matches[0]
    flag = "NEEDS_REVIEW" if len(categories) > 1 else ""
    return category, evidence, flag

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    """
    description = row.get("description", "")
    category, evidence, flag = choose_category(description)
    severity_keyword = find_severity_keyword(description)
    priority = "Urgent" if severity_keyword else "Standard"

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if severity_keyword:
        reason = (
            f"Classified as {category} because the description mentions "
            f"'{evidence}', with Urgent priority triggered by '{severity_keyword}'."
        )
    else:
        reason = (
            f"Classified as {category} because the description mentions "
            f"'{evidence}', with Standard priority because no severity keyword is present."
        )

    return {
        "complaint_id": row.get("complaint_id", ""),
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
    with open(input_path, newline="", encoding="utf-8") as input_file, open(
        output_path, "w", newline="", encoding="utf-8"
    ) as output_file:
        reader = csv.DictReader(input_file)
        writer = csv.DictWriter(output_file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classified as Other because the row failed with '{exc}'.",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
