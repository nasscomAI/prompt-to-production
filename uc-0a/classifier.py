"""
UC-0A — Complaint Classifier
Classifies citizen complaints by category and priority using keyword-based rules.
Follows the RICE enforcement schema from the workshop specification.
"""
import argparse
import csv
import re


# Allowed categories — exact strings only
CATEGORIES = [
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

# Severity keywords that must trigger Urgent priority
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Category keyword mappings (order matters — first match wins)
CATEGORY_RULES = [
    ("Pothole", ["pothole", "potholes"]),
    ("Flooding", ["flood", "flooded", "flooding", "waterlogged", "stranded", "submerged"]),
    ("Streetlight", ["streetlight", "street light", "lights out", "light out", "flickering", "sparking", "dark at night"]),
    ("Drain Blockage", ["drain blocked", "drain blockage", "drain completely blocked", "blocked drain", "stormwater drain", "main drain blocked"]),
    ("Waste", ["garbage", "waste", "overflowing", "trash", "rubbish", "not cleared", "dead animal", "bins"]),
    ("Noise", ["noise", "music", "drilling", "loud", "idling", "engines on"]),
    ("Road Damage", ["road surface cracked", "road collapsed", "sinking", "crater", "manhole", "broken", "tiles broken", "upturned", "footpath"]),
    ("Heritage Damage", ["heritage"]),
    ("Heat Hazard", ["heat", "heatstroke", "temperature"]),
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").strip()
    desc_lower = description.lower()
    complaint_id = row.get("complaint_id", "")

    # Determine category
    category = "Other"
    matched_keywords = []
    for cat, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_lower:
                category = cat
                matched_keywords.append(kw)
                break
        if category != "Other":
            break

    # Determine priority based on severity keywords
    priority = "Standard"
    severity_found = []
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            severity_found.append(kw)

    if severity_found:
        priority = "Urgent"

    # If complaint has been open a long time but no severity keywords, keep Standard
    # Low priority for very minor issues with short descriptions and no urgency
    if not severity_found and len(description) < 40:
        priority = "Low"

    # Build reason citing specific words from description
    if severity_found and matched_keywords:
        reason = f"Contains '{matched_keywords[0]}' with severity indicator '{severity_found[0]}' in description."
    elif matched_keywords:
        reason = f"Description mentions '{matched_keywords[0]}' indicating {category} issue."
    elif severity_found:
        reason = f"Contains severity keyword '{severity_found[0]}' in description."
    else:
        reason = f"Classified as {category} based on overall description context."

    # Flag ambiguous complaints — when multiple categories could apply
    flag = ""
    categories_matched = []
    for cat, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_lower:
                if cat not in categories_matched:
                    categories_matched.append(cat)
                break

    if len(categories_matched) > 1:
        flag = "NEEDS_REVIEW"

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
    Handles bad rows gracefully without crashing.
    """
    results = []

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                # Don't crash on bad rows — flag them
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error during classification: {e}",
                    "flag": "NEEDS_REVIEW",
                })

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} complaints.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
