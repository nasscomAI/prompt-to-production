import argparse
import csv
import os

CATEGORIES = {
    "Pothole": ["pothole", "crater", "hole in road", "pit"],
    "Flooding": ["flood", "waterlog", "submerged", "standing water"],
    "Streetlight": ["streetlight", "street light", "lamp", "darkness", "light out", "light"],
    "Waste": ["garbage", "trash", "waste", "dump", "litter", "debris", "bin"],
    "Noise": ["noise", "loudspeaker", "music", "sound", "blaring"],
    "Road Damage": ["road damage", "pavement", "asphalt", "broken road", "cracks"],
    "Heritage Damage": ["heritage", "monument", "fort", "historical"],
    "Heat Hazard": ["heat", "heatwave", "temperature", "sunstroke"],
    "Drain Blockage": ["drain", "gutter", "sewage", "overflow", "blocked drain"]
}

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "elderly", "senior",
    "collapse", "trap", "immediate", "death", "emergency", "hazard to life"
]

def classify_row(complaint_id, description):
    desc_lower = description.lower()
    
    # 1. Category Classification
    matched_categories = []
    for cat, keywords in CATEGORIES.items():
        if any(kw in desc_lower for kw in keywords):
            matched_categories.append(cat)
            
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = "NONE"
    elif len(matched_categories) > 1:
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NONE"
        
    # 2. Priority Classification
    if any(kw in desc_lower for kw in URGENT_KEYWORDS):
        priority = "Urgent"
    else:
        priority = "Standard"
        
    # 3. Quoted Reason
    words = description.split()
    snippet = " ".join(words[:min(5, len(words))])
    reason = f'Issue reports "{snippet}" requiring attention.'
    
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_file, output_file):
    results = []
    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            c_id = row.get("complaint_id") or row.get("id") or row.get("ID") or "UNKNOWN"
            desc = row.get("description") or row.get("text") or row.get("complaint_text") or ""
            results.append(classify_row(c_id, desc))
            
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Successfully processed {len(results)} rows -> {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)