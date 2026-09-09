"""
UC-0A — Complaint Classifier
Builds on agents.md (enforcement rules) and skills.md (classify_complaint, batch_classify).
"""
import argparse
import csv

CATEGORIES = {
    "pothole": "Pothole",
    "crater": "Pothole",
    "flood": "Flooding",
    "flooded": "Flooding",
    "waterlogged": "Flooding",
    "streetlight": "Streetlight",
    "lights out": "Streetlight",
    "garbage": "Waste",
    "waste": "Waste",
    "bins": "Waste",
    "animal": "Waste",
    "noise": "Noise",
    "music": "Noise",
    "road damage": "Road Damage",
    "road surface": "Road Damage",
    "cracked": "Road Damage",
    "sinking": "Road Damage",
    "sunken": "Road Damage",
    "footpath": "Road Damage",
    "heritage": "Heritage Damage",
    "heat": "Heat Hazard",
    "drain": "Drain Blockage",
    "drainage": "Drain Blockage",
}

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# exact list from enforcement — any description not matching one of these is ambiguous
VAULTED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]


def _detect_category(description: str):
    lower = description.lower()
    for keyword, cat in CATEGORIES.items():
        if keyword in lower:
            return cat
    return None


def _detect_priority(description: str, category: str):
    lower = description.lower()
    if any(kw in lower for kw in SEVERITY_KEYWORDS):
        return "Urgent"
    if category in ("Flooding", "Drain Blockage"):
        return "Standard"
    return "Standard"


def _build_reason(category: str, description: str, flag: str):
    lower = description.lower()
    if flag == "NEEDS_REVIEW":
        return f"Description does not clearly match a listed category, so it is flagged for review: \"{description}\""
    for keyword, cat in CATEGORIES.items():
        if cat == category and keyword in lower:
            idx = lower.find(keyword)
            end = idx + len(keyword)
            snippet = description[idx:end]
            return f"Description reports \"{snippet}\", classified as {category}."
    return f"Classified as {category} based on \"{description}\"."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided to determine a category.",
            "flag": "NEEDS_REVIEW",
        }

    category = _detect_category(description)
    flag = ""
    if category is None:
        category = "Other"
        flag = "NEEDS_REVIEW"

    priority = _detect_priority(description, category)
    reason = _build_reason(category, description, flag)

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
    """
    results = []
    with open(input_path, newline="", encoding="utf-8") as inf:
        reader = csv.DictReader(inf)
        for row in reader:
            try:
                results.append(classify_complaint(row))
            except Exception:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Row could not be processed.",
                    "flag": "NEEDS_REVIEW",
                })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as outf:
        writer = csv.DictWriter(outf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
