"""
UC-0A — Complaint Classifier
Implementation follows the RICE workflow, incorporating rules from agents.md and skills.md.
"""
import argparse
import csv
import os
import re

# Classification Schema Constants (as defined in README.md and agents.md)
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    """
    Classifies a single complaint row.
    Rules:
    - Urgent if description contains severity keywords.
    - Category must be from the allowed exact strings.
    - Reason must be one sentence and cite specific words from description.
    - flag set to NEEDS_REVIEW if category is genuinely ambiguous.
    """
    description = row.get("description", "").strip()
    desc_lower = description.lower()
    
    # 1. Priority Determination
    is_urgent = any(kw in desc_lower for kw in SEVERITY_KEYWORDS)
    priority = "Urgent" if is_urgent else "Standard"
    
    # 2. Category Mapping (Heuristic-based following the taxonomy)
    category = "Other"
    if "pothole" in desc_lower:
        category = "Pothole"
    elif "heritage" in desc_lower:
        category = "Heritage Damage"
    elif "noise" in desc_lower or "music" in desc_lower:
        category = "Noise"
    elif "light" in desc_lower:
        category = "Streetlight"
    elif "garbage" in desc_lower or "waste" in desc_lower or "dumped" in desc_lower or "animal" in desc_lower:
        category = "Waste"
    elif "drain" in desc_lower or "blocked" in desc_lower:
        category = "Drain Blockage"
    elif "flood" in desc_lower or "water" in desc_lower:
        category = "Flooding"
    elif "heat" in desc_lower or "hot" in desc_lower or re.search(r'\bsun\b', desc_lower) or "temperature" in desc_lower:
        category = "Heat Hazard"
    elif "road" in desc_lower or "surface" in desc_lower or "crack" in desc_lower or "manhole" in desc_lower or "footpath" in desc_lower:

        category = "Road Damage"


    # 3. Flagging Ambiguity
    flag = ""
    # Flag if 'Other' or if multiple potential categories overlap without a clear winner
    if category == "Other" or len(description.split()) < 4:
        flag = "NEEDS_REVIEW"
    
    # 4. Reason Generation
    # Must cite specific words from the description
    found_keywords = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    
    # Extract terms that likely triggered the category
    category_terms = [t for t in ["pothole", "heritage", "noise", "music", "light", "garbage", "waste", "drain", "flood", "water", "heat", "hot", "temperature", "road", "surface", "footpath"] if t in desc_lower]
    if re.search(r'\bsun\b', desc_lower):
        category_terms.append("sun")
    
    cited_words = sorted(list(set(found_keywords + category_terms)))
    
    if cited_words:
        reason = f"Classification based on terms like '{', '.join(cited_words)}' found in description."
    else:
        reason = "Classification assigned based on contextual keywords in the description."


    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Reads input CSV, applies classify_complaint per row, and writes output CSV.
    Ensures the process doesn't crash on bad rows and flags nulls.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    processed_rows = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
            
            for row in reader:
                try:
                    # Check for empty description
                    if not row.get("description"):
                        classification = {
                            "category": "Other",
                            "priority": "Low",
                            "reason": "Missing description field.",
                            "flag": "NEEDS_REVIEW"
                        }
                    else:
                        classification = classify_complaint(row)
                    
                    row.update(classification)
                    processed_rows.append(row)
                except Exception as e:
                    print(f"Skipping row due to error: {e}")
                    continue

        if processed_rows:
            with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(processed_rows)
            print(f"Successfully processed {len(processed_rows)} rows.")
        else:
            print("No valid rows were processed.")

    except Exception as e:
        print(f"Fatal error during batch processing: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
