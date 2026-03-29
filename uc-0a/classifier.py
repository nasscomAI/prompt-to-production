"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on keywords.
    """
    desc = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "Unknown")
    
    # Define category keywords (Order matters!)
    categories = {
        "Heritage Damage": ["heritage"],
        "Drain Blockage": ["drain", "blocked"],
        "Heat Hazard": ["heat", "hot"],
        "Pothole": ["pothole"],
        "Road Damage": ["cracked", "sinking", "manhole", "road surface", "footpath", "tiles", "tiles broken"],
        "Streetlight": ["light", "streetlight"],
        "Flooding": ["flood", "water"],
        "Waste": ["garbage", "waste", "bins", "animal"],
        "Noise": ["noise", "music", "loud"]
    }
    
    selected_category = "Other"
    found_words = []
    
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in desc:
                selected_category = cat
                found_words.append(kw)
                break
        if selected_category != "Other":
            break
            
    # Priority Keywords
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    for kw in urgent_keywords:
        if kw in desc:
            priority = "Urgent"
            found_words.append(kw)
            break
            
    # If no category found but urgent keyword found, priority is still Urgent
    # Wait, README says Urgent if severity keywords present.
    
    reason = f"Cites specific words '{', '.join(set(found_words))}' in the description." if found_words else "No specific keywords found."
    
    flag = ""
    if selected_category == "Other" or not desc:
        flag = "NEEDS_REVIEW"
        
    return {
        "complaint_id": complaint_id,
        "category": selected_category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not any(row.values()): # Skip empty rows
                    continue
                results.append(classify_complaint(row))
                
        if not results:
            print(f"Warning: No valid rows found in {input_path}")
            return

        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Error processing {input_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
