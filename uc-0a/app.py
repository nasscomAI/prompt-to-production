"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import os
from typing import Dict, List

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
    "Pothole": ["pothole", "manhole cover missing", "road surface cracked", "road surface", "tire damage", "road surface cracked", "sinkhole"],
    "Flooding": ["flood", "flooded", "knee-deep", "standing water", "water", "underpass flooded", "commuters stranded", "bus stand flooded"],
    "Streetlight": ["streetlight", "lights out", "dark at night", "flickering", "sparking", "street lights", "lamp post"],
    "Waste": ["garbage", "waste", "dumped", "overflowing", "bins", "bulk waste", "refuse", "trash"],
    "Noise": ["noise", "music", "loud", "playing music", "midnight", "weeknights"],
    "Road Damage": ["cracked", "sinking", "upturned", "footpath tiles", "road surface", "depression", "damage"],
    "Heritage Damage": ["heritage", "historic", "monument", "heritage street"],
    "Heat Hazard": ["heat", "hot", "sun", "heatwave", "temperature"],
    "Drain Blockage": ["drain", "blocked", "drain blocked", "blockage", "drainage"],
}
LOW_PRIORITY_CATEGORIES = {"Noise", "Waste", "Heritage Damage"}


def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    description = (row.get("description") or "").strip()
    if not description:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided for classification.",
            "flag": "NEEDS_REVIEW",
        }

    description_lower = description.lower()
    category = determine_category(description_lower)
    priority = determine_priority(description_lower, category)
    flag = determine_flag(description_lower, category)
    reason = build_reason(description, description_lower, category, flag)

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def determine_category(description_lower: str) -> str:
    best_match = "Other"
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in description_lower for keyword in keywords):
            best_match = category
            break

    if best_match == "Other":
        if "heritage" in description_lower and "damage" in description_lower:
            return "Heritage Damage"
        if "street" in description_lower and "light" in description_lower:
            return "Streetlight"
        if "drain" in description_lower or "blocked" in description_lower:
            return "Drain Blockage"
        if "pothole" in description_lower or "manhole" in description_lower:
            return "Pothole"
    if best_match not in ALLOWED_CATEGORIES:
        return "Other"
    return best_match


def determine_priority(description_lower: str, category: str) -> str:
    if any(keyword in description_lower for keyword in SEVERITY_KEYWORDS):
        return "Urgent"
    if category in LOW_PRIORITY_CATEGORIES:
        return "Low"
    return "Standard"


def determine_flag(description_lower: str, category: str) -> str:
    if category == "Other":
        return "NEEDS_REVIEW"
    if "?" in description_lower and category == "Other":
        return "NEEDS_REVIEW"
    return ""


def build_reason(description: str, description_lower: str, category: str, flag: str) -> str:
    if flag == "NEEDS_REVIEW" and category == "Other":
        return f"Text is ambiguous; could not confidently map this description to a single allowed category from: {description}"

    quoted = extract_quote(description, description_lower)
    if quoted:
        return f"Classified as {category} because the report mentions '{quoted}'."

    if category == "Other":
        return "This complaint does not match any of the allowed categories from the provided taxonomy."

    return f"Classified as {category} based on the description."


def extract_quote(description: str, description_lower: str) -> str:
    candidates = [
        "pothole",
        "flooded",
        "road surface cracked",
        "streetlight",
        "garbage",
        "noise",
        "blocked",
        "heritage",
        "knee-deep",
        "sparking",
        "fell",
        "injury",
    ]
    for token in candidates:
        if token in description_lower:
            start = description_lower.index(token)
            return description[start : start + len(token)]
    words = description.split()
    return words[0] if words else "description"


def batch_classify(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        if "description" not in reader.fieldnames:
            raise ValueError("Input CSV is missing required 'description' column.")
        rows = list(reader)

    output_rows: List[Dict[str, str]] = []
    for row in rows:
        try:
            classification = classify_complaint(row)
            output_row = {**row, **classification}
        except Exception:
            output_row = {**row}
            output_row.update(
                {
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Classification failed for this row.",
                    "flag": "NEEDS_REVIEW",
                }
            )
        output_rows.append(output_row)

    if len(output_rows) != len(rows):
        raise RuntimeError("Output row count mismatch after classification.")

    fieldnames = list(reader.fieldnames) + ["category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as out_csv:
        writer = csv.DictWriter(out_csv, fieldnames=fieldnames)
        writer.writeheader()
        for out_row in output_rows:
            writer.writerow(out_row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
