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
    desc = row.get("description", "").lower()
    
    # Priority classification based on severity keywords
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_urgency = [kw for kw in severity_keywords if kw in desc]
    
    if found_urgency:
        priority = "Urgent"
    else:
        priority = "Standard"
        
    # Category identification heuristics
    cat_matches = []
    if "pothole" in desc:
        cat_matches.append("Pothole")
    if "flood" in desc or "rain" in desc:
        cat_matches.append("Flooding")
    if "streetlight" in desc or "light" in desc or "sparking" in desc:
        cat_matches.append("Streetlight")
    if "garbage" in desc or "waste" in desc or "smell" in desc or "animal" in desc or "bin" in desc:
        cat_matches.append("Waste")
    if "music" in desc or "noise" in desc:
        cat_matches.append("Noise")
    if "road" in desc or "crack" in desc or "sinking" in desc or "footpath" in desc or "broken" in desc or "manhole" in desc:
        if "pothole" not in desc:  # Special case to avoid conflicting with Pothole
            cat_matches.append("Road Damage")
    if "heritage" in desc:
        cat_matches.append("Heritage Damage")
    if "heat" in desc:
        cat_matches.append("Heat Hazard")
    if "drain" in desc or "blocked" in desc:
        cat_matches.append("Drain Blockage")

    # Handle ambiguity through flags
    flag = ""
    if len(cat_matches) > 1:
        category = cat_matches[0]
        flag = "NEEDS_REVIEW"
    elif len(cat_matches) == 1:
        category = cat_matches[0]
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Generate reason citing a specific word
    # All base keywords used for matching categories
    cat_keywords = [
        "pothole", "flood", "rain", "streetlight", "light", "sparking", 
        "garbage", "waste", "smell", "animal", "bin",
        "music", "noise", "road", "crack", "sinking", "footpath", "broken", "manhole",
        "heritage", "heat", "drain", "blocked"
    ]
    words = desc.replace('.', '').replace(',', '').split()
    
    if found_urgency:
        cited_word = found_urgency[0]
    elif len(cat_matches) > 0:
        # Find the specific keyword that triggered the category match
        cited_word = next((kw for kw in cat_keywords if kw in desc), words[0] if words else "unknown")
    else:
        cited_word = words[0] if words else "unknown"
        
    reason = f"This complaint was classified based on noting the specific keyword '{cited_word}' in the description."
    
    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
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
    fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
    
    with open(input_path, mode='r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        
        with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                try:
                    if not row.get('description'):
                        writer.writerow({
                            'complaint_id': row.get('complaint_id', 'UNKNOWN'),
                            'category': 'Other',
                            'priority': 'Low',
                            'reason': 'No description was provided.',
                            'flag': 'NEEDS_REVIEW'
                        })
                        continue
                        
                    result = classify_complaint(row)
                    writer.writerow(result)
                except Exception as e:
                    writer.writerow({
                        'complaint_id': row.get('complaint_id', 'ERROR'),
                        'category': 'Other',
                        'priority': 'Low',
                        'reason': f"Processing failed with error: {str(e)}.",
                        'flag': 'NEEDS_REVIEW'
                    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
