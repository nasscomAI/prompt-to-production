"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # Category mapping based on keywords
    category_map = {
        "pothole": "Pothole",
        "flooding": "Flooding",
        "streetlight": "Streetlight",
        "waste": "Waste",
        "garbage": "Waste",
        "noise": "Noise",
        "road damage": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage",
        "blockage": "Drain Blockage"
    }
    
    category = "Other"
    for kw, cat in category_map.items():
        if kw in description:
            category = cat
            break
            
    # Priority escalation keywords
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    priority = "Standard"
    triggered_keywords = [kw for kw in severity_keywords if kw in description]
    if triggered_keywords:
        priority = "Urgent"
    elif "noise" in description or "waste" in description:
        priority = "Low"
        
    # Reason generation
    if triggered_keywords:
        reason = f"Priority set to Urgent because description contains safety-critical words: {', '.join(triggered_keywords)}."
    elif category != "Other":
        reason = f"Classified as {category} based on the mention of related issues in the description."
    else:
        reason = "Classified as Other due to lack of specific category keywords in the description."
        
    # Ambiguity flag
    flag = ""
    if category == "Other" or (priority == "Urgent" and not triggered_keywords):
        flag = "NEEDS_REVIEW"
        
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
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
            
            # Remove existing category/priority/priority_flag if present to avoid duplicates
            fieldnames = [f for f in fieldnames if f not in ["priority_flag"]]
            # Note: DictReader gives us the row with original keys. 
            # We will merge the classification results.
            
            results = []
            for row in reader:
                classification = classify_complaint(row)
                # Merge classification into row
                row.update(classification)
                # Cleanup stripped columns if they were present in input but needs stripping
                if "category" in row and row["category"] == "": del row["category"] # Should be overwritten anyway
                results.append(row)
                
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            # Re-order fieldnames to ensure desired columns are present
            final_fieldnames = [f for f in fieldnames if f not in ["category", "priority", "reason", "flag"]] + ["category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=final_fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(results)
            
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
