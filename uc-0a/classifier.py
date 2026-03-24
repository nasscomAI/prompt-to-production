"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", 
    "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = str(row.get('description', '')).lower()
    
    # 1. Category formulation
    cat_scores = {c: 0 for c in ALLOWED_CATEGORIES}
    
    if "pothole" in desc:
        cat_scores["Pothole"] += 2
    if "flood" in desc or "rain" in desc and "water" in desc:
        cat_scores["Flooding"] += 1.5
    if "streetlight" in desc or "dark" in desc or "light" in desc:
        cat_scores["Streetlight"] += 1.5
    if "garbage" in desc or "waste" in desc or "smell" in desc or "dead animal" in desc:
        cat_scores["Waste"] += 1.5
    if "noise" in desc or "music" in desc or "loud" in desc:
        cat_scores["Noise"] += 2
    if "crack" in desc or "manhole" in desc or "broken" in desc or "footpath" in desc:
        cat_scores["Road Damage"] += 1.2
    if "heritage" in desc:
        cat_scores["Heritage Damage"] += 1.5
    if "drain" in desc or ("water" in desc and "block" in desc):
        cat_scores["Drain Blockage"] += 1.5
    
    sorted_cats = sorted(cat_scores.items(), key=lambda x: x[1], reverse=True)
    best_cat, best_score = sorted_cats[0]
    second_cat, second_score = sorted_cats[1]
    
    if best_score == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif best_score > 0 and second_score > 0 and (best_score - second_score < 0.5):
        category = best_cat
        flag = "NEEDS_REVIEW"
    else:
        category = best_cat
        flag = ""
    
    # Specific edge case corrections
    if "drain blocked" in desc or "drain blockage" in desc:
        category = "Drain Blockage"
        flag = "NEEDS_REVIEW"
    if "dead animal" in desc:
        category = "Waste"
        flag = "NEEDS_REVIEW"
    if "heritage" in desc:
        category = "Heritage Damage"
        flag = ""
        
    # 2. Priority detection
    priority = "Standard"
    urgent_words = []
    for keyword in URGENT_KEYWORDS:
        if keyword in desc:
            priority = "Urgent"
            urgent_words.append(keyword)
            break
            
    # 3. Reason generation
    desc_orig = str(row.get('description', ''))
    words = desc_orig.split()
    snippet = " ".join(words[:4])
    reason = f"The complaint explicitly states '{snippet}'."
    if priority == "Urgent" and len(urgent_words) > 0:
        reason = f"The complaint explicitly cites '{urgent_words[0]}' which elevates severity."
        
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
    """
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return
        
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    results = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row or not any(row.values()):
                continue
            res = classify_complaint(row)
            results.append(res)
            
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
