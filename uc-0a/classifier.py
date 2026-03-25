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
    complaint_id = row.get("complaint_id", "Unknown")
    
    # Categories mapping
    category_map = {
        "Pothole": ["pothole", "pit", "hole"],
        "Flooding": ["flood", "waterlogging", "water logging", "stagnant water"],
        "Streetlight": [" streetlight", "light", "lamp", "darkness"],
        "Waste": ["garbage", "trash", "waste", "dump", "litter"],
        "Noise": ["noise", "loud", "sound", "music", "construction sound"],
        "Road Damage": ["crack", "broken road", "asphalt", "sidewalk damage"],
        "Heritage Damage": ["heritage", "monument", "statue", "temple", "historic"],
        "Heat Hazard": ["heat", "hot", "shade", "sun", "temperature"],
        "Drain Blockage": ["drain", "sewer", "gutter", "blockage", "clogged"],
    }
    
    # Priority Keywords
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    selected_category = "Other"
    found_keywords = []

    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw in description:
                selected_category = cat
                found_keywords.append(kw)
                break
        if selected_category != "Other":
            break

    # Priority determination
    priority = "Standard"
    for ukw in urgent_keywords:
        if ukw in description:
            priority = "Urgent"
            break
    
    # If not urgent, but has no specific category keywords, maybe it's Low?
    if priority != "Urgent" and selected_category == "Other":
        priority = "Low"

    # Flag and Refusal
    flag = ""
    if selected_category == "Other" or not description.strip():
        selected_category = "Other"
        flag = "NEEDS_REVIEW"

    # Reason generation
    if selected_category != "Other":
        kw_evidence = found_keywords[0] if found_keywords else selected_category.lower()
        reason = f"The complaint mentions '{kw_evidence}', which justifies the {selected_category} classification."
    else:
        reason = "The description is too vague or does not match a specific category."

    return {
        "complaint_id": complaint_id,
        "category": selected_category,
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
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                if not any(row.values()): # Skip empty rows
                    continue
                results.append(classify_complaint(row))
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return

    if not results:
        print("No data processed.")
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
