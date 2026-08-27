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
    description = row.get("description", "").lower()
    
    # Priority Keywords (Urgent if present)
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    triggered_urgent = [kw for kw in urgent_keywords if kw in description]
    if triggered_urgent:
        priority = "Urgent"
    
    # Category Keywords strictly mapped to allowed taxonomy
    categories_map = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "water log", "overflow", "water-log", "inundation"],
        "Streetlight": ["streetlight", "street light", "lamp", "pole", "darkness"],
        "Waste": ["garbage", "trash", "waste", "dumping", "litter", "refuse"],
        "Noise": ["noise", "loud", "sound", "speaker", "noise pollution"],
        "Road Damage": ["damage", "crack", "broken road", "resurfacing", "asphalt"],
        "Heritage Damage": ["heritage", "statue", "monument", "historic", "museum"],
        "Heat Hazard": ["heat", "hot", "sunstroke", "thermal"],
        "Drain Blockage": ["drain", "sewage", "gutter", "clog", "choke"]
    }
    
    category = "Other"
    flag = ""
    matches = []
    
    for cat, keywords in categories_map.items():
        if any(kw in description for kw in keywords):
            matches.append(cat)
    
    if len(matches) == 1:
        category = matches[0]
    elif len(matches) > 1:
        category = matches[0]
        flag = "NEEDS_REVIEW"
    else:
        if not description or len(description.split()) < 3:
            flag = "NEEDS_REVIEW"

    # Reason field: one sentence citing specific words
    found_keywords = list(set([kw for cat_kws in categories_map.values() for kw in cat_kws if kw in description] + triggered_urgent))
    if found_keywords:
        reason = f"This complaint was classified as {category} because it mentions {', '.join(found_keywords)}."
    elif category == "Other":
        reason = "No specific keywords were found, so it was categorized as Other."
    else:
        reason = f"Classification determined as {category}."

    return {
        "complaint_id": row.get("complaint_id", "Unknown"),
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
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not any(row.values()): # Skip empty rows
                    continue
                results.append(classify_complaint(row))
        
        if not results:
            print(f"No valid rows found in {input_path}")
            return

        headers = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(results)
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"Error during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
