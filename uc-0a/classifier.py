"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    """
    description = row.get("description", "")
    if not description:
        description = ""
    desc_lower = description.lower()
    
    # 1. Enforcement: Priority keywords -> Urgent
    urgent_keywords = ['injury', 'child', 'children', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    
    priority = "Standard"
    matched_urgent_kws = []
    for kw in urgent_keywords:
        if re.search(rf'\b{kw}\b', desc_lower):
            matched_urgent_kws.append(kw)
            priority = "Urgent"

    # 2. Enforcement: Categories allowed maps explicitly
    category_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "flooded", "floods"],
        "Streetlight": ["streetlight", "lights out", "dark"],
        "Waste": ["garbage", "waste", "dead animal", "smell", "dump"],
        "Noise": ["music", "noise", "loud"],
        "Road Damage": ["cracked", "broken", "sinking", "road surface"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat", "temperature"],
        "Drain Blockage": ["drain", "manhole"]
    }

    detected_categories = []
    matched_evidence = {}
    for cat, kws in category_map.items():
        for kw in kws:
            if re.search(rf'\b{kw}\b', desc_lower) or kw in desc_lower:
                if cat not in detected_categories:
                    detected_categories.append(cat)
                    matched_evidence[cat] = kw

    # 3. Enforcement: Genuninely ambiguous -> Other + NEEDS_REVIEW
    if len(detected_categories) == 0:
        return {
            "category": "Other",
            "priority": priority,
            "reason": "Classified as Other because the description lacks specific category keywords.",
            "flag": "NEEDS_REVIEW"
        }
    elif len(detected_categories) > 1:
        return {
            "category": "Other",
            "priority": priority,
            "reason": f"Classified as Other because the description is ambiguous, mentioning both {detected_categories[0]} and {detected_categories[1]}.",
            "flag": "NEEDS_REVIEW"
        }

    # Exactly one category determined
    category = detected_categories[0]
    evidence_word = matched_evidence[category]
    category_just = f"Issue involves '{evidence_word}'"
    
    priority_just = ""
    if priority == "Urgent":
        priority_just = f", triggering Urgent status due to '{matched_urgent_kws[0]}'"

    reason = f"Classified as {category} based on explicit description text: {category_just}{priority_just}."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": ""
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, apply classification, handle errors row-by-row, and write.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
            fieldnames = list(reader.fieldnames) if reader.fieldnames else []
    except Exception as e:
        print(f"Error reading input CSV: {e}")
        return

    for field in ['category', 'priority', 'reason', 'flag']:
        if field not in fieldnames:
            fieldnames.append(field)

    processed_rows = []
    for row in rows:
        out_row = row.copy()
        try:
            result = classify_complaint(out_row)
            out_row['category'] = result.get('category', 'Other')
            out_row['priority'] = result.get('priority', 'Standard')
            out_row['reason'] = result.get('reason', '')
            out_row['flag'] = result.get('flag', '')
        except Exception as e:
            print(f"Exception classifying row {out_row.get('complaint_id', '')}: {e}")
            out_row['category'] = 'Other'
            out_row['priority'] = 'Standard'
            out_row['reason'] = 'Failure processing row.'
            out_row['flag'] = 'NEEDS_REVIEW'

        processed_rows.append(out_row)

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_rows)
    except Exception as e:
        print(f"Error writing output CSV: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
