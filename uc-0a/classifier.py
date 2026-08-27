"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").strip()
    if not desc:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Low",
            "reason": "The description provided was entirely empty.",
            "flag": "ERROR"
        }
    
    desc_lower = desc.lower()
    
    # 1. Determine Category and a cited word for reason
    category = "Other"
    cited_word = "complaint"
    
    if "pothole" in desc_lower:
        category, cited_word = "Pothole", "pothole"
    elif "flood" in desc_lower:
        category, cited_word = "Flooding", "flood"
    elif "water" in desc_lower:
        category, cited_word = "Flooding", "water"
    elif "light" in desc_lower:
        category, cited_word = "Streetlight", "light"
    elif "waste" in desc_lower:
        category, cited_word = "Waste", "waste"
    elif "garbage" in desc_lower:
        category, cited_word = "Waste", "garbage"
    elif "noise" in desc_lower or "music" in desc_lower:
        category, cited_word = "Noise", "music" if "music" in desc_lower else "noise"
    elif "road" in desc_lower and "damage" in desc_lower:
        category, cited_word = "Road Damage", "road damage"
    elif "heritage" in desc_lower:
        category, cited_word = "Heritage Damage", "heritage"
    elif "heat" in desc_lower:
        category, cited_word = "Heat Hazard", "heat"
    elif "manhole" in desc_lower or "drain" in desc_lower:
        category, cited_word = "Drain Blockage", "manhole" if "manhole" in desc_lower else "drain"
    elif "broken" in desc_lower or "crack" in desc_lower:
        category, cited_word = "Road Damage", "crack" if "crack" in desc_lower else "broken"
        
    # 2. Determine Priority & Reason
    priority = "Standard"
    found_keywords = []

    for keyword in URGENT_KEYWORDS:
        if keyword in desc_lower:
            found_keywords.append(keyword)

    if found_keywords:
        priority = "Urgent"
        reason = f"Priority escalated to Urgent due to finding '{found_keywords[0]}', classified as {category} based on '{cited_word}'."
    else:
        reason = f"Assigned Standard priority and categorized as {category} because of the word '{cited_word}'."

    # 3. Determine Flag
    flag = "NEEDS_REVIEW" if category == "Other" else ""

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
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id', 'UNKNOWN')}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "",
                        "priority": "",
                        "reason": "",
                        "flag": "ERROR"
                    })
    except FileNotFoundError:
        print(f"Input file not found: {input_path}")
        sys.exit(1)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except IOError as e:
        print(f"Error writing to output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
