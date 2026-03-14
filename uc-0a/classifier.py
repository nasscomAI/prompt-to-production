"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

# Allowed categories
CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

# Severity keywords for Urgent priority
URGENT_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Simple rule-based classification heuristics for demonstration
    # In a real "prompt to production" LLM pipeline, this would call an LLM.
    # We will implement heuristic logic that mimics the LLM instructions.
    
    category = "Other"
    ambiguous = False
    matched_cats = []
    
    if "pothole" in desc or "cracked" in desc or "sinking" in desc:
        matched_cats.append("Road Damage" if "cracked" in desc else "Pothole")
    if "flood" in desc or "water" in desc:
        matched_cats.append("Flooding")
    if "light" in desc or "dark" in desc:
        matched_cats.append("Streetlight")
    if "garbage" in desc or "waste" in desc or "smell" in desc or "dead animal" in desc:
        matched_cats.append("Waste")
    if "music" in desc or "noise" in desc:
        matched_cats.append("Noise")
    if "drain" in desc or "manhole" in desc:
        matched_cats.append("Drain Blockage")
    
    if len(matched_cats) == 1:
        category = matched_cats[0]
    elif len(matched_cats) > 1:
        # Ambiguous if multiple categories match
        category = "Other"
        ambiguous = True
        
    # Check priority
    priority = "Standard"
    for keyword in URGENT_KEYWORDS:
        if keyword in desc:
            priority = "Urgent"
            break
            
    # Set flag
    flag = "NEEDS_REVIEW" if ambiguous or category == "Other" else ""
    
    # Generate reason citing words
    words = desc.split()
    cite_word = words[0] if words else "unknown"
    
    # Try to grab the exact keyword that triggered the category
    extracted_kws = ["pothole", "flood", "light", "dark", "garbage", "waste", "smell", "dead", "music", "noise", "drain", "manhole", "cracked", "sinking", "water"]
    for kw in extracted_kws:
        if kw in desc:
            cite_word = kw
            break
            
    reason = f"The description mentions '{cite_word}'."
    
    if priority == "Urgent":
        urgent_kws = [k for k in URGENT_KEYWORDS if k in desc]
        if urgent_kws:
            reason = f"The description mentions '{urgent_kws[0]}' making it urgent."

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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    
    print(f"Reading from {input_path}...")
    try:
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id', 'UNKNOWN')}: {e}")
                    # append a blank/failed record to keep going
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing failed: {e}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Failed to read input file: {e}")
        return

    print(f"Writing to {output_path}...")
    try:
        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except Exception as e:
        print(f"Failed to write output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Processed results written to {args.output}")
