"""
UC-0A — Complaint Classifier
Implementation based on RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, date_raised, city, ward, location, description, reported_by, days_open, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Simple rule-based classification mapping
    category = "Other"
    reason_words = []
    flag = ""
    
    if "pothole" in desc:
        category = "Pothole"
        reason_words.append("pothole")
    elif "flood" in desc or "water" in desc:
        if "drain" in desc:
            category = "Drain Blockage"
            reason_words.append("drain")
        else:
            category = "Flooding"
            reason_words.append("flood")
    elif "streetlight" in desc or "dark" in desc or "lights" in desc:
        category = "Streetlight"
        reason_words.extend(["streetlight", "dark", "lights"])
    elif "garbage" in desc or "waste" in desc or "smell" in desc or "dead animal" in desc:
        category = "Waste"
        reason_words.extend(["garbage", "waste", "smell", "dead animal"])
    elif "music" in desc or "noise" in desc:
        category = "Noise"
        reason_words.extend(["music", "noise"])
    elif "crack" in desc or "sinking" in desc or "road surface" in desc:
        category = "Road Damage"
        reason_words.append("crack")
    elif "heritage" in desc:
        category = "Heritage Damage"
        reason_words.append("heritage")
    elif "manhole cover missing" in desc:
        category = "Road Damage"
        reason_words.append("manhole")
    
    if not reason_words:
        flag = "NEEDS_REVIEW"
        category = "Other"
        reason = "No specific category matched the description."
    else:
        # Find which of the reason_words is actually in the text
        matched_words = [w for w in reason_words if w in desc]
        if matched_words:
            reason = f"Description contains specific keywords: {', '.join(matched_words)}."
        else:
            flag = "NEEDS_REVIEW"
            category = "Other"
            reason = "Could not determine category from description alone."
            
    # Check severity
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if kw in desc:
            priority = "Urgent"
            reason += f" Priority set to Urgent due to keyword '{kw}'."
            break
            
    # Specific edge case handling based on README rules
    if row.get("description") == "":
        flag = "NEEDS_REVIEW"
        category = "Other"
        reason = "Empty description."

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
    results = []
    fieldnames = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
            for row in reader:
                try:
                    classified_row = classify_complaint(row)
                    results.append(classified_row)
                except Exception as e:
                    # Don't crash on bad rows, just flag them
                    row["category"] = "Other"
                    row["priority"] = "Low"
                    row["reason"] = f"Processing error: {str(e)}"
                    row["flag"] = "NEEDS_REVIEW"
                    results.append(row)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow(row)
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
