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

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

KEYWORD_TO_CAT = {
    "pothole": "Pothole",
    "flood": "Flooding",
    "water": "Flooding",
    "light": "Streetlight",
    "waste": "Waste",
    "garbage": "Waste",
    "trash": "Waste",
    "noise": "Noise",
    "loud": "Noise",
    "road damage": "Road Damage",
    "heritage": "Heritage Damage",
    "monument": "Heritage Damage",  
    "heat": "Heat Hazard",
    "drain": "Drain Blockage",
    "blockage": "Drain Blockage"
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules defined in the prompt.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", row.get("id", "UNKNOWN"))
    
    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "The description provided was entirely blank or missing.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = desc.lower()

    # 1. Category Classification
    found_categories = set()
    for kw, cat in KEYWORD_TO_CAT.items():
        if re.search(rf"\b{kw}\b", desc_lower):
            found_categories.add(cat)

    if "damage" in desc_lower and "road" in desc_lower:
        found_categories.add("Road Damage")
    elif "damage" in desc_lower and "heritage" in desc_lower:
        found_categories.add("Heritage Damage")

    flag = ""
    if len(found_categories) == 1:
        category = found_categories.pop()
    elif len(found_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 2. Priority Routing
    priority = "Standard"
    urgent_match = None
    for kw in URGENT_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            urgent_match = kw
            break

    # 3. Rationale Formulation
    words = desc.split()
    snippet = " ".join(words[:3]) + "..." if len(words) > 3 else desc
    clean_snippet = snippet.replace('"', '').replace("'", "")
    
    if priority == "Urgent":
        reason = f"The priority is Urgent because the complaint text explicitly mentions the word '{urgent_match}'."
    else:
        reason = f"The complaint is categorized as '{category}' and lacks urgent keywords, based on the text starting with '{clean_snippet}'."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must handle bad rows without crashing the sequence.
    """
    processed = []
    keys = ["complaint_id", "category", "priority", "reason", "flag"]
    
    try:
        with open(input_path, 'r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    result = classify_complaint(row)
                    processed.append(result)
                except Exception as e:
                    processed.append({
                        "complaint_id": row.get("complaint_id", row.get("id", "UNKNOWN")),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"System error processing this specific row: {e}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return

    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=keys)
            writer.writeheader()
            writer.writerows(processed)
    except Exception as e:
        print(f"Error writing {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Batch run processed successfully. Output: {args.output}")
