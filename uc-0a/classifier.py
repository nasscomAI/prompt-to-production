"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

# Categories from schema
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # 1. Determine category and find the trigger word
    category = "Other"
    reason_word = None
    
    word_mappings = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "drain blocked": "Drain Blockage",
        "light": "Streetlight",
        "sparking": "Streetlight",
        "garbage": "Waste",
        "waste": "Waste",
        "animal": "Waste",
        "noise": "Noise",
        "music": "Noise",
        "crack": "Road Damage",
        "manhole": "Road Damage",
        "tiles": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard"
    }

    for key, cat in word_mappings.items():
        if key in description:
            category = cat
            reason_word = key
            break
            
    # 2. Determine Priority based on exact severity keywords
    priority = "Standard"
    urgent_word = None
    
    for word in SEVERITY_KEYWORDS:
        if word in description:
            priority = "Urgent"
            urgent_word = word
            break
            
    # 3. Construct reason & flag
    if reason_word:
        reason = f"Classified as {category} because description mentions '{reason_word}'."
    else:
        reason = "Could not map to specific category based on description."
        
    if urgent_word:
        reason += f" Priority upgraded to Urgent due to keyword '{urgent_word}'."
        
    flag = "NEEDS_REVIEW" if category == "Other" else ""
        
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason.strip(),
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
            
        results = []
        for row in rows:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                # Must not crash on bad rows
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error classifying: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Error processing batch: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
