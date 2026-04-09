"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Severity & Priority
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    matched_sev = [kw for kw in severity_keywords if kw in desc]
    priority = "Urgent" if matched_sev else "Standard"

    # Category Mapping
    categories_map = {
        "Pothole": ["pothole", "potholes"],
        "Flooding": ["flood", "floods", "flooded", "waterlog", "waterlogged", "inundated"],
        "Streetlight": ["streetlight", "light", "dark", "streetlamp", "lamp"],
        "Waste": ["waste", "garbage", "trash", "debris", "litter", "effluent"],
        "Noise": ["noise", "loud", "drilling", "sound", "volume", "engine", "engines"],
        "Road Damage": ["collapse", "collapsed", "crater"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat", "sun", "temperature", "burn"],
        "Drain Blockage": ["drain blocked", "blocked", "clog", "drain", "drainage"]
    }

    matched_categories = []
    reason_word = None
    
    # Strict whole-word categories check
    for cat, kws in categories_map.items():
        for kw in kws:
            if re.search(r'\b' + re.escape(kw) + r'\b', desc):
                matched_categories.append(cat)
                if not reason_word:
                    reason_word = kw
                break
                
    if not desc.strip() or len(matched_categories) == 0:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": priority,
            "reason": "The description lacks any clear context or recognized categories.",
            "flag": "NEEDS_REVIEW"
        }
    
    # Enforcement: Category name must be one of the allowed strings
    category = matched_categories[0]
    
    if len(matched_categories) == 1:
        flag = ""
        # Reason: Must be one sentence citing specific words
        reason = f"The description identifies the issue through the term '{reason_word}'."
    else:
        # Ambiguity rule: Set NEEDS_REVIEW for genuinely ambiguous/multiple matches
        flag = "NEEDS_REVIEW"
        reason = f"The description is flagged for review as it mentions multiple categories including '{reason_word}'."

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
    try:
        with open(input_path, mode="r", encoding="utf-8") as in_f:
            reader = csv.DictReader(in_f)
            f_names = reader.fieldnames
            safe_fieldnames = f_names if f_names is not None else []
            rows = list(reader)
    except Exception as e:
        print(f"Error reading input CSV: {e}")
        return

    out_fieldnames = [str(f) for f in safe_fieldnames] + ["category", "priority", "reason", "flag"]
    results = []
    
    for row in rows:
        try:
            classification = classify_complaint(row)
            out_row = {**row}
            # Add new fields
            out_row["category"] = classification.get("category", "Other")
            out_row["priority"] = classification.get("priority", "Standard")
            out_row["reason"] = classification.get("reason", "")
            out_row["flag"] = classification.get("flag", "")
            results.append(out_row)
        except Exception as e:
            print(f"Error processing row {row.get('complaint_id', 'UNKNOWN')}: {e}")
            out_row = {**row, "category": "Other", "priority": "Standard", "reason": f"Processing error: {e}", "flag": "NEEDS_REVIEW"}
            results.append(out_row)
            
    try:
        with open(output_path, mode="w", encoding="utf-8", newline='') as out_f:
            writer = csv.DictWriter(out_f, fieldnames=out_fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output CSV: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
