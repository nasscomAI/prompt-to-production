"""
UC-0A — Complaint Classifier
Rule-based classification script (No GenAI).
"""
import argparse
import csv
import sys
import re

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater", "craters", "potholes"],
    "Flooding": ["flood", "flooding", "waterlogging", "waterlog", "submerge", "submerged", "overflow"],
    "Streetlight": ["streetlight", "street light", "dark", "no light", "lamp", "bulb"],
    "Waste": ["waste", "garbage", "trash", "rubbish", "dump", "litter", "debris"],
    "Noise": ["noise", "loud", "music", "speaker", "sound", "party"],
    "Road Damage": ["road damage", "crack", "broken road", "surface", "rut"],
    "Heritage Damage": ["heritage", "monument", "statue", "ruin", "historic"],
    "Heat Hazard": ["heat hazard", "heat wave", "sun", "heatstroke"],
    "Drain Blockage": ["drain", "blockage", "sewer", "clog", "choke", "gutter"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using rule-based keyword matching.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    
    if not description or not description.strip():
         row["category"] = "Other"
         row["priority"] = "Standard"
         row["reason"] = "Empty description"
         row["flag"] = "NEEDS_REVIEW"
         return row
    
    desc_lower = description.lower()
    
    # Priority check
    priority = "Standard"
    reason_words = []
    
    for word in URGENT_KEYWORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', desc_lower):
            priority = "Urgent"
            reason_words.append(word)
    
    # Category check
    matched_categories = []
    category_reasons = []
    
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
                if cat not in matched_categories:
                    matched_categories.append(cat)
                category_reasons.append(kw)
    
    if len(matched_categories) == 1:
        row["category"] = matched_categories[0]
        row["flag"] = ""
        reason_words.extend(category_reasons)
        unique_reasons = sorted(set(reason_words))
        row["reason"] = f"Keywords detected: {', '.join(unique_reasons)}" if unique_reasons else "Category matched."
    else:
        # Ambiguous or no match
        row["category"] = "Other"
        row["flag"] = "NEEDS_REVIEW"
        if len(matched_categories) > 1:
            all_words = sorted(set(reason_words + category_reasons))
            row["reason"] = f"Ambiguous categories ({', '.join(matched_categories)}). Keywords: {', '.join(all_words)}"
        else:
            unique_reasons = sorted(set(reason_words))
            row["reason"] = f"Unable to determine category. Priority keywords: {', '.join(unique_reasons)}" if unique_reasons else "No identifying keywords found."
            
    row["priority"] = priority
    return row

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, mode="r", encoding="utf-8") as in_file:
            reader = csv.DictReader(in_file)
            rows = list(reader)
            fieldnames = list(reader.fieldnames) if reader.fieldnames else []
    except Exception as e:
        print(f"Failed to read input file {input_path}: {e}", file=sys.stderr)
        return

    if not rows:
        print("Input file is empty.", file=sys.stderr)
        return

    # Add the new fields if they don't exist in fieldnames
    for field in ["category", "priority", "reason", "flag"]:
        if field not in fieldnames:
            fieldnames.append(field)

    processed_rows = []
    total = len(rows)
    for i, row in enumerate(rows, 1):
        print(f"Processing row {i}/{total}...", end="\r")
        processed_row = classify_complaint(row)
        processed_rows.append(processed_row)
    print(f"\nCompleted {total} rows.")

    try:
        with open(output_path, mode="w", encoding="utf-8", newline="") as out_file:
            writer = csv.DictWriter(out_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_rows)
    except Exception as e:
        print(f"Failed to write output file {output_path}: {e}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
