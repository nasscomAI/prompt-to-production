"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage",
    "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
}

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "road hole", "sinkhole", "crater"],
    "Flooding": ["flood", "flooded", "water logging", "waterlogged", "inundation"],
    "Streetlight": ["streetlight", "light", "dark", "lighting"],
    "Waste": ["garbage", "waste", "dump", "trash", "litter", "bin"],
    "Noise": ["noise", "loud", "music", "sound"],
    "Road Damage": ["road surface", "crack", "broken road", "sinking", "uneven"],
    "Heritage Damage": ["heritage", "monument", "historic"],
    "Heat Hazard": ["heat", "scorch", "burn", "hot"],
    "Drain Blockage": ["drain", "blocked", "clog", "sewer", "drainage"]
}


def normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def find_category(description: str):
    text = normalize_text(description)
    if not text:
        return "Other", True

    matched = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += 1
        if score > 0:
            matched.append((cat, score))

    if not matched:
        return "Other", True

    matched.sort(key=lambda x: x[1], reverse=True)
    if len(matched) > 1 and matched[0][1] == matched[1][1]:
        return matched[0][0], True

    return matched[0][0], False


def determine_priority(description: str) -> str:
    text = normalize_text(description)
    for keyword in SEVERITY_KEYWORDS:
        if keyword in text:
            return "Urgent"
    return "Standard"


def construct_reason(description: str, category: str, priority: str) -> str:
    desc = (description or "").strip()
    if not desc:
        return "No description provided."

    snippet = None
    cues = SEVERITY_KEYWORDS.union({"pothole", "flood", "streetlight", "garbage", "noise", "crack", "heritage", "drain"})
    for keyword in cues:
        pattern = re.compile(r"\\b" + re.escape(keyword) + r"\\b", re.IGNORECASE)
        if pattern.search(desc):
            snippet = keyword
            break

    if snippet is None:
        snippet = desc[:75] + ("..." if len(desc) > 75 else "")

    return f"Classified as {category} because description contains '{snippet}'; priority: {priority}."


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")

    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Insufficient description provided for classification.",
            "flag": "NEEDS_REVIEW"
        }

    category, ambiguous = find_category(description)
    priority = determine_priority(description)
    reason = construct_reason(description, category, priority)
    flag = "NEEDS_REVIEW" if ambiguous else ""

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, mode="r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for idx, row in enumerate(reader, start=1):
                try:
                    result = classify_complaint(row)
                except Exception as e:
                    result = {
                        "complaint_id": row.get("complaint_id", f"row_{idx}"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Classification error: {e}",
                        "flag": "NEEDS_REVIEW"
                    }
                writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
