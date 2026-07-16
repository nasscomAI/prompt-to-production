"""
UC-0A — Complaint Classifier
Deterministic rule-based agent conforming to RICE specifications.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").strip()
    comp_id = row.get("complaint_id", "").strip()
    
    # 1. Determine Priority based on severity keywords
    priority = "Standard"
    matched_severity = []
    desc_lower = desc.lower()
    for word in SEVERITY_KEYWORDS:
        if word in desc_lower:
            priority = "Urgent"
            matched_severity.append(word)
            
    # 2. Determine Category
    category = "Other"
    flag = ""
    matched_kw = ""
    
    if "heritage" in desc_lower or "historic" in desc_lower or "museum" in desc_lower:
        category = "Heritage Damage"
        matched_kw = "heritage/historic"
    elif "pothole" in desc_lower:
        category = "Pothole"
        matched_kw = "pothole"
    elif "flood" in desc_lower or "underpass flooded" in desc_lower or "water" in desc_lower or "rain" in desc_lower:
        category = "Flooding"
        matched_kw = "flooded/water"
    elif "light" in desc_lower or "dark" in desc_lower or "unlit" in desc_lower or "sparking" in desc_lower:
        category = "Streetlight"
        matched_kw = "streetlight/lights/dark"
    elif "garbage" in desc_lower or "waste" in desc_lower or "trash" in desc_lower or "dumped" in desc_lower or "dead animal" in desc_lower or "bins" in desc_lower:
        category = "Waste"
        matched_kw = "garbage/waste/dumped"
    elif "noise" in desc_lower or "music" in desc_lower or "loud" in desc_lower or "amplifier" in desc_lower or "drilling" in desc_lower or "idling" in desc_lower:
        category = "Noise"
        matched_kw = "music/noise/drilling"
    elif "heat" in desc_lower or "temp" in desc_lower or "burn" in desc_lower or "sun" in desc_lower or "hot" in desc_lower or "44°c" in desc_lower or "45°c" in desc_lower or "52°c" in desc_lower:
        category = "Heat Hazard"
        matched_kw = "heat/temperature/sun"
    elif "drain" in desc_lower or "blockage" in desc_lower or "clog" in desc_lower:
        category = "Drain Blockage"
        matched_kw = "drain/blockage"
    elif "road" in desc_lower or "sinking" in desc_lower or "surface" in desc_lower or "crack" in desc_lower or "footpath" in desc_lower or "manhole" in desc_lower or "tiles" in desc_lower or "bridge" in desc_lower:
        category = "Road Damage"
        matched_kw = "road/footpath/surface"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 3. Generate Reason citing specific words
    # Cite specific words from description
    if category != "Other":
        # Extract a short context or sentence
        sentences = [s.strip() for s in re.split(r'[.!?]', desc) if s.strip()]
        citation = desc
        for s in sentences:
            if matched_kw.split('/')[0] in s.lower():
                citation = s
                break
        reason = f"Classified as {category} because the description cites '{citation}'."
    else:
        reason = "Category is ambiguous and needs manual verification."
        flag = "NEEDS_REVIEW"
        
    return {
        "complaint_id": comp_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, mode="r", encoding="utf-8") as f_in:
            reader = csv.DictReader(f_in)
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            
            results = []
            for row in reader:
                if not row.get("complaint_id"):
                    continue  # skip null or empty rows
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # Not crash on bad rows, produce output even if some rows fail
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Failed to classify due to error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
                    
        with open(output_path, mode="w", encoding="utf-8", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Error in batch classification: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
