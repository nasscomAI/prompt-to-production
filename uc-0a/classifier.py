"""
UC-0A — Complaint Classifier
Build: Refined using agents.md and skills.md logic.
"""
import argparse
import csv
import os

# Configuration derived from agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "flooded", "waterlogging", "submerged"],
    "Streetlight": ["streetlight", "street light", "lamp", "flickering", "dark"],
    "Waste": ["garbage", "waste", "bins", "rubbish", "smell", "animal", "dumped"],
    "Noise": ["noise", "music", "loud"],
    "Road Damage": ["cracked", "sinking", "tiles", "broken", "pavement", "footpath"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "sun", "temperature"],
    "Drain Blockage": ["drain", "manhole", "gutter", "sewage"],
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on instructions in agents.md.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "Unknown")
    
    # 1. Determine Category
    assigned_category = "Other"
    reason_word = ""
    
    # Check for specific categories based on keywords
    found_categories = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in description:
                found_categories.append((cat, kw))
                break # Only need one keyword per category
    
    flag = ""
    if len(found_categories) == 1:
        assigned_category = found_categories[0][0]
        reason_word = found_categories[0][1]
    elif len(found_categories) > 1:
        # Ambiguous: multiple categories match
        assigned_category = "Other"
        flag = "NEEDS_REVIEW"
        reason_word = f"multiple categories detected ({', '.join([c[0] for c in found_categories])})"
    else:
        # Ambiguous: no categories match
        assigned_category = "Other"
        flag = "NEEDS_REVIEW"
        reason_word = "no specific category keywords identified"

    # 2. Determine Priority
    priority = "Standard"
    urgent_reason = ""
    for kw in URGENT_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            urgent_reason = kw
            break
            
    # 3. Construct Reason (Single sentence citing specific words)
    if assigned_category == "Other" and flag == "NEEDS_REVIEW":
        reason = f"Category set to Other because {reason_word}."
    else:
        reason = f"Classified as {assigned_category} because description mentions '{reason_word}'"
        if priority == "Urgent":
            reason += f" and triggered Urgent priority due to keyword '{urgent_reason}'."
        else:
            reason += "."

    return {
        "complaint_id": complaint_id,
        "category": assigned_category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    headers = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            headers = reader.fieldnames
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    # Merge original row with classification results
                    # Only add the new columns
                    output_row = row.copy()
                    output_row.update({
                        "category": classification["category"],
                        "priority": classification["priority"],
                        "reason": classification["reason"],
                        "flag": classification["flag"]
                    })
                    results.append(output_row)
                except Exception as e:
                    print(f"Skipping row {row.get('complaint_id')}: {e}")
                    
        if not results:
            print("No data processed.")
            return

        output_fieldnames = headers + ["category", "priority", "reason", "flag"]
        
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Fatal error during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
