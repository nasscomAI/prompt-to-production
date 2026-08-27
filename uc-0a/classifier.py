"""
UC-0A — Complaint Classifier
Implementation based strictly on agents.md (RICE enforcement) and skills.md.
"""
import argparse
import csv
import os

# Context from agents.md: "You must only use the provided citizen complaint description text"
# Enforcement 2 from agents.md: Priority keywords
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

# Enforcement 1 from agents.md: Exact allowed categories
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "water"],
    "Streetlight": ["streetlight", "lights out", "dark", "sparking", "lights"],
    "Waste": ["garbage", "waste", "dead animal", "dumped"],
    "Noise": ["music", "noise", "loud"],
    "Road Damage": ["cracked", "sinking", "broken", "road surface", "footpath tiles"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat"],
    "Drain Blockage": ["drain blocked", "manhole", "drain"]
}

def classify_complaint(row: dict) -> dict:
    """
    Skill: classify_complaint
    Enforces RICE rules from agents.md on a single CSV row.
    Returns: dict with complaint_id, category, priority, reason, flag.
    """
    description = row.get("description", "").lower()
    
    # ---------------------------------------------------------
    # Priority Enforcement (agents.md rule 2)
    # ---------------------------------------------------------
    priority = "Standard"
    found_severity = []
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description:
            priority = "Urgent"
            found_severity.append(keyword)
            
    # ---------------------------------------------------------
    # Category Enforcement (agents.md rule 1)
    # ---------------------------------------------------------
    found_categories = []
    reason_words = []
    
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in description:
                if cat not in found_categories:
                    found_categories.append(cat)
                reason_words.append(kw)
                
    # ---------------------------------------------------------
    # Ambiguity / Fallback Enforcement (agents.md rule 4)
    # ---------------------------------------------------------
    if len(found_categories) == 1:
        category = found_categories[0]
        flag = ""
    else:
        # 0 or multiple matching categories
        category = "Other"
        flag = "NEEDS_REVIEW"
        if len(found_categories) == 0:
            reason_words.append("ambiguous description")
            
    # ---------------------------------------------------------
    # Reason Generation Enforcement (agents.md rule 3)
    # ---------------------------------------------------------
    all_matched_words = list(set(reason_words + found_severity))
    if not all_matched_words:
        reason_text = "no precise identifiers"
    else:
        reason_text = ", ".join(all_matched_words)
        
    reason = f"Category '{category}' and priority '{priority}' assigned because the description contains the specific words: '{reason_text}'."
    
    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Skill: batch_classify
    Reads input CSV, applies classify_complaint to each row, securely writes results CSV.
    Matches error_handling defined in skills.md.
    """
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return
        
    results = []
    with open(input_path, 'r', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        for row in reader:
            try:
                # Skill error_handling: Handle missing/undefined description
                if not row.get("description"):
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Description is missing from input row.",
                        "flag": "NEEDS_REVIEW"
                    })
                    continue
                    
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                # Skill error_handling: Skip failures gracefully without stalling batch
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Classify computation failed: {str(e)}.",
                    "flag": "NEEDS_REVIEW"
                })
                
    with open(output_path, 'w', encoding='utf-8', newline='') as f_out:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in results:
            writer.writerow(row)
            
    print(f"Successfully processed {len(results)} rows into {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
