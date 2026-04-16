import argparse
import csv

def classify_complaint(row: dict) -> dict:
    desc = row.get("description", "").lower()
    
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    matched_urgent = [kw for kw in urgent_keywords if kw in desc]
    priority = "Urgent" if matched_urgent else "Standard"
    
    categories = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "drain": "Drain Blockage",
        "light": "Streetlight",
        "garbage": "Waste",
        "waste": "Waste",
        "animal": "Waste",
        "music": "Noise",
        "noise": "Noise",
        "crack": "Road Damage",
        "tile": "Road Damage",
        "manhole": "Other"
    }
    
    category = "Other"
    flag = "NEEDS_REVIEW"
    matched_cat_word = None
    
    for kw, cat in categories.items():
        if kw in desc:
            category = cat
            flag = "NEEDS_REVIEW" if cat == "Other" else ""
            matched_cat_word = kw
            break
            
    if matched_cat_word:
        reason = f"Description contains the word '{matched_cat_word}'."
    else:
        reason = "Description requires human review for classification."
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    if matched_urgent:
        reason += f" Priority set to Urgent due to keyword '{matched_urgent[0]}'."
    
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    results = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(classify_complaint(row))
            
    if results:
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
