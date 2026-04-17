"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '').lower()
    
    # 1. Determine Category
    matched_categories = []
    if "pothole" in description:
        matched_categories.append("Pothole")
    if "flood" in description or "water" in description:
        matched_categories.append("Flooding")
    if "light" in description or "dark" in description or "sparking" in description:
        matched_categories.append("Streetlight")
    if "waste" in description or "garbage" in description or "animal" in description or "dumped" in description:
        matched_categories.append("Waste")
    if "music" in description or "noise" in description:
        matched_categories.append("Noise")
    if "crack" in description or "broken" in description or "sink" in description or "footpath" in description:
        matched_categories.append("Road Damage")
    if "heritage" in description:
        matched_categories.append("Heritage Damage")
    if "heat" in description:
        matched_categories.append("Heat Hazard")
    if "drain" in description or "manhole" in description:
        matched_categories.append("Drain Blockage")
    
    # Resolve Category and Flag
    flag = ""
    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 2. Determine Priority
    urgent_keywords_found = [kw for kw in SEVERITY_KEYWORDS if kw in description]
    
    if urgent_keywords_found:
        priority = "Urgent"
        cited_word = urgent_keywords_found[0]
        reason = f"Priority is Urgent because the description explicitly mentions '{cited_word}'."
    else:
        priority = "Standard"
        # Find a significant word from the description to cite if possible
        words = [w for w in row.get('description', '').split() if len(w) > 3]
        cited_word = words[0] if words else "none"
        reason = f"Classified as {category} based on terms like '{cited_word}' from the description."
        
    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    if not row.get('description') or row['description'].strip() == "":
                        results.append({
                            "complaint_id": row.get("complaint_id", "UNKNOWN"),
                            "category": "Other",
                            "priority": "Low",
                            "reason": "The description is missing or null.",
                            "flag": "NEEDS_REVIEW"
                        })
                        continue
                        
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Failed to process row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
