"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

# --- Constants from agents.md and README.md ---
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_MAP = {
    "Pothole": ["pothole", "crater", "sinkhole"],
    "Flooding": ["flood", "waterlogging", "submerged", "underpass", "knee-deep", "inaccessible"],
    "Streetlight": ["streetlight", "dark", "lighting", "lamp", "flicking"],
    "Waste": ["garbage", "trash", "waste", "dump", "litter", "animal", "smell"],
    "Noise": ["noise", "loud", "music", "midnight", "disturbance"],
    "Road Damage": ["cracked", "sinking", "surface", "broken", "footpath", "manhole", "bridge"],
    "Heritage Damage": ["heritage", "monument", "ancient", "statue"],
    "Heat Hazard": ["heat", "sun", "extreme temperature", "exhaustion"],
    "Drain Blockage": ["drain", "sewage", "clogged", "overflowing", "gutter"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row with high-fidelity logic for priority and categorization.
    """
    description = (row.get("description") or "").strip().lower()
    
    # 1. Determine Priority
    # Rule: Urgent if severity keywords present. Otherwise, categorize as Standard/Low.
    priority = "Standard"
    is_urgent = False
    for kw in SEVERITY_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            is_urgent = True
            break
            
    # 2. Determine Category
    category = "Other"
    found_keyword = None
    
    for cat, keywords in CATEGORY_MAP.items():
        for kw in keywords:
            if kw in description:
                category = cat
                found_keyword = kw
                break
        if category != "Other":
            break
            
    # 3. Handle Ambiguity & Defaulting
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    # Refine non-urgent priority: Assign 'Low' for specific categories
    if not is_urgent:
        if category in ["Noise", "Waste"]:
            priority = "Low"
        else:
            priority = "Standard"
        
    # 4. Generate Reason (Must be one sentence and cite specific words)
    if found_keyword:
        reason = f"The compliant is categorized as {category} as the description explicitly mentions '{found_keyword}'."
    elif is_urgent:
        reason = "The complaint is marked as Urgent due to safety-critical keywords in the description despite an ambiguous category."
    else:
        reason = "The category is set to Other because the description lacks specific classification keywords."
        
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
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
            
            with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in reader:
                    classification = classify_complaint(row)
                    row.update(classification)
                    writer.writerow(row)
                    
    except Exception as e:
        print(f"Error processing CSV: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
