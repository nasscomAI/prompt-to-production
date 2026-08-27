"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

# Official Taxonomy from agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity rules from agents.md
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(description: str) -> dict:
    """
    Classifies a single citizen complaint based on description.
    Enforces rules from agents.md.
    """
    desc_lower = description.lower()
    
    # 1. Determine Category (Simplified Keyword Match)
    category = "Other"
    reason_snippet = ""
    
    # Mapping keywords (using stems where possible) to categories
    category_map = {
        "Pothole": ["pothole", "pit"],
        "Flooding": ["flood", "waterlog", "inundat"],
        "Streetlight": ["streetlight", "street light", "lamp", "unlit", "darkness", "lights out"],
        "Waste": ["garbage", "bin", "trash", "waste", "dump", "smell", "dead animal", "litter"],
        "Noise": ["noise", "music", "loud", "audible"],
        "Heritage Damage": ["heritage", "ancient", "monument", "step well", "archaeologic"],
        "Heat Hazard": ["heat", "sun", "shade", "melt", "temp", "°c", "burn", "hot"],
        "Drain Blockage": ["drain", "manhole", "sewer", "gutter"],
        "Road Damage": ["road surface", "crack", "sink", "footpath", "tile", "broken", "subsidence", "paving", "pavement"]
    }

    found_cat = False
    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw in desc_lower:
                category = cat
                reason_snippet = kw
                found_cat = True
                break
        if found_cat: break

    # 2. Determine Priority
    priority = "Standard"
    urgent_keywords_to_check = [
        "injury", "injured", "child", "school", "hospital", "ambulance", 
        "fire", "hazard", "fell", "fall", "collapse"
    ]
    urgent_found = []
    for kw in urgent_keywords_to_check:
        if kw in desc_lower:
            urgent_found.append(kw)
    
    if urgent_found:
        priority = "Urgent"
        urgent_reason = ", ".join(urgent_found)
        if reason_snippet:
            reason_snippet = f"{reason_snippet} (Category) and {urgent_reason} (Priority)"
        else:
            reason_snippet = urgent_reason
    elif category == "Other":
        priority = "Low"

    # 3. Handle Flag and Final Category
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
    
    # 4. Construct Reason
    if not found_cat and not urgent_found:
        reason = "No specific category or severity keywords identified in description."
    else:
        reason = f"Classification based on mentions of '{reason_snippet}' in the description."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Reads an input CSV, classifies each row, and writes to an output CSV.
    Handles errors and missing fields gracefully.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            # Fix lint: ensure fieldnames is a list even if reader.fieldnames is None
            original_fieldnames = list(reader.fieldnames or [])
            fieldnames = original_fieldnames + ["category", "priority", "reason", "flag"]
            
            for row in reader:
                description = row.get("description", "")
                if not description or not description.strip():
                    # Skill: If input is empty, return Other + NEEDS_REVIEW
                    classification = {
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Empty description provided.",
                        "flag": "NEEDS_REVIEW"
                    }
                else:
                    try:
                        classification = classify_complaint(description)
                    except Exception as e:
                        # Skill: Log error and continue
                        print(f"Error processing row {row.get('complaint_id', 'Unknown')}: {e}")
                        classification = {
                            "category": "Other",
                            "priority": "Low",
                            "reason": f"Processing error: {str(e)}",
                            "flag": "NEEDS_REVIEW"
                        }
                
                # Merge classification with original row
                row.update(classification)
                results.append(row)

        # Write to output file
        if results:
            with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Successfully processed {len(results)} rows.")
        else:
            print("No rows found to process.")

    except Exception as e:
        print(f"Fatal error during batch processing: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
