import csv
import sys
import os
import argparse
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "waterlogging", "water logged"],
    "Streetlight": ["streetlight", "lights out", "dark at night", "sparking"],
    "Waste": ["garbage", "waste", "dump", "dead animal"],
    "Noise": ["music", "noise", "loud"],
    "Road Damage": ["road surface", "broken road", "footpath tiles broken", "road damage"],
    "Heritage Damage": ["heritage", "monument"],
    "Heat Hazard": ["heat", "sun", "hot"],
    "Drain Blockage": ["drain blocked", "clogged drain", "overflowing drain"],
}

def classify_complaint(row: dict) -> dict:
    description = row.get("description", "")
    desc_lower = description.lower()

    # Determine Priority (Severity Blindness enforcement)
    is_urgent = False
    urgent_trigger_word = ""
    for kw in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
            is_urgent = True
            urgent_trigger_word = kw
            break
            
    if is_urgent:
        priority = "Urgent"
    else:
        priority = "Standard" # Defaulting others to Standard

    # Determine Category
    matched_cats = []
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
                if cat not in matched_cats:
                    matched_cats.append(cat)
                    
    if len(matched_cats) == 1:
        category = matched_cats[0]
        flag = ""
    elif len(matched_cats) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Enforce allowed categories
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Reason handling: exact sentence citing description
    sentences = re.split(r'(?<=[.!?]) +|\n+', str(description).strip())
    reason_sentence = sentences[0] if sentences else description
    
    if is_urgent and urgent_trigger_word:
        for s in sentences:
            if re.search(r'\b' + re.escape(urgent_trigger_word) + r'\b', s.lower()):
                reason_sentence = s
                break
    else:
        if category in CATEGORY_KEYWORDS:
            for s in sentences:
                for kw in CATEGORY_KEYWORDS[category]:
                    if re.search(r'\b' + re.escape(kw) + r'\b', s.lower()):
                        reason_sentence = s
                        break
                if reason_sentence == s:
                    break

    reason = reason_sentence.strip()
    if reason and not re.search(r'[.!?]$', reason):
        reason += "."
        
    result = row.copy()
    result["category"] = category
    result["priority"] = priority
    result["reason"] = reason
    result["flag"] = flag
    
    return result

def batch_classify(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)
        
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise ValueError("CSV is empty or lacks headers.")
            rows = list(reader)
    except Exception as e:
        print(f"Error reading input CSV: {e}", file=sys.stderr)
        sys.exit(1)

    output_fieldnames = fieldnames + ["category", "priority", "reason", "flag"]
    output_fieldnames = list(dict.fromkeys(output_fieldnames))

    classified_rows = []
    for row in rows:
        try:
            res = classify_complaint(row)
            if res["category"] not in ALLOWED_CATEGORIES:
                raise ValueError(f"Taxonomy drift: Invalid category '{res['category']}'")
            if not res.get("reason"):
                raise ValueError("Missing justification: reason field is empty.")
            classified_rows.append(res)
        except Exception as e:
            print(f"Error processing row {row.get('complaint_id', '')}: {e}", file=sys.stderr)
            res = row.copy()
            res.update({
                "category": "Other", 
                "priority": "Standard", 
                "reason": f"System error: {str(e)}", 
                "flag": "NEEDS_REVIEW"
            })
            classified_rows.append(res)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=output_fieldnames)
            writer.writeheader()
            writer.writerows(classified_rows)
    except Exception as e:
        print(f"Error writing output CSV: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Classified {args.input} and wrote results to {args.output}")
