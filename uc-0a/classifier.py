"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage"
]

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

CAT_KEYWORDS = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flood", "waterlogging", "submerged", "overflow"],
    "Streetlight": ["streetlight", "dark", "no light", "lamp"],
    "Waste": ["waste", "trash", "garbage", "rubbish", "dump"],
    "Noise": ["noise", "loud", "music", "barking"],
    "Road Damage": ["damage", "crack", "broken"],
    "Heritage Damage": ["heritage", "monument", "statue"],
    "Heat Hazard": ["heat", "sun", "temperature"],
    "Drain Blockage": ["drain", "clogged", "sewer", "blockage"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    desc_lower = description.lower()
    
    # Priority classification
    priority = "Standard"
    found_sev_word = None
    for word in SEVERITY_KEYWORDS:
        if re.search(rf"\b{word}\b", desc_lower):
            priority = "Urgent"
            found_sev_word = word
            break
            
    # Category classification
    matched_cats = {}
    for cat, kws in CAT_KEYWORDS.items():
        for kw in kws:
            if re.search(rf"\b{kw}\b", desc_lower):
                matched_cats[cat] = kw
                break
                
    category = "Other"
    flag = ""
    reason = "No specific keyword matched."

    if len(matched_cats) == 1:
        category = list(matched_cats.keys())[0]
        match_kw = matched_cats[category]
        if found_sev_word:
            reason = f"Description mentions '{match_kw}' indicating {category} and '{found_sev_word}' indicating Urgent priority."
        else:
            reason = f"Description mentions '{match_kw}' indicating {category}."
    elif len(matched_cats) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous description containing multiple keywords across categories: {', '.join(matched_cats.keys())}."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        if found_sev_word:
             reason = f"Unable to determine category, but mentions '{found_sev_word}' indicating Urgent priority."

    # Build result
    result = dict(row)
    result["category"] = category
    result["priority"] = priority
    result["reason"] = reason
    result["flag"] = flag
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            fieldnames = list(reader.fieldnames) if reader.fieldnames else []
            if not fieldnames:
                print("Empty input CSV.")
                return
            
            for field in ["category", "priority", "reason", "flag"]:
                if field not in fieldnames:
                    fieldnames.append(field)
                    
            rows = []
            for row in reader:
                try:
                    classified_row = classify_complaint(row)
                    rows.append(classified_row)
                except Exception as e:
                    # Do not crash on bad rows
                    row["flag"] = "ERROR"
                    row["reason"] = str(e)
                    if "category" not in row: row["category"] = "Other"
                    if "priority" not in row: row["priority"] = "Standard"
                    rows.append(row)
                    
        with open(output_path, 'w', encoding='utf-8', newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"Error processing batch: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
