"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the description text,
    determining its category, priority, reason, and review flag.
    
    Adheres strictly to the RICE rules defined in agents.md.
    """
    description = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Empty complaint description.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()

    # Severity keywords that must trigger Urgent
    severity_keywords = [
        "injury", "child", "school", "hospital", "ambulance", 
        "fire", "hazard", "fell", "collapse"
    ]
    
    # Priority determination
    is_urgent = False
    matched_severity_kw = []
    for kw in severity_keywords:
        # Check word boundaries or substring
        if kw in desc_lower:
            is_urgent = True
            matched_severity_kw.append(kw)

    priority = "Urgent" if is_urgent else "Standard"

    # Category determination and ambiguous flags
    category = "Other"
    flag = ""
    reason_cite = ""

    # Genuinely ambiguous cases first
    if "heritage" in desc_lower:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_cite = "heritage zone or street reference creates potential classification ambiguity"
    elif "drain" in desc_lower and ("flood" in desc_lower or "water" in desc_lower or "injury" in desc_lower or "manhole" in desc_lower):
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_cite = "drain blockage with flooding/hazard indicators is ambiguous"
    elif "manhole" in desc_lower:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_cite = "missing manhole cover represents a multi-category hazard"
    elif "animal" in desc_lower:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_cite = "dead animal removal is ambiguous between waste and health hazard"
    elif "surrounded by fields" in desc_lower:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_cite = "rainwater channelling is ambiguous between flooding and storm water layout"
    # Single-category keywords
    elif "pothole" in desc_lower:
        category = "Pothole"
        reason_cite = "pothole causing tyre damage or traffic safety risks"
    elif "streetlight" in desc_lower or "lights out" in desc_lower:
        category = "Streetlight"
        reason_cite = "streetlight outage causing darkness or safety concern"
    elif "garbage" in desc_lower or "waste" in desc_lower or "bins" in desc_lower or "dumped" in desc_lower:
        category = "Waste"
        reason_cite = "accumulation or dumping of garbage/waste"
    elif "noise" in desc_lower or "music" in desc_lower or "drilling" in desc_lower or "idling with engines" in desc_lower or "idling" in desc_lower:
        category = "Noise"
        reason_cite = "excessive or untimely noise disturbance"
        if not is_urgent:
            priority = "Low"  # Noise is low priority unless urgent keywords are present
    elif "cracked" in desc_lower or "sinking" in desc_lower or "collapsed" in desc_lower or "crater" in desc_lower or "footpath" in desc_lower:
        category = "Road Damage"
        reason_cite = "structural damage to roads or footpaths"
    elif "drain" in desc_lower or "drainage" in desc_lower:
        category = "Drain Blockage"
        reason_cite = "blocked or overflowing drainage systems"
    elif "flood" in desc_lower or "floods" in desc_lower or "flooding" in desc_lower:
        category = "Flooding"
        reason_cite = "water accumulation or flooding in public spaces"
    elif "heat" in desc_lower or "temperature" in desc_lower:
        category = "Heat Hazard"
        reason_cite = "hazardous heat levels reported"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_cite = "complaint description does not match standard categories"

    # Citation sentence structure (must cite specific words from description)
    # Finding the first sentence or substring containing keywords
    words = description.split()
    snippet = " ".join(words[:10]) + "..." if len(words) > 10 else description
    
    if is_urgent:
        reason = f"Classified as {category} with Urgent priority due to severity keyword '{matched_severity_kw[0]}' in text: '{snippet}'."
    else:
        reason = f"Classified as {category} based on description details: '{snippet}'."

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
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                # Flag nulls or bad rows, don't crash
                results.append({
                    "complaint_id": row.get("complaint_id", "ERROR"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Failed to classify due to error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

    # Write results CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    # Ensure directory of output path exists
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        
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
