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
    
    # 1. Determine Category
    category_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood"],
        "Streetlight": ["streetlight", "lights out"],
        "Waste": ["garbage", "waste", "dead animal"],
        "Noise": ["music", "noise"],
        "Road Damage": ["crack", "broken", "road damage"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain", "manhole"]
    }
    
    matches = []
    for cat, kws in category_map.items():
        if any(kw in desc for kw in kws):
            matches.append(cat)
            
    flag = ""
    if "pothole" in desc:
        category = "Pothole"
    elif "drain" in desc or "manhole" in desc:
        category = "Drain Blockage"
    elif "flood" in desc:
        category = "Flooding"
    elif len(matches) == 1:
        category = matches[0]
    elif len(matches) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 2. Determine Priority
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    is_urgent = any(kw in desc for kw in severity_keywords)
    priority = "Urgent" if is_urgent else "Standard"

    # 3. Reason Extraction
    reason = ""
    # simplistic sentence split
    sentences = [s.strip() for s in row.get("description", "").split(".") if s.strip()]
    if is_urgent:
        for s in sentences:
            if any(kw in s.lower() for kw in severity_keywords):
                reason = f"Contains severity keyword: {s}."
                break
    else:
        for s in sentences:
            found = False
            for kws in category_map.values():
                if any(kw in s.lower() for kw in kws):
                    reason = f"Classified based on: {s}."
                    found = True
                    break
            if found: break
            
    if not reason and sentences:
        reason = sentences[0] + "."

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
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        if "category" not in fieldnames:
            fieldnames.extend(["category", "priority", "reason", "flag"])
            
        for row in reader:
            # Handle nulls
            if not row.get("description"):
                row["category"] = "Other"
                row["priority"] = "Low"
                row["reason"] = "No description provided."
                row["flag"] = "NEEDS_REVIEW"
                results.append(row)
                continue
                
            # Classify safely
            try:
                classification = classify_complaint(row)
                row["category"] = classification.get("category", "Other")
                row["priority"] = classification.get("priority", "Standard")
                row["reason"] = classification.get("reason", "")
                row["flag"] = classification.get("flag", "")
            except Exception as e:
                row["category"] = "Other"
                row["priority"] = "Standard"
                row["reason"] = f"Processing error: {str(e)}"
                row["flag"] = "NEEDS_REVIEW"
                
            results.append(row)

    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
