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
    
    Enforcement rules:
    - Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
    - Priority is Urgent if description contains: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
    - Reason must be one sentence citing specific words from the description
    - Flag is NEEDS_REVIEW if category is ambiguous, otherwise empty string
    """
    ALLOWED_CATEGORIES = {
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
        "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    }
    SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}
    
    description = row.get("description", "").lower()
    
    # Determine if priority should be Urgent based on severity keywords
    is_urgent = any(keyword in description for keyword in SEVERITY_KEYWORDS)
    priority = "Urgent" if is_urgent else "Standard"
    
    # Classify complaint into category based on keywords found in description
    category = "Other"
    reason = ""
    flag = ""
    
    description_lower = description.lower()
    
    # Simple keyword-based classification (to be enhanced with AI)
    if any(word in description_lower for word in ["pothole", "potholed", "hole", "road hole"]):
        category = "Pothole"
        reason = "Description contains keywords related to potholes."
    elif any(word in description_lower for word in ["flood", "flooding", "water", "waterlogged", "submerged"]):
        category = "Flooding"
        reason = "Description contains keywords related to flooding."
    elif any(word in description_lower for word in ["streetlight", "lamp", "light post", "street lamp", "broken light"]):
        category = "Streetlight"
        reason = "Description contains keywords related to streetlights."
    elif any(word in description_lower for word in ["waste", "garbage", "trash", "litter", "rubbish"]):
        category = "Waste"
        reason = "Description contains keywords related to waste."
    elif any(word in description_lower for word in ["noise", "sound", "loud", "loudness"]):
        category = "Noise"
        reason = "Description contains keywords related to noise."
    elif any(word in description_lower for word in ["road damage", "damaged road", "road crack", "cracked"]):
        category = "Road Damage"
        reason = "Description contains keywords related to road damage."
    elif any(word in description_lower for word in ["heritage", "historic", "monument", "historical"]):
        category = "Heritage Damage"
        reason = "Description contains keywords related to heritage sites."
    elif any(word in description_lower for word in ["heat", "heat hazard", "extreme heat", "temperature"]):
        category = "Heat Hazard"
        reason = "Description contains keywords related to heat hazards."
    elif any(word in description_lower for word in ["drain", "drainage", "blocked drain", "blockage"]):
        category = "Drain Blockage"
        reason = "Description contains keywords related to drain blockage."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Category could not be confidently determined from the description."
    
    if reason and category != "Other":
        reason = f"{reason} Contains: {', '.join(word for word in description.split() if any(c.isalpha() for c in word))[:50]}..."
    
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Features:
    - Reads all rows from input CSV
    - Applies classify_complaint to each row
    - Handles errors gracefully without crashing
    - Writes output CSV with classification results
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            if reader.fieldnames is None or 'description' not in reader.fieldnames:
                print(f"Error: Input CSV must contain a 'description' column.")
                return
            
            rows = list(reader)
            
        # Classify all rows
        classified_rows = []
        for idx, row in enumerate(rows):
            try:
                if not row.get('description', '').strip():
                    print(f"Warning: Row {idx + 1} has empty description, flagging for review.")
                    classified = {
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Empty description provided.",
                        "flag": "NEEDS_REVIEW"
                    }
                else:
                    classified = classify_complaint(row)
                classified_rows.append(classified)
            except Exception as e:
                print(f"Error classifying row {idx + 1}: {str(e)}")
                classified_rows.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error during classification: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
        
        # Write output CSV
        output_fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
            writer.writeheader()
            writer.writerows(classified_rows)
        
        print(f"Successfully classified {len(classified_rows)} complaints.")
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
    except Exception as e:
        print(f"Error during batch classification: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
