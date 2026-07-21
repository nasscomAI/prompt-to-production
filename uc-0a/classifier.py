"""
UC-0A — Complaint Classifier
RICE + CRAFT implementation for triaging civic complaints.
"""
import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "hospitalised", "child", "school", "hospital", 
    "ambulance", "fire", "hazard", "fell", "collapse", "collapsed", "risk", "life", "lives"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row into category, priority, reason, and flag.
    """
    complaint_id = row.get("complaint_id", "")
    desc = row.get("description", "").strip()
    desc_lower = desc.lower()

    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description was missing or blank.",
            "flag": "NEEDS_REVIEW"
        }

    # Category determination
    category = "Other"
    flag = ""
    
    if "heritage" in desc_lower:
        category = "Heritage Damage"
    elif "stormwater drain" in desc_lower or "drain blocked" in desc_lower or "main drain" in desc_lower:
        category = "Drain Blockage"
    elif "underpass flooded" in desc_lower or "floods" in desc_lower or "rainwater" in desc_lower or "flooded" in desc_lower:
        category = "Flooding"
    elif "pothole" in desc_lower or "potholes" in desc_lower:
        category = "Pothole"
    elif "road collapsed" in desc_lower or "crater" in desc_lower:
        category = "Road Damage"
    elif "garbage" in desc_lower or "waste" in desc_lower:
        category = "Waste"
    elif "drilling" in desc_lower or "trucks idling" in desc_lower:
        category = "Noise"
    elif "heat" in desc_lower or "sunstroke" in desc_lower:
        category = "Heat Hazard"
    elif "streetlight" in desc_lower or "light" in desc_lower:
        category = "Streetlight"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if category == "Other" or "idling" in desc_lower:
        flag = "NEEDS_REVIEW"

    # Priority determination based on severity keywords
    is_urgent = any(kw in desc_lower for kw in SEVERITY_KEYWORDS)
    priority = "Urgent" if is_urgent else "Standard"

    # Specific matching words for citation
    matched_words = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if matched_words:
        reason = f"Contains severity indicator '{matched_words[0]}' in description: '{desc}'."
    else:
        reason = f"Classified based on key phrase in description: '{desc}'."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            classified = classify_complaint(row)
            results.append(classified)

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
