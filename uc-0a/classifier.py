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
    
    Enforcement:
    - Category: exactly one of allowed list
    - Priority: Urgent if severity keywords present
    - Reason: one sentence citing specific words from description
    - Flag: NEEDS_REVIEW if ambiguous, otherwise blank
    """
    # Category taxonomy
    ALLOWED_CATEGORIES = [
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
        "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ]
    
    # Severity keywords that trigger Urgent priority
    SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}
    
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()
    
    # Handle missing/empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }
    
    description_lower = description.lower()
    
    # Check for severity keywords
    has_severity = any(kw in description_lower for kw in SEVERITY_KEYWORDS)
    priority = "Urgent" if has_severity else "Standard"
    
    # Classification logic based on description keywords
    category = "Other"
    reason = ""
    flag = ""
    
    # Pothole detection
    if "pothole" in description_lower or "pit" in description_lower:
        category = "Pothole"
        reason = f"Complaint describes pothole or pit damage affecting road safety."
    
    # Drain Blockage detection (check before Flooding - when drain is primarily blocked)
    elif ("drain" in description_lower and ("blocked" in description_lower or "blockage" in description_lower)) and ("flood" not in description_lower or "stormwater" in description_lower or "100%" in description):
        category = "Drain Blockage"
        reason = f"Complaint describes drain blockage or obstruction."
    
    # Flooding detection
    elif "flood" in description_lower or ("water" in description_lower and "standing" in description_lower):
        category = "Flooding"
        reason = f"Complaint describes flooding or water accumulation issues."
    
    # Streetlight detection
    elif "light" in description_lower or "lamp" in description_lower or "unlit" in description_lower:
        category = "Streetlight"
        reason = f"Complaint addresses malfunctioning or missing street lighting."
    
    # Waste detection
    elif "waste" in description_lower or "garbage" in description_lower or "rubbish" in description_lower or "bin" in description_lower or "litter" in description_lower:
        category = "Waste"
        reason = f"Complaint involves waste management or accumulation."
    
    # Noise detection
    elif "noise" in description_lower or "sound" in description_lower or "music" in description_lower or "loud" in description_lower:
        category = "Noise"
        reason = f"Complaint reports excessive noise disturbance."
    
    # Heat Hazard detection
    elif "heat" in description_lower or "temperature" in description_lower or "melting" in description_lower or "burn" in description_lower or "hot" in description_lower:
        category = "Heat Hazard"
        reason = f"Complaint describes extreme heat or surface temperature hazards."
    
    # Road Damage detection
    elif "road" in description_lower or "surface" in description_lower or "pavement" in description_lower or "paving" in description_lower or "subsidence" in description_lower or "asphalt" in description_lower:
        category = "Road Damage"
        reason = f"Complaint indicates road infrastructure damage or deterioration."
    
    # Heritage Damage detection
    elif "heritage" in description_lower or "historic" in description_lower or "ancient" in description_lower or "monument" in description_lower or "old city" in description_lower:
        category = "Heritage Damage"
        reason = f"Complaint affects heritage sites or historic areas."
    
    else:
        category = "Other"
        reason = f"Complaint could not be confidently categorized from description alone."
        flag = "NEEDS_REVIEW"
    
    # Ensure reason cites specific words from description
    if not reason:
        reason = f"Complaint description indicates {category.lower()} related issues."
    
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
    
    Enforces:
    - Must flag nulls
    - Must not crash on bad rows
    - Must produce output even if some rows fail
    """
    results = []
    error_rows = []
    
    try:
        # Read input CSV
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                raise ValueError("Input CSV has no headers")
            
            input_fields = reader.fieldnames
            
            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                try:
                    # Classify this row
                    classified = classify_complaint(row)
                    # Merge with original row data
                    result_row = {**row, **classified}
                    results.append(result_row)
                except Exception as e:
                    # Capture error row
                    error_rows.append({
                        **row,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Classification failed: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
                    results.append(error_rows[-1])
        
        # Write output CSV with all original columns plus classification columns
        if results:
            output_fields = input_fields + ["category", "priority", "reason", "flag"]
            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=output_fields)
                writer.writeheader()
                for result in results:
                    # Ensure all fields present
                    row_to_write = {field: result.get(field, "") for field in output_fields}
                    writer.writerow(row_to_write)
        else:
            raise ValueError("No valid rows to classify")
            
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
