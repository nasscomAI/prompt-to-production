"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "")
    
    # 1. Determine priority
    priority = "Standard"
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_severe = sorted([kw for kw in severity_keywords if kw in desc])
    if found_severe:
        priority = "Urgent"
        
    # 2. Determine category
    category_map = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "waterlog": "Flooding",
        "streetlight": "Streetlight",
        "light": "Streetlight",
        "dark": "Streetlight",
        "waste": "Waste",
        "garbage": "Waste",
        "smell": "Waste",
        "noise": "Noise",
        "music": "Noise",
        "road": "Road Damage",
        "crack": "Road Damage",
        "heritage": "Heritage Damage",
        "monument": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage",
        "block": "Drain Blockage"
    }

    detected_cats = set()
    matched_kws = []
    for kw, cat in category_map.items():
        if kw in desc:
            detected_cats.add(cat)
            matched_kws.append(kw)
            
    # 3. Handle flags and ambiguity
    flag = ""
    if len(detected_cats) == 1:
        category = list(detected_cats)[0]
    elif len(detected_cats) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 4. Generate reason citing exactly one sentence and specific words
    if found_severe:
        reason = f"Priority is {priority} and category is {category} because the text cites '{found_severe[0]}'."
    elif len(detected_cats) == 1:
        reason = f"Category is exactly mapped to {category} due to the word '{matched_kws[0]}' in the text."
    elif len(detected_cats) > 1:
        reason = f"Category is Other because the text contains conflicting keywords like '{matched_kws[0]}' and '{matched_kws[1]}'."
    else:
        intro_words = " ".join(desc.split()[:3])
        reason = f"Category is Other because the text starting with '{intro_words}' lacks known category keywords."    

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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    
    try:
        with open(input_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Flag nulls or empty descriptions
                    if not row or not row.get("description") or str(row.get("description")).strip() == "":
                        results.append({
                            "complaint_id": row.get("complaint_id", "UNKNOWN"),
                            "category": "Other",
                            "priority": "Standard",
                            "reason": "The description is null or empty.",
                            "flag": "NEEDS_REVIEW"
                        })
                        continue
                        
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as e:
                    # Not crash on bad rows
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Processing failed due to row error.",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Failed to read input CSV: {e}")
        return

    # Write out results
    try:
        with open(output_path, mode="w", encoding="utf-8", newline="") as f:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except Exception as e:
        print(f"Failed to write output CSV: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
