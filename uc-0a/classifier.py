import argparse
import csv
import os
import re
import sys

# Allowed taxonomy list
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Keywords triggering Urgent priority
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """Skill 1: Classify a single complaint row according to RICE enforcement rules."""
    complaint_id = row.get("complaint_id") or row.get("id") or "UNKNOWN"
    desc = row.get("description") or row.get("complaint_text") or row.get("text") or ""
    desc_clean = desc.strip()
    desc_lower = desc_clean.lower()
    
    if not desc_clean:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided in input record.",
            "flag": "NEEDS_REVIEW"
        }

    # Category matching rules
    category = "Other"
    category_reason = "Unspecified issue"
    matched_word = ""

    if re.search(r"\bpothole(s)?\b", desc_lower):
        category = "Pothole"
        matched_word = "pothole"
    elif re.search(r"\b(flood|flooding|waterlogging|submerged)\b", desc_lower):
        category = "Flooding"
        matched_word = "flooding"
    elif re.search(r"\b(streetlight|street light|lamp post|dark street)\b", desc_lower):
        category = "Streetlight"
        matched_word = "streetlight"
    elif re.search(r"\b(garbage|trash|waste|debris|dump)\b", desc_lower):
        category = "Waste"
        matched_word = "waste"
    elif re.search(r"\b(loud|noise|music|decibel|speaker)\b", desc_lower):
        category = "Noise"
        matched_word = "noise"
    elif re.search(r"\b(drain|sewage|gutter|clogged drain|drain blockage)\b", desc_lower):
        category = "Drain Blockage"
        matched_word = "drain"
    elif re.search(r"\b(heritage|monument|historic|statue)\b", desc_lower):
        category = "Heritage Damage"
        matched_word = "heritage"
    elif re.search(r"\b(heat|sunstroke|scorching|heatwave)\b", desc_lower):
        category = "Heat Hazard"
        matched_word = "heat"
    elif re.search(r"\b(road|asphalt|crack|pavement|crater|tarmac)\b", desc_lower):
        category = "Road Damage"
        matched_word = "road"
    else:
        category = "Other"

    # Priority determination
    matched_severity = [kw for kw in SEVERITY_KEYWORDS if re.search(r"\b" + kw + r"\b", desc_lower)]
    if matched_severity:
        priority = "Urgent"
        severity_reason = f"contains severity trigger '{matched_severity[0]}'"
    else:
        priority = "Standard"
        severity_reason = "standard operational priority"

    # Flag assignment
    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = f"Classified as Other due to ambiguous text; {severity_reason}."
    else:
        flag = ""
        reason = f"Citing '{matched_word}' for category {category}; assigned {priority} as it {severity_reason}."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """Skill 2: Read input CSV, classify each row safely, write results CSV."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            classified = classify_complaint(row)
            results.append(classified)

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")