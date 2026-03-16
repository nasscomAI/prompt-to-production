"""
UC-0A — Complaint Classifier
"""
import argparse
import csv

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
    "Flooding": ["flood", "water logging", "waterlogged"],
    "Streetlight": ["streetlight", "light not working", "lamp"],
    "Waste": ["garbage", "trash", "waste"],
    "Noise": ["noise", "loud"],
    "Road Damage": ["road damage", "damaged road", "broken road"],
    "Heritage Damage": ["heritage", "monument"],
    "Heat Hazard": ["heat", "extreme heat"],
    "Drain Blockage": ["drain", "blocked drain"]
}

def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id") or row.get("id") or ""
    description = (row.get("description") or "").lower().strip()
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Empty description",
            "flag": "NEEDS_REVIEW"
        }
    
    matched_categories = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for word in keywords:
            if word in description:
                matched_categories.append(cat)
                break
    
    category = "Other"
    flag = ""
    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"
    
    priority = "Standard"
    for word in SEVERITY_KEYWORDS:
        if word in description:
            priority = "Urgent"
            break
    
    reason = f'Classified based on keywords in description: "{description}"'
    
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    results = []
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row processing failed: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
    
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")