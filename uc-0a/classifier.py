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
    desc = row.get("description", "").lower()
    
    category = "Other"
    priority = "Standard"
    reason = ""
    flag = ""
    
    # Check severity keywords to determine priority
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    found_severity = [kw for kw in severity_keywords if kw in desc]
    if found_severity:
        priority = "Urgent"

    # Identify category keywords based on allowed list
    matches = []
    if "pothole" in desc:
        matches.append(("Pothole", "pothole"))
    if "flood" in desc or "rain" in desc:
        matches.append(("Flooding", "flood/rain"))
    if "streetlight" in desc or "lights out" in desc or "dark" in desc:
        matches.append(("Streetlight", "streetlight/lights out/dark"))
    if "garbage" in desc or "waste" in desc or "smell" in desc or "dead animal" in desc:
        matches.append(("Waste", "garbage/waste/smell/dead animal"))
    if "music" in desc or "noise" in desc:
        matches.append(("Noise", "music/noise"))
    if "crack" in desc or "sink" in desc or "broken" in desc or "manhole" in desc or "tiles" in desc:
        matches.append(("Road Damage", "crack/sink/broken/manhole/tiles"))
    if "heritage" in desc:
        matches.append(("Heritage Damage", "heritage"))
    if "heat" in desc:
        matches.append(("Heat Hazard", "heat"))
    if "drain" in desc:
        matches.append(("Drain Blockage", "drain"))

    # De-duplicate matches
    unique_cats = list({m[0]: m[1] for m in matches}.items())
    
    # Resolve Category & Reason & Flags
    if len(unique_cats) == 1:
        category, matched_word = unique_cats[0]
        reason = f"Description contains explicit reference to '{matched_word}'."
    elif len(unique_cats) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous description containing multiple indicators: '{', '.join([c[1] for c in unique_cats])}'."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Unable to confidently determine category from text."
        
    if priority == "Urgent":
        reason += f" Priority escalated to Urgent due to severity keyword '{found_severity[0]}'."
    
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason.strip(),
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    
    # Read the data safely
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise ValueError("CSV is empty or lacks headers.")
                
            for row_idx, row in enumerate(reader, start=1):
                # Safeguard against malformed/null rows
                if not row or not row.get("description"):
                    row_out = {**row}
                    row_out.update({
                        "category": "Other", 
                        "priority": "Low", 
                        "reason": "Missing or null description.", 
                        "flag": "NEEDS_REVIEW"
                    })
                    results.append(row_out)
                    continue
                    
                # Process strictly without crashing the batch
                try:
                    classification = classify_complaint(row)
                    row_out = {**row}
                    # Update row to include results
                    for k in ["category", "priority", "reason", "flag"]:
                        row_out[k] = classification.get(k, "")
                    results.append(row_out)
                except Exception as e:
                    row_out = {**row}
                    row_out.update({
                        "category": "Other", 
                        "priority": "Low", 
                        "reason": f"System error processing row: {str(e)}", 
                        "flag": "NEEDS_REVIEW"
                    })
                    results.append(row_out)
                    
        # Verify columns & include the new classifications
        out_fields = list(fieldnames)
        for expected_field in ["category", "priority", "reason", "flag"]:
            if expected_field not in out_fields:
                out_fields.append(expected_field)
                
        # Write output systematically
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_fields)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Fatal error during batch processing: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
