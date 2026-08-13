"""
UC-0A — Complaint Classifier
RICE-Enforced Implementation
"""
import argparse
import csv
import re

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

def classify_complaint(row: dict) -> dict:
    """
    Classifies a single citizen complaint row adhering strictly to RICE rules.
    """
    desc = row.get("description", "").strip()
    desc_lower = desc.lower()

    # 1. Priority Determination (Severity Keyword Rule)
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower) or kw in desc_lower:
            priority = "Urgent"
            break

    # 2. Category & Ambiguity Flag Determination
    # Detect matching category signals
    matches = []

    if "pothole" in desc_lower:
        matches.append("Pothole")
    if "drain" in desc_lower:
        matches.append("Drain Blockage")
    if "flood" in desc_lower or "inundated" in desc_lower:
        matches.append("Flooding")
    if "light" in desc_lower or "dark" in desc_lower or "lamp" in desc_lower:
        matches.append("Streetlight")
    if "music" in desc_lower or "noise" in desc_lower or "loudspeaker" in desc_lower:
        matches.append("Noise")
    if "garbage" in desc_lower or "waste" in desc_lower or "dump" in desc_lower or "dead animal" in desc_lower:
        matches.append("Waste")
    if "heat" in desc_lower or "sunstroke" in desc_lower:
        matches.append("Heat Hazard")
    if ("road surface" in desc_lower or "cracked" in desc_lower or "sinking" in desc_lower or "footpath" in desc_lower or "manhole" in desc_lower or "tiles" in desc_lower or "pavement" in desc_lower) and "pothole" not in desc_lower:
        matches.append("Road Damage")

    # Handle structural / contextual heritage case: contextual term "heritage" does not override operational category like Streetlight
    if "heritage" in desc_lower and "Heritage Damage" not in matches:
        if not matches:
            matches.append("Heritage Damage")

    # Deduplicate matches while preserving order
    unique_matches = list(dict.fromkeys(matches))

    flag = ""
    if len(unique_matches) == 1:
        category = unique_matches[0]
    elif len(unique_matches) > 1:
        # Ambiguous case: overlaps multiple operational categories
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 3. Reason Generation (One sentence citing specific verbatim words)
    # Extract key phrase or first sentence
    clause = desc.split(".")[0].strip() if "." in desc else desc
    reason = f"Cited '{clause}' from complaint description."

    return {
        "complaint_id": row.get("complaint_id"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []
    
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            classified = classify_complaint(row)
            results.append(classified)
            
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


