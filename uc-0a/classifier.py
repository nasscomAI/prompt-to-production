"""
UC-0A — Complaint Classifier
Implementation based on agents.md and skills.md rules.
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_RULES = {
    "Pothole": ["pothole"],
    "Flooding": ["flood"],
    "Streetlight": ["streetlight", "lights out"],
    "Waste": ["garbage", "waste", "dead animal"],
    "Noise": ["music", "noise"],
    "Road Damage": ["road surface", "footpath tiles broken", "road surface cracked"],
    "Drain Blockage": ["drain blocked", "manhole"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Rule 2: Priority Urgent keywords
    priority = "Standard"
    urgent_matches = []
    for word in URGENT_KEYWORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', desc):
            priority = "Urgent"
            urgent_matches.append(word)
            
    # Expected Category
    matched_cats = []
    cat_evidence = []
    for cat, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if kw in desc:
                if cat not in matched_cats:
                    matched_cats.append(cat)
                    cat_evidence.append(kw)
    
    # Rule 5: Ambiguity -> Other + NEEDS_REVIEW
    if len(matched_cats) == 1:
        category = matched_cats[0]
        flag = ""
    else:
        # 0 or >1 matches
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Rule 4: Reason quoting specific words
    parts = []
    if cat_evidence:
        parts.append(f"mentions '{cat_evidence[0]}'")
    if urgent_matches:
        parts.append(f"contains severe keywords like '{urgent_matches[0]}'")
        
    if not parts:
        reason = "Could not determine category from vocabulary."
    else:
        reason = "The description " + " and ".join(parts) + "."
        
    # If NEEDS_REVIEW but we had urgent matches, we still need reasoning.
    if flag == "NEEDS_REVIEW" and not cat_evidence:
        reason = "No clear category keywords found. Requires manual review."
        
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
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        
    results = []
    for r in rows:
        try:
            res = classify_complaint(r)
            results.append(res)
        except Exception as e:
            # Must not crash on bad rows
            results.append({
                "complaint_id": r.get("complaint_id", ""),
                "category": "Other",
                "priority": "Low",
                "reason": f"Error during classification: {str(e)}",
                "flag": "NEEDS_REVIEW"
            })
            
    if results:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
