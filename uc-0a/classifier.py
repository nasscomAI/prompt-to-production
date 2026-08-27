"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
}

CAT_KEYWORDS = {
    "Pothole": ["pothole", "crater", "hole"],
    "Flooding": ["flood", "waterlog", "water", "submerge", "overflow"],
    "Streetlight": ["streetlight", "dark", "light", "lighting", "lamp"],
    "Waste": ["waste", "trash", "garbage", "dump", "rubbish"],
    "Noise": ["noise", "loud", "music", "barking", "sound"],
    "Road Damage": ["crack", "road damage", "uneven", "broken road"],
    "Heritage Damage": ["heritage", "monument", "statue", "ruin", "historic"],
    "Heat Hazard": ["heat", "sun", "burn", "temperature"],
    "Drain Blockage": ["drain", "blockage", "clog", "sewage", "gutter"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    desc_lower = description.lower()
    
    # 1. Determine Category & Flag
    matched_cats = {}
    for cat, keywords in CAT_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
                if cat not in matched_cats:
                    matched_cats[cat] = []
                matched_cats[cat].append(kw)
    
    category = "Other"
    flag = ""
    reason_words = []
    
    if len(matched_cats) == 1:
        category = list(matched_cats.keys())[0]
        reason_words.extend(matched_cats[category])
    elif len(matched_cats) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_words = [kw for kws in matched_cats.values() for kw in kws]
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # 2. Determine Priority
    priority = "Standard"
    found_keywords = []
    for keyword in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword) + r'\b', desc_lower):
            priority = "Urgent"
            found_keywords.append(keyword)
            
    # 3. Determine Reason
    if not description:
        reason = "No description provided to extract reason from."
    else:
        cited_words = set(reason_words + found_keywords)
        if cited_words:
            words_str = ", ".join(f"'{w}'" for w in cited_words)
            reason = f"Classified based on the presence of words {words_str} in the description."
        else:
            reason = "No specific category or severity words were found in the description."
        
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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
            fieldnames = reader.fieldnames
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return
        
    final_fields = list(fieldnames) if fieldnames else []
    for f in ["category", "priority", "reason", "flag"]:
        if f not in final_fields:
            final_fields.append(f)
            
    results = []
    for row in rows:
        try:
            if not row.get("description"):
                row["category"] = "Other"
                row["priority"] = "Low"
                row["reason"] = "No description provided."
                row["flag"] = "NEEDS_REVIEW"
            else:
                classification = classify_complaint(row)
                row.update(classification)
        except Exception as e:
            row["category"] = "Other"
            row["priority"] = "Low"
            row["reason"] = f"Error during classification: {str(e)}"
            row["flag"] = "NEEDS_REVIEW"
            
        results.append(row)
        
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=final_fields)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to {output_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
