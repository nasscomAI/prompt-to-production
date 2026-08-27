"""
UC-0A — Complaint Classifier
Classifies civic complaints by category, priority, reason, and review flag
following the RICE enforcement rules defined in agents.md.
"""
import argparse
import csv
import re
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "tyre damage", "road surface"],
    "Flooding": ["flood", "flooded", "flooding", "waterlogged", "knee-deep"],
    "Streetlight": ["streetlight", "street light", "lights out", "flickering", "dark at night"],
    "Waste": ["garbage", "waste", "overflowing", "dead animal", "dumped", "bulk waste"],
    "Noise": ["music", "noise", "loud", "midnight", "wedding venue"],
    "Road Damage": ["road surface", "cracked", "sinking", "broken", "upturned", "tiles broken"],
    "Heritage Damage": ["heritage", "old city", "heritage street"],
    "Heat Hazard": ["heat", "hot", "temperature", "heatwave"],
    "Drain Blockage": ["drain", "drainage", "blocked", "manhole"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").strip()
    flag = ""

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing description",
            "flag": "NEEDS_REVIEW"
        }

    description_lower = description.lower()

    category = _classify_category(description_lower)

    priority = _classify_priority(description_lower)

    reason = _generate_reason(description, category)

    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def _classify_category(description_lower: str) -> str:
    """Determine category from description using keyword matching."""
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in description_lower)
        if score > 0:
            scores[cat] = score

    if not scores:
        return "Other"

    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]

    if best_score == 1 and len(scores) > 1:
        second_best = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if second_best[1][1] == 1:
            return "Other"

    return best_category


def _classify_priority(description_lower: str) -> str:
    """Determine priority based on severity keywords."""
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description_lower:
            return "Urgent"
    return "Standard"


def _generate_reason(description: str, category: str) -> str:
    """Generate a one-sentence reason citing specific words from the description."""
    sentences = [s.strip() for s in description.split('.') if s.strip()]
    if sentences:
        first_sentence = sentences[0]
        if len(first_sentence) > 150:
            first_sentence = first_sentence[:147] + "..."
        return f"Classified as {category} based on: \"{first_sentence}\""
    return f"Classified as {category} based on complaint description"


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception as e:
            results.append({
                "complaint_id": row.get("complaint_id", "UNKNOWN"),
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification error: {str(e)}",
                "flag": "NEEDS_REVIEW"
            })

    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
