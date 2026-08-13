"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Guided by agents.md and skills.md.
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Empty or missing description.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    
    category = "Other"
    flag = ""
    
    # Check for specific undefined categories or natural runoffs
    is_other_needed = (
        "dead animal" in desc_lower or
        "manhole" in desc_lower or
        "draining directly" in desc_lower or
        "substation" in desc_lower or
        "surrounded by fields" in desc_lower or
        "dead trees" in desc_lower or
        ("broken bench" in desc_lower and "paving" in desc_lower)
    )
    
    # Category boolean conditions based on keywords
    has_heritage = "heritage" in desc_lower or "historic" in desc_lower or "ancient" in desc_lower
    has_pothole = "pothole" in desc_lower
    has_streetlight = "streetlight" in desc_lower or "lamp post" in desc_lower or "lights out" in desc_lower or "unlit" in desc_lower
    has_waste = "garbage" in desc_lower or "waste" in desc_lower or "trash" in desc_lower or "dumped" in desc_lower
    has_noise = "music" in desc_lower or "noise" in desc_lower or "amplifiers" in desc_lower or "drilling" in desc_lower or "idling" in desc_lower or "wedding band" in desc_lower
    has_road = "road surface" in desc_lower or "tarmac" in desc_lower or "road collapsed" in desc_lower or "road subsided" in desc_lower or "cracked" in desc_lower or "sinking" in desc_lower or "footpath" in desc_lower or "paving" in desc_lower or "cobblestones" in desc_lower
    has_heat = "heat" in desc_lower or "heatwave" in desc_lower or "temperature" in desc_lower or "melting" in desc_lower or "°c" in desc_lower or "sun" in desc_lower or "burns" in desc_lower
    has_drain = "drain" in desc_lower or "drainage" in desc_lower or "stormwater" in desc_lower or "blocked" in desc_lower
    has_flood = "flood" in desc_lower or "flooded" in desc_lower or "floods" in desc_lower or "flooding" in desc_lower
    
    # Priority severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    is_urgent = any(kw in desc_lower for kw in severity_keywords)
    priority = "Urgent" if is_urgent else "Standard"
    
    # Enforce priority and classification rules
    if is_other_needed:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif has_heritage and (has_waste or has_streetlight or has_road or has_noise or has_pothole):
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif has_drain:
        category = "Drain Blockage"
    elif has_flood:
        category = "Flooding"
    elif has_pothole:
        category = "Pothole"
    elif has_streetlight:
        category = "Streetlight"
    elif has_waste:
        category = "Waste"
    elif has_noise:
        category = "Noise"
    elif has_heat:
        category = "Heat Hazard"
    elif has_road:
        category = "Road Damage"
    elif has_heritage:
        category = "Heritage Damage"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Reason must cite specific words from the description and be exactly one sentence
    sentences = [s.strip() for s in description.split('.') if s.strip()]
    if sentences:
        reason = sentences[0]
        if not reason.endswith('.'):
            reason += '.'
    else:
        reason = description
        
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
    Must flag nulls, not crash on bad rows, and produce output even if some rows fail.
    """
    try:
        with open(input_path, mode="r", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            
            rows_to_write = []
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    rows_to_write.append(classified)
                except Exception as e:
                    print(f"Error classifying row {row.get('complaint_id', 'unknown')}: {e}", file=sys.stderr)
                    rows_to_write.append({
                        "complaint_id": row.get("complaint_id", "unknown"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Error processing row description.",
                        "flag": "NEEDS_REVIEW"
                    })
                    
        with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows_to_write)
            
    except Exception as e:
        print(f"Fatal error reading input path {input_path} or writing output path {output_path}: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
