import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()

    # 1. Determine Priority
    priority = "Standard"
    urgent_kw_found = None
    for kw in SEVERITY_KEYWORDS:
        if kw in desc:
            priority = "Urgent"
            urgent_kw_found = kw
            break

    # 2. Determine Category
    category = "Other"
    reason_kw = ""

    # Keyword heuristics for categorization
    if "pothole" in desc:
        category = "Pothole"
        reason_kw = "pothole"
    elif "flood" in desc or "waterlogging" in desc:
        category = "Flooding"
        reason_kw = "flood"
    elif "streetlight" in desc or "unlit" in desc or "dark" in desc:
        category = "Streetlight"
        reason_kw = "unlit/dark"
    elif "waste" in desc or "garbage" in desc or "bin" in desc or "dump" in desc:
        category = "Waste"
        reason_kw = "waste/bin"
    elif "noise" in desc or "loud" in desc or "music" in desc or "speaker" in desc:
        category = "Noise"
        reason_kw = "noise/music"
    elif "heritage" in desc or "ancient" in desc or "monument" in desc:
        category = "Heritage Damage"
        reason_kw = "heritage/ancient"
    elif "heat" in desc or "temperature" in desc or "melting" in desc or "sun" in desc or "burn" in desc:
        category = "Heat Hazard"
        reason_kw = "heat/melting/sun"
    elif "drain" in desc or "blockage" in desc or "clog" in desc:
        category = "Drain Blockage"
        reason_kw = "drain/blockage"
    elif "road" in desc and "crack" in desc:
        category = "Road Damage"
        reason_kw = "road/crack"

    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = "Could not map to explicit category."
    else:
        flag = ""
        reason = f"Mentioned '{reason_kw}' in description."

    if urgent_kw_found:
        reason += f" Escalated to Urgent due to '{urgent_kw_found}'."

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
    results = []
    fieldnames = []

    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames or [])
            # Add new columns if not present
            for col in ['category', 'priority', 'reason', 'flag']:
                if col not in fieldnames:
                    fieldnames.append(col)

            for row in reader:
                try:
                    classification = classify_complaint(row)
                    row['category'] = classification['category']
                    row['priority'] = classification['priority']
                    row['reason'] = classification['reason']
                    row['flag'] = classification['flag']
                except Exception as e:
                    row['category'] = "Other"
                    row['priority'] = "Low"
                    row['reason'] = f"Error during classification: {str(e)}"
                    row['flag'] = "NEEDS_REVIEW"
                results.append(row)

    except Exception as e:
        print(f"Failed to read input file: {e}")
        return

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Failed to write output file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
