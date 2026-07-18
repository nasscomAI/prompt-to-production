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
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").strip()
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing complaint description.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    
    # Priority classification
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Standard"
    matched_severity = None
    for kw in severity_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            matched_severity = kw
            break
            
    # Category detection
    matched_categories = []
    if "pothole" in desc_lower:
        matched_categories.append("Pothole")
    if "flood" in desc_lower or "rainwater" in desc_lower or "waterlogged" in desc_lower:
        matched_categories.append("Flooding")
    if "streetlight" in desc_lower or "light out" in desc_lower or "sparking" in desc_lower or "dark at night" in desc_lower:
        matched_categories.append("Streetlight")
    if "garbage" in desc_lower or "waste" in desc_lower or "litter" in desc_lower:
        matched_categories.append("Waste")
    if "drilling" in desc_lower or "music" in desc_lower or "noise" in desc_lower or "idling" in desc_lower:
        matched_categories.append("Noise")
    if "road collapsed" in desc_lower or "crater" in desc_lower or "sinking" in desc_lower or "cracked" in desc_lower:
        matched_categories.append("Road Damage")
    if "heritage" in desc_lower:
        matched_categories.append("Heritage Damage")
    if "heat" in desc_lower or "sunstroke" in desc_lower or "temperature" in desc_lower:
        matched_categories.append("Heat Hazard")
    if "drain" in desc_lower:
        matched_categories.append("Drain Blockage")

    # Handle results
    flag = ""
    category = "Other"
    
    # Check for ambiguity conditions or manual rules
    is_ambiguous = len(matched_categories) > 1 or "idling" in desc_lower or "channel rainwater" in desc_lower or "mosquito" in desc_lower
    
    if matched_categories:
        # Default to first matched category
        category = matched_categories[0]
    else:
        category = "Other"
        
    if is_ambiguous:
        flag = "NEEDS_REVIEW"
        
    # Standardised reason creation: cite specific words
    citations = []
    for term in ["pothole", "flood", "rainwater", "drain", "garbage", "waste", "drilling", "idling", "road collapsed", "crater", "streetlight", "light", "heritage"]:
        if term in desc_lower:
            citations.append(f"'{term}'")
            
    if priority == "Urgent" and matched_severity:
        citations.append(f"severity keyword '{matched_severity}'")
                
    if citations:
        citation_str = ", ".join(citations)
        reason = f"Classified as {category} with priority {priority} based on {citation_str} in the description."
    else:
        reason = f"Classified as {category} based on general context in the description."
        
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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    cleaned_row = {k.strip(): (v.strip() if v else "") for k, v in row.items() if k}
                    res = classify_complaint(cleaned_row)
                    results.append(res)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Failed to process row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Error opening or reading input file: {e}")
        return

    # Write output CSV
    try:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except Exception as e:
        print(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
