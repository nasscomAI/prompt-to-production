import argparse
import csv
import os

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules in agents.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").strip()
    
    result = {
        "complaint_id": row.get("complaint_id", ""),
        "category": "Other",
        "priority": "Standard",
        "reason": "",
        "flag": ""
    }
    
    if not desc:
        result["category"] = "Other"
        result["flag"] = "NEEDS_REVIEW"
        result["reason"] = "Description is missing."
        return result
        
    desc_lower = desc.lower()
    
    # Priority
    urgent_word = None
    for word in SEVERITY_KEYWORDS:
        if word in desc_lower:
            urgent_word = word
            result["priority"] = "Urgent"
            break
            
    # Categories
    cat_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "water", "rain"],
        "Streetlight": ["streetlight", "light", "dark"],
        "Waste": ["garbage", "waste", "smell", "dump", "animal", "bin"],
        "Noise": ["noise", "music", "loud"],
        "Road Damage": ["road surface", "cracked", "sinking", "manhole"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain blocked", "blockage", "drain"]
    }
    
    found_category = "Other"
    reason_word = None
    
    for cat, keywords in cat_keywords.items():
        for kw in keywords:
            if kw in desc_lower:
                found_category = cat
                reason_word = kw
                break
        if found_category != "Other":
            break
            
    result["category"] = found_category
    
    if found_category == "Other":
        result["flag"] = "NEEDS_REVIEW"
        if not urgent_word:
            result["reason"] = "Ambiguous complaint missing specific category keywords."
            return result
            
    # Reason formulation
    if urgent_word and reason_word:
        result["reason"] = f"Classified as {found_category} because it mentions '{reason_word}', and Urgent because it mentions '{urgent_word}'."
    elif urgent_word:
        result["reason"] = f"Classified as Other but prioritized as Urgent because it mentions '{urgent_word}'."
    elif reason_word:
        result["reason"] = f"Classified as {found_category} because it mentions '{reason_word}'."
        
    return result

def batch_classify(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return
        
    results = []
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
                
    if not results:
        print("No rows processed.")
        return
        
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
