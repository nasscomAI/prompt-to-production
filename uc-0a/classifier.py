"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to the rules defined in agents.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "")
    desc_lower = desc.lower()

    # 1. Determine Category
    category_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "water"],
        "Streetlight": ["streetlight", "lights out", "dark", "sparking"],
        "Waste": ["garbage", "waste", "dead animal", "dumped", "smell"],
        "Noise": ["music", "noise", "loud"],
        "Road Damage": ["road", "footpath", "broken", "cracked", "sinking", "surface"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["manhole", "drain"],
    }
    
    category = "Other"
    matched_cat_word = None
    
    # Priority handling: check for drain blockage explicitly before road damage
    for cat, keywords in category_map.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
                category = cat
                matched_cat_word = kw
                break
        if category != "Other":
            break

    # 2. Determine Priority
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    matched_sev_word = None
    for kw in severity_keywords:
        if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
            priority = "Urgent"
            matched_sev_word = kw
            break

    # 3. Flag and Reason Validation
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    
    reason_parts = []
    if matched_cat_word:
        reason_parts.append(f"Description mentions '{matched_cat_word}'.")
    else:
        reason_parts.append("The issue does not clearly match known categories.")
        
    if matched_sev_word:
        reason_parts.append(f"Priority escalated to Urgent due to keyword '{matched_sev_word}'.")
        
    reason = " ".join(reason_parts)

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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    try:
        with open(input_path, mode="r", encoding="utf-8") as f_in:
            reader = csv.DictReader(f_in)
            for row in reader:
                if not row.get("description"):
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Missing description.",
                        "flag": "NEEDS_REVIEW"
                    })
                    continue
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Classification error: {e}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        return

    with open(output_path, mode="w", encoding="utf-8", newline="") as f_out:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
