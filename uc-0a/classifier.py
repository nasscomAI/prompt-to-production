import argparse
import csv
import re

# Severity keywords that MUST trigger Urgent priority
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Category mapping with keywords for matching
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater", "hole in road", "hole on road"],
    "Flooding": ["flood", "flooding", "water logging", "waterlogging", "submerged", "water stagnant"],
    "Streetlight": ["streetlight", "street light", "lamp post", "lampost", "light not working", "street lamp"],
    "Waste": ["garbage", "trash", "waste", "dumping", "litter", "refuse", "dead animal", "not removed"],
    "Noise": ["noise", "loud", "sound", "disturbance", "honking", "speaker", "music", "playing"],
    "Road Damage": ["road damage", "broken road", "crack in road", "damaged road", "road broken", "cracked", "sinking", "footpath", "tiles broken", "upturned"],
    "Heritage Damage": ["heritage", "monument", "historical building", "heritage structure"],
    "Heat Hazard": ["heat", "extreme temperature", "no shade", "heat stroke", "overheating"],
    "Drain Blockage": ["drain", "sewage", "clogged", "blockage", "drainage", "sewer", "manhole"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = str(row.get("description", "")).strip()
    
    if not description:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }
    
    desc_lower = description.lower()
    
    # Determine priority
    priority = "Standard"
    for keyword in URGENT_KEYWORDS:
        if keyword.lower() in desc_lower:
            priority = "Urgent"
            break
    
    # Determine category by keyword matching
    category = "Other"
    max_matches = 0
    
    for cat, keywords in CATEGORY_KEYWORDS.items():
        matches = sum(1 for kw in keywords if kw.lower() in desc_lower)
        if matches > max_matches:
            max_matches = matches
            category = cat
    
    # Flag if truly ambiguous
    flag = "NEEDS_REVIEW" if category == "Other" and max_matches == 0 else ""
    
    # Generate reason — cite words from description
    sentences = re.split(r'[.!?]', description)
    reason = sentences[0].strip() if sentences else description[:100]
    if len(reason) > 120:
        reason = reason[:117] + "..."
    
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        original_fieldnames = reader.fieldnames
        rows = list(reader)
    
    # Determine output fieldnames
    output_fieldnames = list(original_fieldnames) + ['category', 'priority', 'reason', 'flag']
    
    results = []
    for row in rows:
        classification = classify_complaint(row)
        row.update(classification)
        results.append(row)
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Done. Classified {len(results)} rows. Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)