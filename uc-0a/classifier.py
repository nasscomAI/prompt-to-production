import argparse
import csv
import sys
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "The description is missing, preventing accurate classification.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()
    
    # 1. Category Matching (Taxonomy)
    # Rules: Pothole · Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other
    category_keywords = {
        "Pothole": ["pothole", "pit"],
        "Flooding": ["flood", "water", "submerged", "flooded"],
        "Streetlight": ["streetlight", "light", "dark", "unlit"],
        "Waste": ["garbage", "waste", "smell", "dumped", "animal", "bin"],
        "Noise": ["noise", "music", "loud"],
        "Road Damage": ["road surface", "cracked", "sinking", "footpath", "tiles", "paving", "tarmac"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat", "hot", "temperature", "°c", "sun", "melting"],
        "Drain Blockage": ["drain", "sewage", "blocked"],
    }
    
    matched_categories = []
    for cat, keywords in category_keywords.items():
        if any(kw in desc_lower for kw in keywords):
            matched_categories.append(cat)
    
    # Selection logic
    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        category = matched_categories[0] # Pick first, but will flag later
    else:
        category = "Other"

    # 2. Priority Matching (Severity triggers)
    # Rules: Urgent if keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    is_urgent = any(kw in desc_lower for kw in urgent_keywords)
    priority = "Urgent" if is_urgent else "Standard"

    # 3. Reason Generation (One sentence citing description)
    # Find the evidence in the text
    evidence = []
    for kw in urgent_keywords:
        if kw in desc_lower:
            evidence.append(kw)
    
    # If no urgent keywords, find category keywords
    if not evidence and category != "Other":
        for kw in category_keywords[category]:
            if kw in desc_lower:
                evidence.append(kw)
    
    evidence_str = ", ".join(evidence) if evidence else "contextual cues"
    reason = f"Categorized as {category} with {priority} priority based on the mention of '{evidence_str}' in the complaint description."

    # 4. Flagging (NEEDS_REVIEW)
    flag = ""
    if category == "Other" or len(matched_categories) > 1:
        flag = "NEEDS_REVIEW"
    
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
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified_row = classify_complaint(row)
                    results.append(classified_row)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                    # Create a dummy failed row
                    results.append({
                        "complaint_id": row.get('complaint_id', 'ERROR'),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing failed: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })

        if not results:
            print("No data processed.")
            return

        keys = results[0].keys()
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Batch processing error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

