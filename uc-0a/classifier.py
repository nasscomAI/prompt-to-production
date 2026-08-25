"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import re

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
    description = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "").strip()
    
    # Defaults
    category = "Other"
    priority = "Standard"
    flag = ""
    reason = ""
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Empty complaint description.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    
    # Priority classification: Urgent if severity keywords present
    urgent_found = [word for word in SEVERITY_KEYWORDS if word in desc_lower]
    if urgent_found:
        priority = "Urgent"
    else:
        priority = "Standard"
        
    # Category rules
    matched_categories = []
    
    # Check category triggers
    if "pothole" in desc_lower:
        matched_categories.append("Pothole")
    
    if "flood" in desc_lower or "waterlogging" in desc_lower or "water logging" in desc_lower:
        matched_categories.append("Flooding")
        
    if "streetlight" in desc_lower or "street light" in desc_lower or "lights out" in desc_lower or "unlit" in desc_lower:
        # If it is a heritage street, we handle it separately
        if "heritage" not in desc_lower:
            matched_categories.append("Streetlight")
            
    if "garbage" in desc_lower or "waste" in desc_lower or "trash" in desc_lower or "dumped" in desc_lower or "dead animal" in desc_lower:
        matched_categories.append("Waste")
        
    if "music" in desc_lower or "noise" in desc_lower or "loud" in desc_lower:
        matched_categories.append("Noise")
        
    if "road surface" in desc_lower or "cracked" in desc_lower or "sinking" in desc_lower or "footpath" in desc_lower or "tiles broken" in desc_lower or ("paving" in desc_lower and "broken" in desc_lower):
        matched_categories.append("Road Damage")
        
    if "heritage" in desc_lower:
        matched_categories.append("Heritage Damage")
        # If it also contains lights out/dark/unlit, add Streetlight to make it ambiguous
        if "light" in desc_lower or "unlit" in desc_lower or "dark" in desc_lower:
            matched_categories.append("Streetlight")
            
    if "heat" in desc_lower or "temperature" in desc_lower or "melting" in desc_lower or "hot" in desc_lower:
        matched_categories.append("Heat Hazard")
        
    if "drain" in desc_lower or "drainage" in desc_lower or "manhole" in desc_lower or "sewer" in desc_lower:
        matched_categories.append("Drain Blockage")
        
    # Deduplicate matched categories
    matched_categories = list(set(matched_categories))
    
    # Determine final category and flag
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Construct a single sentence reason
    if flag == "NEEDS_REVIEW":
        if len(matched_categories) > 1:
            cats_str = " and ".join(sorted(matched_categories))
            reason = f"The complaint is flagged for review because the description contains references to multiple categories ({cats_str}) causing ambiguity."
        else:
            reason = "The complaint is flagged for review because the category cannot be determined from the description alone."
    else:
        # Construct specific reasons citing words
        citations = []
        if category == "Pothole":
            citations.append("pothole")
        elif category == "Flooding":
            citations.append("flooding/flooded")
        elif category == "Streetlight":
            citations.append("streetlight/lights out")
        elif category == "Waste":
            citations.append("waste/garbage/dead animal")
        elif category == "Noise":
            citations.append("music/noise")
        elif category == "Road Damage":
            citations.append("road/footpath damage")
        elif category == "Heritage Damage":
            citations.append("heritage street")
        elif category == "Heat Hazard":
            citations.append("heat/melting temperatures")
        elif category == "Drain Blockage":
            citations.append("drain/manhole")
            
        cit_str = citations[0] if citations else "the details"
        if priority == "Urgent":
            urg_str = f"with Urgent priority due to the keyword '{urgent_found[0]}'"
        else:
            urg_str = "with Standard priority"
            
        reason = f"This complaint is classified under {category} {urg_str} based on the description citing '{cit_str}'."
        
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
        raise FileNotFoundError(f"Input file not found at {input_path}")
        
    results = []
    
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check for missing complaint_id or other fields
            if not row.get("complaint_id"):
                continue
            classified = classify_complaint(row)
            results.append(classified)
            
    # Write to output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
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
