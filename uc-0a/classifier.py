"""
UC-0A — Complaint Classifier
Updated standalone Python script mimicking deterministic extraction according to the RICE schema without external APIs.
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row deterministically based on keyword checks.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # --- Priority & Reason Logic ---
    priority = "Standard"
    reason_words = []
    for word in URGENT_KEYWORDS:
        if word in description.lower():
            priority = "Urgent"
            reason_words.append(word)
    
    if reason_words:
        reason = f"Urgent severity keyword(s) found: {', '.join(reason_words)}."
    elif not description.strip():
        reason = "Empty description."
    else:
        reason = "Standard complaint without specific urgency keywords."

    # --- Category Logic ---
    category = "Other"
    flag = ""
    
    if any(w in description for w in ["pothole"]):
         category = "Pothole"
    elif any(w in description for w in ["flood", "water", "overflow"]):
         category = "Flooding"
    elif any(w in description for w in ["streetlight", "light", "dark"]):
         category = "Streetlight"
    elif any(w in description for w in ["waste", "garbage", "trash"]):
         category = "Waste"
    elif any(w in description for w in ["noise", "loud", "music"]):
         category = "Noise"
    elif any(w in description for w in ["road damage", "crack"]):
         category = "Road Damage"
    elif any(w in description for w in ["heritage", "monument"]):
         category = "Heritage Damage"
    elif any(w in description for w in ["heat", "sun"]):
         category = "Heat Hazard"
    elif any(w in description for w in ["drain", "clog", "sewage"]):
         category = "Drain Blockage"
    else:
         category = "Other"
         flag = "NEEDS_REVIEW"

    # Flag ambiguous items or blank descriptions
    if not description.strip():
         flag = "NEEDS_REVIEW"
         category = "Other"

    # Extract EXACT keys as instructed by skills.md
    result = {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }
    
    return result

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    fieldnames = []
    rows = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames if reader.fieldnames else []
            for r in reader:
                rows.append(r)
    except Exception as e:
        print(f"Failed to read input file {input_path}: {e}")
        return

    # Ensure fieldnames match exactly the skill.md requirements
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    classified_rows = []
    for r in rows:
        try:
            classified_row = classify_complaint(r)
            classified_rows.append(classified_row)
        except Exception as e:
            # Not crashing on bad rows - output the error safely mapped to exact schema
            error_row = {
                "complaint_id": r.get("complaint_id", ""),
                "category": "Other",
                "priority": "Low",
                "reason": "Error during classification",
                "flag": "NEEDS_REVIEW"
            }
            classified_rows.append(error_row)

    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(classified_rows)
    except Exception as e:
        print(f"Failed to write results file {output_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
