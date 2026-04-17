"""
UC-0A — Complaint Classifier
Implemented using RICE framework, agents.md, and skills.md.
"""
import argparse
import csv

# Official Classification Schema Constants
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
PRIORITIES = ["Urgent", "Standard", "Low"]
URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

# Category Keyword Mapping for rule-based matching
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "waterlog", "inundated", "stranded", "rain"],
    "Streetlight": ["streetlight", "dark", "light", "lamp"],
    "Waste": ["garbage", "waste", "bin", "dump", "smell", "animal"],
    "Noise": ["noise", "sound", "loud", "music"],
    "Road Damage": ["cracked", "sinking", "surface", "damage", "tiles"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "hot", "sun"],
    "Drain Blockage": ["drain", "blocked", "sewage", "manhole"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the official schema and enforcement rules.
    """
    description = row.get("description", "").lower().strip()
    complaint_id = row.get("complaint_id", "Unknown")
    
    # Rule: If complaint is empty or unclear -> Unknown
    if not description or len(description) < 5:
        return {
            "complaint_id": complaint_id,
            "category": "Unknown",
            "priority": "Unknown",
            "reason": "Description is empty or too short to classify.",
            "flag": "NEEDS_REVIEW"
        }

    # Rule: Out of Scope check
    out_of_scope_keywords = ["recipe", "movie", "game", "joke", "weather forecast"]
    if any(k in description for k in out_of_scope_keywords):
        return {
            "complaint_id": complaint_id,
            "category": "Out of Scope",
            "priority": "Out of Scope",
            "reason": "Content appears unrelated to city services.",
            "flag": "NEEDS_REVIEW"
        }

    # Identify Category
    category = "Other"
    matched_cat_keywords = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for k in keywords:
            if k in description:
                category = cat
                matched_cat_keywords.append(k)
                break
        if category != "Other":
            break

    # Identify Priority
    priority = "Standard"
    matched_priority_keywords = []
    for k in URGENT_KEYWORDS:
        if k in description:
            priority = "Urgent"
            matched_priority_keywords.append(k)
            break
            
    # Reason generation: Must cite specific words
    reason_parts = []
    if category != "Other" and matched_cat_keywords:
        reason_parts.append(f"categorized as {category} due to mentions of '{matched_cat_keywords[0]}'")
    else:
        reason_parts.append("categorized as Other as no specific keywords matched")
        
    if priority == "Urgent" and matched_priority_keywords:
        reason_parts.append(f"assigned Urgent priority due to keyword '{matched_priority_keywords[0]}'")
    
    reason = " and ".join(reason_parts).capitalize() + "."

    # Flag logic
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write output CSV.
    """
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                classification = classify_complaint(row)
                results.append(classification)
                
        if not results:
            print("No data found in input file.")
            return

        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
