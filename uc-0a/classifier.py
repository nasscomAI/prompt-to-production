import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using strict python string matching 
    based on the RICE prompt rules from agents.md. No external APIs allowed.
    """
    description = row.get("description", "").lower()
    
    # 1. Determine priority via severity keywords
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    matched_severity = next((kw for kw in severity_keywords if kw in description), None)
    
    # 2. Determine category via strict string matching 
    # Categories: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
    keyword_map = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "streetlight": "Streetlight",
        "lights out": "Streetlight",
        "dark": "Streetlight",
        "garbage": "Waste",
        "waste": "Waste",
        "dead animal": "Waste",
        "music": "Noise",
        "noise": "Noise",
        "road surface": "Road Damage",
        "tiles broken": "Road Damage",
        "crack": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage"
    }
    
    category = "Other"
    matched_cat_word = ""
    
    for kw, cat in keyword_map.items():
        if kw in description:
            category = cat
            matched_cat_word = kw
            break
            
    # 3. Apply constraints
    priority = "Standard"
    reason = ""
    flag = ""
    
    # Enforcement: "If the category cannot be determined from the description alone, or is genuinely ambiguous, 
    # output category: Other, flag: NEEDS_REVIEW and Priority: Low."
    if category == "Other":
        flag = "NEEDS_REVIEW"
        priority = "Low"
        reason = "Category could not be determined unambiguously from the description text."
    else:
        # Enforcement: "Priority must be Urgent if the description contains any of the following severity keywords..."
        if matched_severity:
            priority = "Urgent"
            reason = f"Classified as Urgent because description mentions '{matched_cat_word}' and severity keyword '{matched_severity}'."
        else:
            priority = "Standard"
            reason = f"Classified primarily because the description explicitly cites '{matched_cat_word}'."
            
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Reads an input CSV of complaints, applies classify_complaint to each row, 
    and writes the results to an output CSV. 
    """
    results = []
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    with open(input_path, mode='r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
            print("Error: Input CSV has no headers.")
            return
            
        fieldnames = list(reader.fieldnames)
        
        # Add output columns from skills.md
        for col in ["category", "priority", "reason", "flag"]:
            if col not in fieldnames:
                fieldnames.append(col)
                
        for row in reader:
            try:
                classification_result = classify_complaint(row)
                merged_row = {**row, **classification_result}
                results.append(merged_row)
            except Exception as e:
                print(f"Failed to process row ID {row.get('complaint_id', 'UNKNOWN')}: {e}")
                # Create an error record
                error_row = {**row}
                error_row["category"] = "Other"
                error_row["priority"] = "Low"
                error_row["reason"] = f"Processing Error: {e}"
                error_row["flag"] = "NEEDS_REVIEW"
                results.append(error_row)

    if not results:
        print("No rows processed.")
        return

    writer_fieldnames = list(results[0].keys())
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=writer_fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Successfully processed {len(results)} rows.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
