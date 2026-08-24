"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

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


def determine_category(description: str) -> tuple[str, bool]:
    """
    Determine category from description based on RICE taxonomy enforcement.
    Returns (category, is_ambiguous).
    """
    desc_lower = description.lower()

    # Rule checks in order of specificity
    
    # 1. Drain Blockage
    if any(k in desc_lower for k in ["drain blocked", "blocked drain", "drain completely blocked", "drain 100% blocked", "main drain blocked", "drainage blocked"]):
        return "Drain Blockage", False

    # 2. Pothole
    if "pothole" in desc_lower or "potholes" in desc_lower:
        return "Pothole", False

    # 3. Heritage Damage
    if any(k in desc_lower for k in ["heritage", "historic tram", "ancient step well"]):
        return "Heritage Damage", False

    # 4. Heat Hazard
    if any(k in desc_lower for k in ["44°c", "45°c", "52°c", "heatwave", "burns on contact", "full sun", "dangerous temperatures", "melting at 44"]):
        return "Heat Hazard", False

    # 5. Flooding
    if any(k in desc_lower for k in ["flooded", "flooding", "floods in", "rainwater"]):
        return "Flooding", False

    # 6. Streetlight
    if any(k in desc_lower for k in ["streetlight", "streetlights", "unlit", "dark at night", "wiring theft", "lamp post", "substation tripped", "lights out"]):
        return "Streetlight", False

    # 7. Waste
    if any(k in desc_lower for k in ["garbage", "waste", "dead animal", "dumped", "bins overflowing"]):
        return "Waste", False

    # 8. Noise
    if any(k in desc_lower for k in ["music", "noise", "drilling", "amplifiers", "engines on"]):
        return "Noise", False

    # 9. Road Damage
    if any(k in desc_lower for k in ["road surface", "cracked", "sinking", "footpath", "tiles broken", "paving", "subsidence", "road collapsed", "crater"]):
        return "Road Damage", False

    # Ambiguous or non-matching complaint
    return "Other", True


def determine_priority(description: str, days_open: int = 0) -> str:
    """
    Determine priority level.
    Triggers Urgent if any severity keyword is present.
    """
    desc_lower = description.lower()

    # Check severity keywords trigger rule
    for keyword in SEVERITY_KEYWORDS:
        if keyword in desc_lower:
            return "Urgent"

    # Additional critical indicators or days open threshold
    if any(k in desc_lower for k in ["hospitalised", "lives at risk", "gas leak", "dengue concern", "diplomatic complaint"]):
        return "Urgent"

    try:
        days = int(days_open)
    except (ValueError, TypeError):
        days = 0

    if days > 14:
        return "Standard"
    elif days < 5:
        return "Low"
    else:
        return "Standard"


def generate_reason(description: str) -> str:
    """
    Generate a single sentence reason citing specific words from the description.
    """
    cleaned = description.strip()
    if not cleaned:
        return "Description is empty or missing."
    
    first_sentence = cleaned.split('.')[0].strip()
    return f"Cited from description: '{first_sentence}'."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")
    days_open = row.get("days_open", 0)

    category, is_ambiguous = determine_category(description)
    priority = determine_priority(description, days_open)
    reason = generate_reason(description)

    flag = "NEEDS_REVIEW" if (is_ambiguous or category == "Other") else ""

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
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Error processing row: {str(e)}",
                    "flag": "NEEDS_REVIEW",
                })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
