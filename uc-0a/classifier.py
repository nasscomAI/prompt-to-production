"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the taxonomy and rules in agents.md.
    """
    # Extract description, handling potential casing variations
    description = row.get("description", "") or row.get("Description", "")
    desc_lower = str(description).lower()
    complaint_id = row.get("complaint_id") or row.get("id") or "N/A"
    
    # 1. Category taxonomy and keyword mapping
    category_map = {
        "Pothole": ["pothole", "pit", "crater"],
        "Flooding": ["flood", "water", "overflow", "submerged", "rain"],
        "Streetlight": ["streetlight", "street light", "lamp", "dark", "no light"],
        "Waste": ["waste", "trash", "garbage", "rubbish", "litter", "dump"],
        "Noise": ["noise", "loud", "sound", "music", "barking"],
        "Road Damage": ["crack", "pavement", "asphalt", "broken road", "damage"],
        "Heritage Damage": ["heritage", "statue", "monument", "historic", "museum"],
        "Heat Hazard": ["heat", "hot", "sun", "temperature"],
        "Drain Blockage": ["drain", "sewage", "clog", "blockage", "pipe"]
    }
    
    matched_categories = []
    matched_words = []
    
    for cat, keywords in category_map.items():
        found_in_cat = [kw for kw in keywords if kw in desc_lower]
        if found_in_cat:
            matched_categories.append(cat)
            matched_words.extend(found_in_cat)
    
    # 2. Priority logic based on severity keywords from agents.md
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    urgent_words = [kw for kw in severity_keywords if kw in desc_lower]
    
    priority = "Urgent" if urgent_words else "Standard"
    
    # 3. Refusal and Ambiguity handling
    unique_cats = list(set(matched_categories))
    flag = ""
    
    if len(unique_cats) == 1:
        category = unique_cats[0]
    else:
        # If no match or multiple matches, categorize as Other and flag
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # 4. Reason construction citing source words
    all_matched = sorted(list(set(matched_words + urgent_words)))
    if not all_matched:
        reason = "Categorized as Other because no specific infrastructure or severity keywords were found in the description."
        flag = "NEEDS_REVIEW"
    else:
        cited = ", ".join(f"'{w}'" for w in all_matched)
        reason = f"Justified by keywords {cited} found in the report description."
        
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, apply classification logic per row, and write structured results to CSV.
    """
    import os
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                print("Error: Input CSV is empty or missing headers.")
                return
                
            for row in reader:
                # Handle empty rows or missing descriptions
                description = row.get("description") or row.get("Description")
                if not description:
                    results.append({
                        "complaint_id": row.get("complaint_id") or row.get("id") or "N/A",
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Missing or empty description field.",
                        "flag": "NEEDS_REVIEW"
                    })
                else:
                    results.append(classify_complaint(row))
                    
        if not results:
            print("No data found to process.")
            return

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"An unexpected error occurred during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
