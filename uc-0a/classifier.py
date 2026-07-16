"""
UC-0A — Complaint Classifier
Implementation file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "")
    
    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing description field.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = desc.lower()
    
    # Define category keywords mapping
    category_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "waterlogging", "water-logging"],
        "Streetlight": ["streetlight", "street light", "lights out", "unlit", "lamp post", "darkness"],
        "Waste": ["garbage", "waste", "rubbish", "trash", "dumped", "dead animal", "bins", "dead tree", "debris"],
        "Noise": ["noise", "music", "loud", "drilling", "amplifier"],
        "Heritage Damage": ["heritage", "historic", "ancient"],
        "Heat Hazard": ["heat", "temperature", "melting", "sun", "hot"],
        "Drain Blockage": ["drain", "sewer", "manhole", "blockage"],
        "Road Damage": ["road surface", "footpath", "cracked", "pavement", "sinking", "tiles", "tarmac", "paving", "subside", "subsidence", "buckled"]
    }
    
    matched_categories = []
    matched_keywords = {}
    
    for cat, keywords in category_keywords.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_categories.append(cat)
                # Keep track of the first keyword that matched for reason citation
                if cat not in matched_keywords:
                    start_idx = desc_lower.find(kw)
                    original_word = desc[start_idx:start_idx+len(kw)]
                    matched_keywords[cat] = original_word
                break  # match next category
                
    # Determine the category and flag
    flag = ""
    category = "Other"
    
    if len(matched_categories) > 1:
        # Resolve common overlap: Pothole is a specific type of Road Damage
        if "Pothole" in matched_categories and "Road Damage" in matched_categories:
            category = "Pothole"
            if len(matched_categories) > 2:
                flag = "NEEDS_REVIEW"
        else:
            category = matched_categories[0]
            flag = "NEEDS_REVIEW"
    elif len(matched_categories) == 1:
        category = matched_categories[0]
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Severity keywords that must trigger Urgent
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    is_urgent = False
    matched_severity = None
    
    for kw in severity_keywords:
        if kw in desc_lower:
            is_urgent = True
            start_idx = desc_lower.find(kw)
            matched_severity = desc[start_idx:start_idx+len(kw)]
            break
            
    priority = "Urgent" if is_urgent else "Standard"
    
    # Generate citation-based reason sentence
    citations = []
    if category != "Other" and category in matched_keywords:
        citations.append(f"'{matched_keywords[category]}'")
    if is_urgent and matched_severity:
        citations.append(f"'{matched_severity}'")
        
    if citations:
        reason = f"Classified as {category} ({priority}) citing {', '.join(citations)} from the description."
    else:
        # Fallback citation
        first_word = desc.split()[0] if desc.split() else "complaint"
        reason = f"Classified based on description mentioning '{first_word}'."
        
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
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                print(f"Error: Empty CSV or missing headers in {input_path}")
                return
                
            for row in reader:
                if not row or not row.get("complaint_id"):
                    continue
                
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Classification failed: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Failed to read input file {input_path}: {e}")
        return

    # Write output CSV
    try:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except Exception as e:
        print(f"Failed to write output file {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
