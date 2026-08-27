"""
UC-0A — Complaint Classifier
Implementation based on RICE (agents.md) and skills definitions (skills.md).
"""
import argparse
import csv
import os

# --- Enforcement Rules from agents.md ---
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

# Simple rule-based mapping for classification (as an initial "tool" logic)
CATEGORY_MAPPING = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "rain", "waterlogged", "underpass flooding", "knee-deep", "draining"],
    "Streetlight": ["streetlight", "lights out", "dark at night", "flickering", "darkness", "tripped", "unlit"],
    "Waste": ["garbage", "bins", "dumped", "waste", "dead animal", "market area", "piles", "filth"],
    "Noise": ["noise", "music", "loud", "midnight", "11pm", "wedding", "band", "amplifier", "2am"],
    "Road Damage": ["cracked", "sinking", "manhole", "footpath", "tiles", "road surface", "buckled", "subsided", "cobblestones", "paving", "broken bench"],
    "Heritage Damage": ["heritage", "historic", "monument", "ancient", "precinct"],
    "Heat Hazard": ["heat", "shade", "sun", "melting", "temperature", "burns", "44°c", "45°c", "52°c", "heatwave"],
    "Drain Blockage": ["drain", "sewage", "blockage", "sewer"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    desc_lower = description.lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # 1. Determine Category
    category = "Other"
    for cat, keywords in CATEGORY_MAPPING.items():
        if any(kw in desc_lower for kw in keywords):
            category = cat
            break
            
    # 2. Determine Priority
    priority = "Standard"
    triggered_keyword = None
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            triggered_keyword = kw
            break
            
    # 3. Construct Reason
    # Must be one sentence and cite specific words
    if category != "Other":
        # Find which keyword matched for justification
        source_kw = next((kw for kw in CATEGORY_MAPPING[category] if kw in desc_lower), "the context")
        reason = f"Classified as {category} based on description mentioning '{source_kw}'."
    else:
        reason = "Determined as Other because the description does not match any primary category keywords."

    if priority == "Urgent":
        reason = reason.rstrip(".") + f", with priority set to Urgent due to safety keyword '{triggered_keyword}'."

    # 4. Set Flag
    # Set when category is genuinely ambiguous or 'Other'
    flag = ""
    if category == "Other" or not description.strip():
        flag = "NEEDS_REVIEW"
        category = "Other"
        
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
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                # Basic null/missing description check
                if not row.get("description"):
                    results.append({
                        "complaint_id": row.get("complaint_id", "N/A"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Missing or empty description field.",
                        "flag": "NEEDS_REVIEW"
                    })
                    continue
                
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Failed to process row {row.get('complaint_id')}: {e}")
                    # Don't crash, append a failure placeholder
                    results.append({
                        "complaint_id": row.get("complaint_id", "N/A"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"System error during classification: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
