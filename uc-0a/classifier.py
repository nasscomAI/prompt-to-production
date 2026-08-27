"""
UC-0A — Complaint Classifier
Implemented using RICE constraints from agents.md.
"""
import argparse
import csv
import re

CATEGORIES = {
    "Pothole": ["pothole", "potholes"],
    "Flooding": ["flood", "flooded", "flooding"],
    "Streetlight": ["streetlight", "lights out", "dark at night", "sparking", "light"],
    "Waste": ["garbage", "waste", "dead animal", "dumped"],
    "Noise": ["music", "noise", "loud"],
    "Road Damage": ["crack", "sinking", "manhole", "broken", "upturned"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "hot"],
    "Drain Blockage": ["drain blocked", "drainage"]
}

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on skills.md definition.
    Returns: dict with keys: category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Priority Enforcement
    urgent_keywords = [kw for kw in SEVERITY_KEYWORDS if kw in desc]
    priority = "Urgent" if urgent_keywords else "Standard"
    
    # Category Enforcement
    matched_cats = {}
    for cat, kws in CATEGORIES.items():
        for kw in kws:
            if re.search(r'\b' + re.escape(kw) + r'\b', desc) or kw in desc:
                if cat not in matched_cats:
                    matched_cats[cat] = kw

    flag = ""
    category = "Other"
    reason = "No relevant severity or category keywords found."

    if len(matched_cats) == 1:
        category = list(matched_cats.keys())[0]
        used_word = matched_cats[category]
        if urgent_keywords:
            reason = f"Classified exactly as {category} based on '{used_word}' and prioritized as Urgent due to '{urgent_keywords[0]}'."
        else:
            reason = f"Classified exactly as {category} based on the word '{used_word}' in the description."
    elif len(matched_cats) > 1:
        flag = "NEEDS_REVIEW"
        reason = f"Flagged for manual review due to ambiguous overlapping categories explicitly matching: {', '.join(matched_cats.keys())}."
    else:
        flag = "NEEDS_REVIEW"
        reason = "Flagged for manual review because issue cannot be cleanly determined from description alone."
        
    row["category"] = category
    row["priority"] = priority
    row["reason"] = reason
    row["flag"] = flag
    return row

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV using error handling 
    defined in skills.md.
    """
    results = []
    fieldnames = []
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames)
            for row in reader:
                try:
                    classified_row = classify_complaint(row)
                    results.append(classified_row)
                except Exception as e:
                    print(f"Skipping badly formatted row: {e}")
                    pass
    except Exception as e:
        print(f"Failed opening input CSV: {e}")
        return

    if not results:
        print("No valid rows matched to write out.")
        return

    # Add RICE structured columns
    for f in ["category", "priority", "reason", "flag"]:
        if f not in fieldnames:
            fieldnames.append(f)

    try:
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Failed to write output CSV: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
