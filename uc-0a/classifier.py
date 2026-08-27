"""
UC-0A — Complaint Classifier
Starter file. Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
import os

# --- Constants from agents.md ---
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater", "sinkhole", "road hole"],
    "Flooding": ["flood", "waterlog", "submerge", "inundat"],
    "Streetlight": ["streetlight", "street light", "lamp", "darkness", "dark out"],
    "Waste": ["waste", "garbage", "trash", "dump", "litter", "refuse"],
    "Noise": ["noise", "loud", "sound", "volume", "music"],
    "Road Damage": ["road crack", "pavement", "asphalt", "broken road", "surface damage"],
    "Heritage Damage": ["heritage", "monument", "statue", "historical", "temple", "shrine"],
    "Heat Hazard": ["heat", "hot", "shade", "sunstroke", "burn", "temperature"],
    "Drain Blockage": ["drain", "sewage", "gutter", "clog", "sewer"]
}

def detect_severity(description: str) -> bool:
    """
    Skill: detect_severity
    Granular check for safety-critical keywords to ensure mandatory escalation.
    """
    desc_lower = description.lower()
    for word in SEVERITY_KEYWORDS:
        if word in desc_lower:
            return True
    return False

def map_category(description: str) -> str:
    """
    Heuristic to map description to strict taxonomy.
    """
    desc_lower = description.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            return cat
    return "Other"

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").strip()
    
    # Handle empty/vague scenario
    if not description or len(description) < 10:
        return {
            "complaint_id": row.get("complaint_id"),
            "category": "Other",
            "priority": "Low",
            "reason": "Description is too generic or missing to classify effectively.",
            "flag": "NEEDS_REVIEW"
        }
    
    # 1. Determine Priority
    is_urgent = detect_severity(description)
    priority = "Urgent" if is_urgent else "Standard" # Defaulting to Standard if not Urgent
    
    # Heuristic for 'Low' priority (e.g., if it's aesthetic or very minor)
    if not is_urgent and any(kw in description.lower() for kw in ["aesthetic", "paint", "minor", "clean"]):
        priority = "Low"
    
    # 2. Determine Category
    category = map_category(description)
    
    # 3. Handle Ambiguity (Flagging)
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
    
    # 4. Generate Reason (One sentence citing words)
    # Simple logic: use the first sentence or part of it and quote a key word found.
    found_keywords = []
    for word in SEVERITY_KEYWORDS + sum(CATEGORY_KEYWORDS.values(), []):
        if re.search(rf"\b{re.escape(word)}\b", description.lower()):
            found_keywords.append(word)
    
    citation = ""
    if found_keywords:
        citation = f" based on words: '{found_keywords[0]}'"
    
    reason = f"Classified as {category} with {priority} priority{citation} found in the description."

    return {
        "complaint_id": row.get("complaint_id"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if not fieldnames or 'description' not in fieldnames:
                print(f"Error: Input file missing 'description' column.")
                return

            results = []
            for row in reader:
                try:
                    result = classify_complaint(row)
                    # Merge with original row for full output
                    row.update(result)
                    results.append(row)
                except Exception as e:
                    print(f"Warning: Failed to process row {row.get('complaint_id')}: {e}")
            
            # Write output
            if results:
                # Add the new columns to the output file headers
                new_headers = list(results[0].keys())
                with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=new_headers)
                    writer.writeheader()
                    writer.writerows(results)
                print(f"Successfully processed {len(results)} rows.")
            else:
                print("No rows processed.")

    except Exception as e:
        print(f"Critical Error during batch processing: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
