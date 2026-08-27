"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = str(row.get("description", "")).strip()
    desc_lower = description.lower()
    complaint_id = row.get("complaint_id", "N/A")
    
    # 1. Determine Priority based on severity keywords
    priority = "Standard"
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_urgent = [kw for kw in urgent_keywords if kw in desc_lower]
    if found_urgent:
        priority = "Urgent"
    
    # 2. Determine Category based on keywords
    category = "Other"
    matched_kw = None
    
    mapping = {
        "pothole": "Pothole",
        "flooding": "Flooding",
        "flooded": "Flooding",
        "streetlight": "Streetlight",
        "light": "Streetlight",
        "waste": "Waste",
        "garbage": "Waste",
        "dumped": "Waste",
        "noise": "Noise",
        "loud": "Noise",
        "road damage": "Road Damage",
        "cracked": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "hot": "Heat Hazard",
        "drain": "Drain Blockage",
        "drainage": "Drain Blockage"
    }
    
    for kw, cat in mapping.items():
        if kw in desc_lower:
            category = cat
            matched_kw = kw
            break
            
    # 3. Construct Reason citing specific words
    if category != "Other":
        reason = f"Classified as {category} because description mentions '{matched_kw}'."
    else:
        reason = "Category could not be determined from the provided description."
        
    if priority == "Urgent":
        reason += f" Priority marked Urgent due to keyword: '{found_urgent[0]}'."
    elif not matched_kw and not found_urgent:
        priority = "Low" # Default for ambiguous/empty
        
    # 4. Handle Flag for ambiguity
    flag = "NEEDS_REVIEW" if category == "Other" or not description else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Handle null/empty rows
                    if not row or not any(row.values()):
                        continue
                        
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error processing row: {e}")
                    # Continue processing other rows
                    
        if not results:
            print("No data processed.")
            return

        # Write results to CSV
        keys = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
            
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
    except Exception as e:
        print(f"Batch processing failed: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

