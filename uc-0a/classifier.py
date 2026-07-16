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
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Empty description provided.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    
    # Priority check: Urgent if severity keywords present
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    is_urgent = any(kw in desc_lower for kw in severity_keywords)
    priority = "Urgent" if is_urgent else "Standard"
    
    # Category check
    category_keywords = {
        "Pothole": ["pothole", "potholes"],
        "Flooding": ["flood", "flooded", "flooding", "floods", "rainwater"],
        "Streetlight": ["streetlight", "streetlights", "unlit", "darkness", "lights out", "lamp post"],
        "Waste": ["garbage", "waste", "debris", "dead animal", "litter"],
        "Noise": ["music", "noise", "drilling", "idling", "engines on", "amplifiers", "wedding band"],
        "Road Damage": ["cracked", "sinking", "collapsed", "subsidence", "subsided", "footpath", "tarmac", "paving", "broken tiles", "broken bench"],
        "Heritage Damage": ["heritage", "historic", "ancient", "museum", "step well"],
        "Heat Hazard": ["melting", "heatwave", "temperature", "heat", "bubbling", "burns on contact", "full sun"],
        "Drain Blockage": ["drain", "drainage", "manhole"]
    }
    
    matched_categories = []
    for cat, kws in category_keywords.items():
        if any(kw in desc_lower for kw in kws):
            matched_categories.append(cat)
            
    # Ambiguity check for "manhole cover missing" (could be Road Damage or Drain Blockage)
    if "manhole" in desc_lower and "cover" in desc_lower:
        if "Road Damage" not in matched_categories:
            matched_categories.append("Road Damage")
            
    # Ambiguity check for "gas leak" / "gas pipeline"
    if "gas leak" in desc_lower or "gas pipeline" in desc_lower:
        if "Road Damage" not in matched_categories:
            matched_categories.append("Road Damage")
            
    flag = ""
    category = "Other"
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Generate one-sentence reason
    # Get the first sentence from description
    first_sentence = description.split('.')[0].strip()
    if first_sentence.endswith('.'):
        first_sentence = first_sentence[:-1]
    # Clean quotes
    first_sentence = first_sentence.replace("'", "").replace('"', '')
    
    if flag == "NEEDS_REVIEW":
        if len(matched_categories) > 1:
            reason = f"Flagged for review because the description '{first_sentence}' matches multiple categories: {', '.join(matched_categories)}."
        else:
            reason = f"Flagged for review because the description '{first_sentence}' does not clearly match any predefined category."
    else:
        reason = f"Classified under {category} because the description cites '{first_sentence}'."
        
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
    """
    results = []
    
    try:
        with open(input_path, mode="r", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                raise ValueError("CSV file has no header or columns.")
            
            for row in reader:
                try:
                    cleaned_row = {k.strip() if k else "": v.strip() if v else "" for k, v in row.items()}
                    classified = classify_complaint(cleaned_row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error classifying row {row.get('complaint_id', 'unknown')}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", "").strip(),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Failed to classify due to error: {e}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Critical error reading input path {input_path}: {e}")
        raise e
        
    try:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except Exception as e:
        print(f"Critical error writing output path {output_path}: {e}")
        raise e


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
