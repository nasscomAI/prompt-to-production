"""
UC-0A — Complaint Classifier
Implementation based on constraints defined in agents.md and skills.md
"""
import argparse
import csv
import re

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
}

def classify_complaint(row: dict) -> dict:
    """
    Classifies a single citizen complaint according to the schema.
    """
    desc = row.get("description", "").lower()
    
    category_matches = []
    if "pothole" in desc: category_matches.append(("Pothole", "pothole"))
    if "flood" in desc or "rain" in desc: category_matches.append(("Flooding", "flood or rain"))
    if "light" in desc or "dark" in desc: category_matches.append(("Streetlight", "light or dark"))
    if "garbage" in desc or "waste" in desc: category_matches.append(("Waste", "garbage or waste"))
    if "dead animal" in desc: category_matches.append(("Waste", "dead animal"))
    if "music" in desc or "noise" in desc: category_matches.append(("Noise", "music or noise"))
    if "crack" in desc or "sink" in desc or "manhole" in desc or "tiles" in desc or "road" in desc: 
        category_matches.append(("Road Damage", "road condition indicators"))
    if "heritage" in desc: category_matches.append(("Heritage Damage", "heritage"))
    if "heat" in desc: category_matches.append(("Heat Hazard", "heat"))
    if "drain" in desc or "block" in desc: category_matches.append(("Drain Blockage", "drain block"))

    category = "Other"
    flag = ""
    match_word = ""

    unique_cats = list({c for c, w in category_matches})
    if len(unique_cats) == 1:
        category = unique_cats[0]
        match_word = category_matches[0][1]
    elif len(unique_cats) > 1:
        # Ambiguous if multiple categories match
        flag = "NEEDS_REVIEW"
        category = "Other"
    else:
        # No clear category found
        flag = "NEEDS_REVIEW"
        category = "Other"
        
    priority = "Standard"
    found_keyword = None
    for kw in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', desc):
            priority = "Urgent"
            found_keyword = kw
            break
            
    reason_parts = []
    if found_keyword:
        reason_parts.append(f"severity keyword '{found_keyword}'")
    if match_word:
        reason_parts.append(f"category indicator '{match_word}'")
        
    if reason_parts:
        reason = f"Classified based on {' and '.join(reason_parts)} found in the description."
    else:
        reason = "Classified as Other due to lack of clear category or severity indicators."
        
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
    Continues processing even if a row fails.
    """
    results = []
    
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                
    if not results:
        print("No results to output.")
        return
        
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
