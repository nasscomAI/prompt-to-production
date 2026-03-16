"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to the rules in agents.md.
    """
    description = row.get("description", "").lower()
    
    # Allowed categories and their matching keywords
    category_map = {
        "Pothole": ["pothole", "crater", "road cavity"],
        "Flooding": ["flood", "waterlogging", "inundated"],
        "Streetlight": ["streetlight", "lamp", "dark street"],
        "Waste": ["waste", "garbage", "trash", "rubbish", "dump"],
        "Noise": ["noise", "loud", "music", "barking"],
        "Road Damage": ["crack", "broken road", "uneven surface"],
        "Heritage Damage": ["heritage", "monument", "statue"],
        "Heat Hazard": ["heat", "sun", "shade needed", "temperature"],
        "Drain Blockage": ["drain", "clogged", "sewer", "blockage"]
    }
    
    severity_keywords = [
        "injury", "child", "school", "hospital", "ambulance", 
        "fire", "hazard", "fell", "collapse"
    ]
    
    # 1. Determine Category
    matched_categories = []
    matched_category_keywords = []
    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw in description:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                matched_category_keywords.append(kw)

    category = "Other"
    flag = ""
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
    else:
        # Ambiguous or no match
        flag = "NEEDS_REVIEW"
        
    # 2. Determine Priority
    matched_severity_keywords = [kw for kw in severity_keywords if kw in description]
    if matched_severity_keywords:
        priority = "Urgent"
    else:
        priority = "Standard"  # Defaulting, though "Low" is also valid per rules
        
    # 3. Compile Reason
    reason = "No specific keywords found."
    all_matched_keywords = list(set(matched_category_keywords + matched_severity_keywords))
    
    if all_matched_keywords:
        reason = f"Classification is based on the presence of words: {', '.join(all_matched_keywords)}."
        
    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if not fieldnames:
                print(f"Error: Could not read column headers from {input_path}")
                return
                
            # Define output headers
            output_headers = list(fieldnames)
            for col in ["category", "priority", "reason", "flag"]:
                if col not in output_headers:
                    output_headers.append(col)

            rows_to_write = []
            for i, row in enumerate(reader):
                try:
                    result = classify_complaint(row)
                    row.update(result)
                    rows_to_write.append(row)
                except Exception as e:
                    print(f"Skipping row {i} due to error: {e}")
                    
        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_headers)
            writer.writeheader()
            writer.writerows(rows_to_write)
            
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"An unexpected error occurred during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
