"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.

This script implements the rules explicitly defined in agents.md and skills.md.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage",
    "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

# Mapping of keywords to categories for classification
CATEGORY_RULES = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "rain", "stranded"],
    "Streetlight": ["streetlight", "dark", "sparking", "lights out"],
    "Waste": ["garbage", "waste", "dead animal", "dumped"],
    "Noise": ["music", "noise"],
    "Road Damage": ["cracked", "sinking", "manhole", "footpath", "broken", "upturned"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "sunstroke", "temperature"],
    "Drain Blockage": ["drain blocked", "overflowing"]
}

def classify_complaint(row: dict) -> dict:
    """
    Skill: classify_complaint
    Receives one complaint row, determines category, priority, reason, and flag.
    Strictly follows enforcement rules from agents.md.
    """
    desc = row.get("description", "")
    desc_lower = desc.lower()

    # Rule: Priority matching
    priority = "Standard"
    cited_priority_word = None
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            cited_priority_word = kw
            break

    # Rule: Category matching
    category = "Other"
    flag = "NEEDS_REVIEW"
    cited_category_word = None

    # Drain blockage has precedence over flooding if specific words appear
    if "drain block" in desc_lower or "drain blocked" in desc_lower:
        category = "Drain Blockage"
        flag = ""
        cited_category_word = "drain block"
    else:
        for cat, keywords in CATEGORY_RULES.items():
            for kw in keywords:
                if kw in desc_lower:
                    category = cat
                    flag = ""
                    cited_category_word = kw
                    break
            if category != "Other":
                break

    # Rule: Reason formatting citing specific words
    if category != "Other":
        reason_parts = [f"Classified as {category} because description explicitly states '{cited_category_word}'."]
    else:
        reason_parts = ["Classified as Other since no recognized category keywords were found."]

    if priority == "Urgent":
        reason_parts.append(f"Marked Urgent because the severe keyword '{cited_priority_word}' was detected.")
    else:
        reason_parts.append("Marked Standard as no severe keywords were present.")

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
    Skill: batch_classify
    Reads input CSV, applies classify_complaint per row, writes output CSV.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return

    results = []
    for row in rows:
        try:
            classified = classify_complaint(row)
            results.append(classified)
        except Exception:
            # Error handling rule: Fallback when parsing fails
            results.append({
                "complaint_id": row.get("complaint_id", "UNKNOWN"),
                "category": "Other",
                "priority": "Standard",
                "reason": "Processing failed due to internal error.",
                "flag": "NEEDS_REVIEW"
            })

    if results:
        try:
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
                writer.writeheader()
                writer.writerows(results)
            print(f"Done. Classified {len(results)} rows.")
        except Exception as e:
            print(f"Error writing to {output_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
