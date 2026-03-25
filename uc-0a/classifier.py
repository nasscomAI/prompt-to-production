"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classifies a citizen complaint strictly based on the provided description text.
    Implements the R.I.C.E. rules from agents.md.
    """
    # OPERATIONAL BOUNDARY: Only use description text, disregard geography/location.
    description = row.get("description", "")
    if not description:
        return {
            "complaint_id": row.get("complaint_id", "UNKNOWN"),
            "category": "Other",
            "priority": "Standard",
            "reason": "The description is empty and cannot be classified.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()
    
    # 1. TAXONOMY MAPPING (Rigid Schema)
    taxonomy = {
        "Pothole": ["pothole", "manhole", "road cavity", "hole in road"],
        "Flooding": ["flooding", "flooded", "flood", "water logging", "waterlogging", "underpass flooded"],
        "Streetlight": ["streetlight", "lights out", "flickering", "dark", "street lamp"],
        "Waste": ["garbage", "waste", "trash", "refuse", "dumped", "bin", "animal", "smell"],
        "Noise": ["noise", "loud", "music", "midnight", "sound"],
        "Road Damage": ["road surface", "cracked", "sinking", "footpath", "tiles", "pavement", "broken"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat", "sun", "temperature", "shade"],
        "Drain Blockage": ["drain", "sewage", "gutter", "blockage", "clogged"],
    }
    
    category = "Other"
    matched_cat_word = None
    for cat, keywords in taxonomy.items():
        for keyword in keywords:
            if keyword in desc_lower:
                category = cat
                matched_cat_word = keyword
                break
        if category != "Other":
            break
            
    # 2. PRIORITY SCHEMA (Severity Keywords)
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    matched_urgent_word = None
    for word in urgent_keywords:
        if word in desc_lower:
            priority = "Urgent"
            matched_urgent_word = word
            break
            
    # 3. REFUSAL RULE (Ambiguity Check)
    flag = ""
    # If no category was determined or if description is too short to be certain
    if category == "Other" or len(description.split()) < 3:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Category cannot be determined with high certainty from description alone."
    else:
        # 4. REASON FIELD (Exactly one sentence citing specific word)
        reason = f"Classified as {category} because description mentions '{matched_cat_word}'."
        if priority == "Urgent":
            reason = reason.rstrip(".") + f" and priority set to Urgent due to word '{matched_urgent_word}'."

    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Orchestrates batch classification of entries in a CSV file.
    Ensures output matching input row count as per skills.md.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    # Enforce schema consistency and row-count logic
                    classified = classify_complaint(row)
                except Exception:
                    # Fallback for malformed data
                    classified = {
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "A processing error occurred for this row data.",
                        "flag": "NEEDS_REVIEW"
                    }
                results.append(classified)
                
        output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fields)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Critical error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
