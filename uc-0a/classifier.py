"""
UC-0A — Complaint Classifier
RICE + CRAFT implementation for civic complaint classification.
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
    "Other"
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
    "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row into schema:
    category, priority, reason, flag
    """
    desc = row.get("description", "").strip()
    desc_lower = desc.lower()
    loc = row.get("location", "").strip().lower()

    if not desc:
        return {
            **row,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing or empty.",
            "flag": "NEEDS_REVIEW"
        }

    # Determine Priority based on severity keywords
    is_urgent = any(kw in desc_lower for kw in SEVERITY_KEYWORDS)
    
    # Determine Category
    category = "Other"
    flag = ""
    reason_phrase = desc

    if "pothole" in desc_lower:
        category = "Pothole"
        reason_phrase = f"Description notes '{desc}'"
    elif "flood" in desc_lower or "waterlogging" in desc_lower or "standing in water" in desc_lower:
        if "drain" in desc_lower and "blocked" in desc_lower:
            category = "Flooding"
            flag = ""
            reason_phrase = f"Description mentions '{desc}'"
        else:
            category = "Flooding"
            reason_phrase = f"Description reports '{desc}'"
    elif "drain" in desc_lower and "blocked" in desc_lower:
        category = "Drain Blockage"
        reason_phrase = f"Description states '{desc}'"
    elif "heritage" in desc_lower:
        category = "Heritage Damage"
        flag = "NEEDS_REVIEW"
        reason_phrase = f"Description mentions '{desc}'"
    elif "streetlight" in desc_lower or "lights out" in desc_lower or "dark at night" in desc_lower:
        category = "Streetlight"
        reason_phrase = f"Description reports '{desc}'"
    elif "garbage" in desc_lower or "waste" in desc_lower or "dead animal" in desc_lower or "dumped" in desc_lower:
        category = "Waste"
        reason_phrase = f"Description states '{desc}'"
    elif "music" in desc_lower or "noise" in desc_lower or "loud" in desc_lower:
        category = "Noise"
        reason_phrase = f"Description notes '{desc}'"
    elif "heat" in desc_lower or "sunstroke" in desc_lower:
        category = "Heat Hazard"
        reason_phrase = f"Description notes '{desc}'"
    elif "road surface" in desc_lower or "manhole" in desc_lower or "footpath" in desc_lower or "sinking" in desc_lower or "cracked" in desc_lower:
        category = "Road Damage"
        reason_phrase = f"Description reports '{desc}'"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_phrase = f"Category ambiguous from description '{desc}'"

    # Enforce Allowed Categories exact string validation
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Determine priority level
    if is_urgent:
        priority = "Urgent"
    elif category == "Noise":
        priority = "Low"
    else:
        priority = "Standard"

    # Construct one sentence reason citing specific words
    reason = f"Classified as {category} with {priority} priority: {reason_phrase}"

    result = dict(row)
    result["category"] = category
    result["priority"] = priority
    result["reason"] = reason
    result["flag"] = flag
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    classified_rows = []
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        
        # Ensure category, priority, reason, flag are present in header
        for field in ["category", "priority", "reason", "flag"]:
            if field not in fieldnames:
                fieldnames.append(field)
                
        for row in reader:
            classified = classify_complaint(row)
            classified_rows.append(classified)

    with open(output_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(classified_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
