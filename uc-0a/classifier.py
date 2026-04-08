import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on agents.md rules.
    """
    description = row.get("description", "").lower()
    
    # 1. Initialize with Fallback Rules
    category = "Other"
    priority = "Low"
    flag = "NEEDS_REVIEW"
    reason = "Category could not be definitively matched from the description alone."
    
    # 2. Determine Category based on keywords
    if "pothole" in description:
        category = "Pothole"
        reason = "The description explicitly mentions a pothole."
        flag = ""
    elif "drain" in description:
        category = "Drain Blockage"
        reason = "The description mentions a blocked drain."
        flag = ""
    elif "flood" in description or "water" in description:
        category = "Flooding"
        reason = "The description mentions flooding or standing water."
        flag = ""
    elif "streetlight" in description or "lights" in description or "dark" in description:
        category = "Streetlight"
        reason = "The description mentions lighting issues."
        flag = ""
    elif "garbage" in description or "waste" in description or "animal" in description or "smell" in description:
        category = "Waste"
        reason = "The description mentions waste or garbage."
        flag = ""
    elif "music" in description or "noise" in description:
        category = "Noise"
        reason = "The description mentions noise or loud music."
        flag = ""
    elif "road" in description or "footpath" in description or "manhole" in description:
        category = "Road Damage"
        reason = "The description mentions damage to the road or footpath."
        flag = ""
    elif "heritage" in description:
        category = "Heritage Damage"
        reason = "The description mentions a heritage area or structure."
        flag = ""
    elif "heat" in description:
        category = "Heat Hazard"
        reason = "The description mentions extreme heat or temperature."
        flag = ""

    # 3. Determine Priority (Enforce Urgent Keywords)
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    matched_urgent_words = [word for word in urgent_keywords if word in description]
    
    if matched_urgent_words:
        priority = "Urgent"
        # Reason must cite specific words from description
        reason = f"Priority escalated to Urgent because description contains the word '{matched_urgent_words[0]}'."
    elif category != "Other":
        # If it's classified and has no urgent keywords, default to Medium
        priority = "Medium"
        
    # Append results to row
    result = row.copy()
    result["category"] = category
    result["priority"] = priority
    result["reason"] = reason
    result["flag"] = flag
    
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must handle errors gracefully per skills.md.
    """
    with open(input_path, 'r', encoding='utf-8') as fin:
        reader = csv.DictReader(fin)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        
        # Add the new fields
        for field in ["category", "priority", "reason", "flag"]:
            if field not in fieldnames:
                fieldnames.append(field)
                
        with open(output_path, 'w', encoding='utf-8', newline='') as fout:
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
            writer.writeheader()
            
            for row_idx, row in enumerate(reader, start=1):
                try:
                    classified_row = classify_complaint(row)
                    writer.writerow(classified_row)
                except Exception as e:
                    print(f"Error processing row {row_idx}: {e}")
                    # Guarantee output even if row fails
                    err_row = row.copy()
                    err_row["category"] = "Other"
                    err_row["priority"] = "Low"
                    err_row["reason"] = f"Error during processing: {str(e)}"
                    err_row["flag"] = "NEEDS_REVIEW"
                    writer.writerow(err_row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
